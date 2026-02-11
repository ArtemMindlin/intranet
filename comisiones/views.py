from calendar import monthrange
from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

# Datos mockeados para mostrar en la plantilla. En un entorno real, estos datos se obtendrían de una consulta a SQL Server.
from .mock_data import INCIDENCIAS
from .models import Comision, Incidencia, Perfil, Venta


def _es_gerencia(user):
    return (
        user.is_superuser
        or user.groups.filter(name__in=["Gerente", "Director Comercial"]).exists()
    )


def _contexto_base_usuario(request, perfil):
    return {
        "usuario_nombre": request.user.get_full_name() or request.user.username,
        "usuario_login": request.user.username,
        "sede": perfil.sede,
        "foto_perfil_url": perfil.foto_perfil.url if perfil.foto_perfil else "",
        "ultima_conexion": request.user.last_login,
    }


def _parse_iso_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


# @login_required
# def inicio(request):
#     return HttpResponse("Bienvenido a la sección de Comisiones")


@login_required
def mis_ventas(request):

    def _unique_non_empty(values):
        seen = set()
        result = []
        for value in values:
            if value in (None, ""):
                continue
            if value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result

    fecha_desde_param = request.GET.get("desde")
    fecha_hasta_param = request.GET.get("hasta")
    fecha_desde_date = _parse_iso_date(fecha_desde_param)
    fecha_hasta_date = _parse_iso_date(fecha_hasta_param)

    if fecha_desde_date and fecha_hasta_date and fecha_hasta_date < fecha_desde_date:
        fecha_hasta_date = fecha_desde_date

    fecha_desde = fecha_desde_date.strftime("%Y-%m-%d") if fecha_desde_date else ""
    fecha_hasta = fecha_hasta_date.strftime("%Y-%m-%d") if fecha_hasta_date else ""

    ventas_periodo_qs = Venta.objects.filter(usuario=request.user)
    if fecha_desde_date:
        ventas_periodo_qs = ventas_periodo_qs.filter(fecha_venta__gte=fecha_desde_date)
    if fecha_hasta_date:
        ventas_periodo_qs = ventas_periodo_qs.filter(fecha_venta__lte=fecha_hasta_date)
    ventas_periodo_qs = ventas_periodo_qs.order_by("-fecha_venta", "-id")
    ventas_periodo = list(ventas_periodo_qs)

    matriculas_opciones = _unique_non_empty(venta.matricula for venta in ventas_periodo)
    idv_opciones = _unique_non_empty(str(venta.idv) for venta in ventas_periodo)
    tipo_venta_codes = _unique_non_empty(venta.tipo_venta for venta in ventas_periodo)
    dni_opciones = _unique_non_empty(venta.dni for venta in ventas_periodo)
    tipo_cliente_codes = _unique_non_empty(
        venta.tipo_cliente for venta in ventas_periodo
    )
    nombre_cliente_opciones = _unique_non_empty(
        venta.nombre_cliente for venta in ventas_periodo
    )

    tipo_venta_dict = dict(Venta.TIPO_VENTA_CHOICES)
    tipo_cliente_dict = dict(Venta.TIPO_CLIENTE_CHOICES)
    tipo_venta_opciones = [
        {"value": code, "label": tipo_venta_dict.get(code, code)}
        for code in tipo_venta_codes
    ]
    tipo_cliente_opciones = [
        {"value": code, "label": tipo_cliente_dict.get(code, code)}
        for code in tipo_cliente_codes
    ]

    filtros = {
        "matricula": request.GET.get("matricula", "").strip(),
        "idv": request.GET.get("idv", "").strip(),
        "tipo_venta": request.GET.get("tipo_venta", "").strip(),
        "dni": request.GET.get("dni", "").strip(),
        "tipo_cliente": request.GET.get("tipo_cliente", "").strip(),
        "nombre_cliente": request.GET.get("nombre_cliente", "").strip(),
    }

    ventas_qs = ventas_periodo_qs

    if filtros["matricula"]:
        ventas_qs = ventas_qs.filter(matricula__icontains=filtros["matricula"])

    if filtros["idv"]:
        if filtros["idv"].isdigit():
            ventas_qs = ventas_qs.filter(idv=int(filtros["idv"]))
        else:
            ventas_qs = ventas_qs.none()

    if filtros["tipo_venta"]:
        ventas_qs = ventas_qs.filter(tipo_venta__iexact=filtros["tipo_venta"])

    if filtros["dni"]:
        ventas_qs = ventas_qs.filter(dni__icontains=filtros["dni"])

    if filtros["tipo_cliente"]:
        ventas_qs = ventas_qs.filter(tipo_cliente__iexact=filtros["tipo_cliente"])

    if filtros["nombre_cliente"]:
        ventas_qs = ventas_qs.filter(
            nombre_cliente__icontains=filtros["nombre_cliente"]
        )

    ventas = list(ventas_qs)
    total_comision_aprobada = (
        Comision.objects.filter(venta__in=ventas_qs, estado="aprobada").aggregate(
            total=Sum("monto")
        )["total"]
    )
    comision_aprobada = (
        f"{total_comision_aprobada:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        if total_comision_aprobada is not None
        else ""
    )
    comision_aprobada_disponible = (
        comision_aprobada is not None and bool(str(comision_aprobada).strip())
    )

    # Garantiza perfil para usuarios antiguos que se crearon antes de esta lógica.
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    # Contexto que se pasará a la plantilla para renderizar la información de las ventas y comisiones del usuario.
    context = {
        **_contexto_base_usuario(request, perfil),
        "ultima_conexion": request.user.last_login,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "total_ventas_periodo": len(ventas),
        "comision_aprobada_str": comision_aprobada,
        "comision_aprobada_disponible": comision_aprobada_disponible,
        "ventas": ventas,
        "filtros": filtros,
        "matriculas_opciones": matriculas_opciones,
        "idv_opciones": idv_opciones,
        "tipo_venta_opciones": tipo_venta_opciones,
        "dni_opciones": dni_opciones,
        "tipo_cliente_opciones": tipo_cliente_opciones,
        "nombre_cliente_opciones": nombre_cliente_opciones,
    }

    return render(request, "comisiones/mis_ventas.html", context)


@login_required
def mis_incidencias(request):

    def _unique_non_empty(values):
        seen = set()
        result = []
        for value in values:
            if value in (None, ""):
                continue
            if value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result

    fecha_desde_param = request.GET.get("desde")
    fecha_hasta_param = request.GET.get("hasta")
    fecha_desde_date = _parse_iso_date(fecha_desde_param)
    fecha_hasta_date = _parse_iso_date(fecha_hasta_param)
    if fecha_desde_date and fecha_hasta_date and fecha_hasta_date < fecha_desde_date:
        fecha_hasta_date = fecha_desde_date

    fecha_desde = fecha_desde_date.strftime("%Y-%m-%d") if fecha_desde_date else ""
    fecha_hasta = fecha_hasta_date.strftime("%Y-%m-%d") if fecha_hasta_date else ""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    incidencias_periodo_qs = Incidencia.objects.filter(reportado_por=request.user)
    if fecha_desde_date:
        incidencias_periodo_qs = incidencias_periodo_qs.filter(
            fecha_incidencia__gte=fecha_desde_date
        )
    if fecha_hasta_date:
        incidencias_periodo_qs = incidencias_periodo_qs.filter(
            fecha_incidencia__lte=fecha_hasta_date
        )
    incidencias_periodo_qs = incidencias_periodo_qs.prefetch_related("ventas")
    incidencias_periodo = list(incidencias_periodo_qs)

    matriculas_opciones = []
    matriculas_seen = set()
    for incidencia in incidencias_periodo:
        if incidencia.es_general and "GENERAL" not in matriculas_seen:
            matriculas_opciones.append("GENERAL")
            matriculas_seen.add("GENERAL")
            continue
        for venta in incidencia.ventas.all():
            if venta.matricula in matriculas_seen:
                continue
            matriculas_opciones.append(venta.matricula)
            matriculas_seen.add(venta.matricula)

    estado_codes = _unique_non_empty(
        incidencia.estado for incidencia in incidencias_periodo
    )
    estado_dict = dict(Incidencia.ESTADOS)
    estado_opciones = [
        {"value": code, "label": estado_dict.get(code, code)} for code in estado_codes
    ]

    filtros = {
        "matricula": request.GET.get("matricula", "").strip(),
        "estado": request.GET.get("estado", "").strip(),
    }

    incidencias = incidencias_periodo_qs

    if filtros["matricula"]:
        matricula_val = filtros["matricula"]
        condicion_matricula = Q(ventas__matricula__icontains=matricula_val)
        if "general" in matricula_val.lower():
            condicion_matricula |= Q(es_general=True)
        incidencias = incidencias.filter(condicion_matricula).distinct()

    if filtros["estado"] in estado_codes:
        incidencias = incidencias.filter(estado=filtros["estado"])
    else:
        filtros["estado"] = ""

    context = {
        **_contexto_base_usuario(request, perfil),
        "ultima_conexion": request.user.last_login,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "incidencias": incidencias,
        "filtros": filtros,
        "matriculas_opciones": matriculas_opciones,
        "estado_opciones": estado_opciones,
    }
    return render(request, "comisiones/incidencias_personales.html", context)


@login_required
def registrar_incidencia(request):
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    ventas_usuario = list(
        Venta.objects.filter(usuario=request.user).order_by("-fecha_venta", "-id")
    )

    matriculas_disponibles = []
    matriculas_seen = set()
    for venta in ventas_usuario:
        if venta.matricula not in matriculas_seen:
            matriculas_disponibles.append(venta.matricula)
            matriculas_seen.add(venta.matricula)
    matriculas_opciones = ["GENERAL", *matriculas_disponibles]

    form_data = {
        "fecha_incidencia": date.today().strftime("%Y-%m-%d"),
        "matricula": "GENERAL",
        "tipo": "",
        "detalle": "",
    }
    errores = []

    if request.method == "POST":
        form_data = {
            "fecha_incidencia": request.POST.get("fecha_incidencia", "").strip(),
            "matricula": request.POST.get("matricula", "").strip(),
            "tipo": request.POST.get("tipo", "").strip(),
            "detalle": request.POST.get("detalle", "").strip(),
        }

        fecha = _parse_iso_date(form_data["fecha_incidencia"])
        if not fecha:
            errores.append("La fecha de incidencia no es válida.")
        elif fecha > date.today():
            errores.append("La fecha de incidencia no puede estar en el futuro.")

        if form_data["matricula"] not in matriculas_opciones:
            errores.append("Debes seleccionar una matrícula de tus ventas.")

        if not form_data["tipo"]:
            errores.append("El tipo de incidencia es obligatorio.")

        if not form_data["detalle"]:
            errores.append("El detalle de incidencia es obligatorio.")

        if not errores:
            incidencia = Incidencia.objects.create(
                reportado_por=request.user,
                es_general=form_data["matricula"] == "GENERAL",
                fecha_incidencia=fecha,
                tipo=form_data["tipo"],
                detalle=form_data["detalle"],
                estado="pte_revision",
                validacion_ok=False,
            )
            if form_data["matricula"] != "GENERAL":
                ventas_matricula = Venta.objects.filter(
                    usuario=request.user, matricula=form_data["matricula"]
                )
                incidencia.ventas.set(ventas_matricula)
            return redirect("mis_incidencias")

    context = {
        **_contexto_base_usuario(request, perfil),
        "form_data": form_data,
        "matriculas_disponibles": matriculas_disponibles,
        "matriculas_opciones": matriculas_opciones,
        "errores": errores,
    }
    return render(request, "comisiones/registrar_incidencia.html", context)


@login_required
def detalle_incidencia_personal(request, incidencia_id):
    fecha_desde_param = request.GET.get("desde")
    fecha_hasta_param = request.GET.get("hasta")
    fecha_desde_date = _parse_iso_date(fecha_desde_param)
    fecha_hasta_date = _parse_iso_date(fecha_hasta_param)
    if fecha_desde_date and fecha_hasta_date and fecha_hasta_date < fecha_desde_date:
        fecha_hasta_date = fecha_desde_date
    fecha_desde = fecha_desde_date.strftime("%Y-%m-%d") if fecha_desde_date else ""
    fecha_hasta = fecha_hasta_date.strftime("%Y-%m-%d") if fecha_hasta_date else ""

    filtros = {
        "matricula": request.GET.get("matricula", "").strip(),
        "estado": request.GET.get("estado", "").strip(),
    }

    incidencias_qs = Incidencia.objects.filter(reportado_por=request.user)
    if fecha_desde_date:
        incidencias_qs = incidencias_qs.filter(fecha_incidencia__gte=fecha_desde_date)
    if fecha_hasta_date:
        incidencias_qs = incidencias_qs.filter(fecha_incidencia__lte=fecha_hasta_date)

    if filtros["matricula"]:
        condicion_matricula = Q(ventas__matricula__icontains=filtros["matricula"])
        if "general" in filtros["matricula"].lower():
            condicion_matricula |= Q(es_general=True)
        incidencias_qs = incidencias_qs.filter(condicion_matricula).distinct()

    estados_validos = {code for code, _ in Incidencia.ESTADOS}
    if filtros["estado"] in estados_validos:
        incidencias_qs = incidencias_qs.filter(estado=filtros["estado"])
    else:
        filtros["estado"] = ""

    incidencias_filtradas = list(
        incidencias_qs.prefetch_related("ventas").order_by("-fecha_incidencia", "-id")
    )
    incidencia_ids = [inc.id for inc in incidencias_filtradas]

    incidencia = get_object_or_404(
        Incidencia.objects.prefetch_related("ventas"),
        id=incidencia_id,
        reportado_por=request.user,
    )

    anterior_id = None
    siguiente_id = None
    posicion_actual = None
    total_incidencias = len(incidencia_ids)
    if incidencia.id in incidencia_ids:
        idx = incidencia_ids.index(incidencia.id)
        posicion_actual = idx + 1
        if idx > 0:
            anterior_id = incidencia_ids[idx - 1]
        if idx < len(incidencia_ids) - 1:
            siguiente_id = incidencia_ids[idx + 1]

    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    context = {
        **_contexto_base_usuario(request, perfil),
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "incidencia": incidencia,
        "anterior_id": anterior_id,
        "siguiente_id": siguiente_id,
        "posicion_actual": posicion_actual,
        "total_incidencias": total_incidencias,
        "filtros": filtros,
    }
    return render(request, "comisiones/detalle_incidencia_personal.html", context)


@login_required
def mi_perfil(request):
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    context = {
        **_contexto_base_usuario(request, perfil),
        "ultima_conexion": request.user.last_login,
        "dni": "50232508W",
        "email": request.user.email or "usuario@empresa.com",
        "telefono": "637372631",
        "perfil_rol": "Vendedor",
        "area": "ventas",
        "concesionario": "Francisco Marcos",
        "direccion_comercial": "Ovidio Portillo",
        "gerencia": "Ovidio Portillo",
        "jefatura_ventas": "Francisco Javier González",
        "responsable_vo": "Damián Rech",
    }
    return render(request, "comisiones/mi_perfil.html", context)


@login_required
def comisiones_gerencia(request):
    if not _es_gerencia(request.user):
        return redirect("redirigir_por_rol")

    today = date.today()
    first_day = today.replace(day=1)
    last_day = today.replace(day=monthrange(today.year, today.month)[1])
    fecha_desde_param = request.GET.get("desde")
    fecha_hasta_param = request.GET.get("hasta")
    fecha_desde_date = _parse_iso_date(fecha_desde_param) or first_day
    fecha_hasta_date = _parse_iso_date(fecha_hasta_param) or last_day
    fecha_desde = fecha_desde_date.strftime("%Y-%m-%d")
    fecha_hasta = fecha_hasta_date.strftime("%Y-%m-%d")
    instalacion = request.GET.get("instalacion", "2901: Nissan Orihuela")
    vendedor = request.GET.get("vendedor", "Todos")

    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    ventas_qs = Venta.objects.filter(
        fecha_venta__range=(fecha_desde_date, fecha_hasta_date)
    ).select_related("usuario")

    vendedor_val = (vendedor or "").strip()
    if vendedor_val and vendedor_val.lower() != "todos":
        ventas_qs = ventas_qs.filter(
            Q(usuario__username__icontains=vendedor_val)
            | Q(usuario__first_name__icontains=vendedor_val)
            | Q(usuario__last_name__icontains=vendedor_val)
            | Q(matricula__icontains=vendedor_val)
        )

    filas = []
    for venta in ventas_qs.order_by("-fecha_venta", "-id"):
        nombre_empleado = (
            venta.usuario.get_full_name().strip()
            if venta.usuario
            else ""
        ) or (venta.usuario.username if venta.usuario else "Sin empleado")
        filas.append(
            {
                "empleado_matricula": f"{nombre_empleado} / {venta.matricula}",
                "ventas_idv": str(venta.idv),
                "facturacion": "-",
                "margen_bruto": "-",
                "imp_costo": "-",
                "comision_financiera": "-",
                "total_beneficio": "-",
                "seguros": "-",
                "imp_comision": "-",
                "estado": venta.get_tipo_venta_display(),
                "tipo_cliente": venta.get_tipo_cliente_display(),
            }
        )

    context = {
        **_contexto_base_usuario(request, perfil),
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "instalacion": instalacion,
        "vendedor": vendedor,
        "pendientes_revision": 1,
        "filas_comision": filas,
    }
    return render(request, "comisiones/comisiones.html", context)


@login_required
def incidencias_gerencia(request):
    if not _es_gerencia(request.user):
        return redirect("redirigir_por_rol")

    today = date.today()
    first_day = today.replace(day=1)
    last_day = today.replace(day=monthrange(today.year, today.month)[1])
    fecha_desde = request.GET.get("desde") or first_day.strftime("%Y-%m-%d")
    fecha_hasta = request.GET.get("hasta") or last_day.strftime("%Y-%m-%d")
    instalacion = request.GET.get("instalacion", "2901: Nissan Orihuela")
    vendedor = request.GET.get("vendedor", "Todos")

    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    incidencias = INCIDENCIAS

    context = {
        **_contexto_base_usuario(request, perfil),
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "instalacion": instalacion,
        "vendedor": vendedor,
        "pendientes_revision": 1,
        "incidencias": incidencias,
    }
    return render(request, "comisiones/incidencias_gerencia.html", context)


@login_required
def redirigir_por_rol(request):
    user = request.user

    if user.groups.filter(name__in=["Vendedor", "Jefe de ventas"]).exists():
        return redirect("mis_ventas")
    if _es_gerencia(user):
        return redirect("comisiones_gerencia")
