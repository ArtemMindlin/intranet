from calendar import monthrange
from datetime import date
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q, Sum, CharField
from django.db.models.functions import Cast
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Comision, Incidencia, Perfil, Venta

# Envio de correo temporalmente desactivado:
# import logging
# from django.conf import settings
# from django.contrib import messages
# from django.core.mail import send_mail
# logger = logging.getLogger(__name__)
# DESTINATARIO_PRUEBA_INCIDENCIAS = "artem.mindlin@marcosautomocion.com"


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


def _parse_year_month(value):
    if not value:
        return None
    try:
        year_str, month_str = value.split("-", 1)
        year = int(year_str)
        month = int(month_str)
    except (TypeError, ValueError):
        return None
    if month < 1 or month > 12:
        return None
    return year, month


def _format_year_month(value):
    if not value:
        return ""
    year, month = value
    return f"{year:04d}-{month:02d}"


def _format_year_month_label(value):
    ym = _parse_year_month(value)
    if not ym:
        return value or ""
    year, month = ym
    return f"{month:02d}/{year:04d}"


def _year_month_bounds(value):
    year, month = value
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    return first_day, last_day


def _previous_year_month():
    today = date.today()
    if today.month == 1:
        return today.year - 1, 12
    return today.year, today.month - 1


def _resolve_month_range(
    desde_param, hasta_param, default_to_current=False, default_to_previous=False
):
    desde_ym = _parse_year_month(desde_param)
    hasta_ym = _parse_year_month(hasta_param)
    if default_to_previous:
        default_month = _previous_year_month()
        if not desde_ym:
            desde_ym = default_month
        if not hasta_ym:
            hasta_ym = default_month
    elif default_to_current:
        current = (date.today().year, date.today().month)
        if not desde_ym:
            desde_ym = current
        if not hasta_ym:
            hasta_ym = current
    if desde_ym and hasta_ym and hasta_ym < desde_ym:
        hasta_ym = desde_ym

    fecha_desde = _format_year_month(desde_ym)
    fecha_hasta = _format_year_month(hasta_ym)
    fecha_desde_date = _year_month_bounds(desde_ym)[0] if desde_ym else None
    fecha_hasta_date = _year_month_bounds(hasta_ym)[1] if hasta_ym else None
    return fecha_desde, fecha_hasta, fecha_desde_date, fecha_hasta_date


def _build_empty_pdf_bytes():
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Length 0 >>\nstream\n\nendstream\nendobj\n",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)

    xref_offset = len(pdf)
    pdf.extend(b"xref\n")
    pdf.extend(f"0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    pdf.extend(b"trailer\n")
    pdf.extend(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode("ascii"))
    pdf.extend(b"startxref\n")
    pdf.extend(f"{xref_offset}\n".encode("ascii"))
    pdf.extend(b"%%EOF\n")
    return bytes(pdf)


# Función auxiliar para obtener valores únicos y no vacíos de una lista, preservando el orden original. Esto se utiliza en la generación de opciones para los filtros de búsqueda en la vista de ventas del comercial.
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


@login_required
def descargar_boletin_mock(request, boletin_id):
    pdf_bytes = _build_empty_pdf_bytes()
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="boletin_{boletin_id}.pdf"'
    return response


def _enviar_correo_nueva_incidencia(incidencia):
    destinatario = getattr(settings, "INCIDENCIAS_EMAIL_TO", "").strip()
    if not destinatario:
        destinatario = (
            incidencia.reportado_por.email
            if incidencia.reportado_por and incidencia.reportado_por.email
            else "test@local.test"
        )

    usuario = (
        incidencia.reportado_por.get_full_name().strip()
        if incidencia.reportado_por
        else ""
    ) or (incidencia.reportado_por.username if incidencia.reportado_por else "Sin usuario")

    asunto = f"Nueva incidencia registrada - {incidencia.matricula_display}"
    cuerpo = (
        "Se ha registrado una nueva incidencia.\n\n"
        f"Usuario: {usuario}\n"
        f"Fecha incidencia: {incidencia.fecha_incidencia:%d/%m/%Y}\n"
        f"Matricula: {incidencia.matricula_display}\n"
        f"Tipo: {incidencia.tipo}\n"
        f"Estado: {incidencia.get_estado_display()}\n\n"
        f"Detalle:\n{incidencia.detalle}\n"
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "") or "no-reply@local.test"

    send_mail(
        subject=asunto,
        message=cuerpo,
        from_email=from_email,
        recipient_list=[destinatario],
        fail_silently=False,
    )


@login_required
def mis_ventas(request):

    # Por defecto se muestra el mes actual
    fecha_desde, fecha_hasta, fecha_desde_date, fecha_hasta_date = _resolve_month_range(
        request.GET.get("desde"), request.GET.get("hasta"), default_to_current=True
    )

    # Se obtienen las ventas del usuario en el rango de fechas seleccionado, aplicando filtros y ordenamientos según los parámetros de la consulta.
    ventas_periodo_qs = Venta.objects.filter(usuario=request.user)
    if fecha_desde_date:
        ventas_periodo_qs = ventas_periodo_qs.filter(fecha_venta__gte=fecha_desde_date)
    if fecha_hasta_date:
        ventas_periodo_qs = ventas_periodo_qs.filter(fecha_venta__lte=fecha_hasta_date)
    ventas_periodo_qs = ventas_periodo_qs.order_by("-fecha_venta", "-id")
    # ventas_periodo = list(ventas_periodo_qs)

    # Se generan las opciones únicas para los filtros de búsqueda en base a las ventas obtenidas, asegurando que no haya valores vacíos ni duplicados.

    matriculas_opciones = list(
        ventas_periodo_qs.exclude(matricula__isnull=True)
        .exclude(matricula="")
        .values_list("matricula", flat=True)
        .distinct()
        .order_by("matricula")
    )

    idv_opciones = list(
        ventas_periodo_qs.exclude(idv__isnull=True)
        .annotate(idv_str=Cast("idv", output_field=CharField()))
        .values_list("idv_str", flat=True)
        .distinct()
        .order_by("idv_str")
    )

    tipo_venta_codes = list(
        ventas_periodo_qs.exclude(tipo_venta__isnull=True)
        .exclude(tipo_venta="")
        .values_list("tipo_venta", flat=True)
        .distinct()
        .order_by("tipo_venta")
    )

    dni_opciones = list(
        ventas_periodo_qs.exclude(dni__isnull=True)
        .exclude(dni="")
        .values_list("dni", flat=True)
        .distinct()
        .order_by("dni")
    )

    tipo_cliente_codes = list(
        ventas_periodo_qs.exclude(tipo_cliente__isnull=True)
        .exclude(tipo_cliente="")
        .values_list("tipo_cliente", flat=True)
        .distinct()
        .order_by("tipo_cliente")
    )

    nombre_cliente_opciones = list(
        ventas_periodo_qs.exclude(nombre_cliente__isnull=True)
        .exclude(nombre_cliente="")
        .values_list("nombre_cliente", flat=True)
        .distinct()
        .order_by("nombre_cliente")
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

    sort_by = request.GET.get("sort", "fecha").strip().lower()
    sort_dir = request.GET.get("dir", "desc").strip().lower()
    campos_ordenables = {
        "matricula": "matricula",
        "fecha": "fecha_venta",
        "idv": "idv",
        "tipo_venta": "tipo_venta",
        "ud_financiadas": "ud_financiadas",
        "dni": "dni",
        "tipo_cliente": "tipo_cliente",
        "nombre_cliente": "nombre_cliente",
    }
    if sort_by not in campos_ordenables:
        sort_by = "fecha"
    if sort_dir not in {"asc", "desc"}:
        sort_dir = "desc"

    campo_orden = campos_ordenables[sort_by]
    prefijo = "" if sort_dir == "asc" else "-"
    orden = [f"{prefijo}{campo_orden}"]
    if campo_orden != "id":
        orden.append("id" if sort_dir == "asc" else "-id")
    ventas_qs = ventas_qs.order_by(*orden)

    siguiente_direccion = {}
    for campo in campos_ordenables:
        if sort_by == campo and sort_dir == "asc":
            siguiente_direccion[campo] = "desc"
        else:
            siguiente_direccion[campo] = "asc"

    ventas = list(ventas_qs)
    total_resultados = len(ventas)
    initial_visible_rows = 25
    initial_visible_count = min(total_resultados, initial_visible_rows)
    total_comision_aprobada = Comision.objects.filter(
        venta__in=ventas_qs, estado="aprobada"
    ).aggregate(total=Sum("monto"))["total"]
    comision_aprobada = (
        f"{total_comision_aprobada:,.2f}".replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
        if total_comision_aprobada is not None
        else ""
    )
    comision_aprobada_disponible = comision_aprobada is not None and bool(
        str(comision_aprobada).strip()
    )

    current_month = _format_year_month((date.today().year, date.today().month))
    active_filters = []
    if (fecha_desde or fecha_hasta) and (
        fecha_desde != current_month or fecha_hasta != current_month
    ):
        if fecha_desde and fecha_hasta:
            period_value = (
                f"{_format_year_month_label(fecha_desde)} - "
                f"{_format_year_month_label(fecha_hasta)}"
            )
        else:
            period_value = (
                _format_year_month_label(fecha_desde)
                if fecha_desde
                else _format_year_month_label(fecha_hasta)
            )
        active_filters.append(
            {
                "title": "Periodo",
                "label": f"Periodo: {period_value}",
                "fields": ["desde", "hasta"],
            }
        )

    filters_meta = (
        ("matricula", "Matrícula"),
        ("idv", "IDV"),
        ("tipo_venta", "Tipo venta"),
        ("dni", "DNI"),
        ("tipo_cliente", "Tipo cliente"),
        ("nombre_cliente", "Nombre cliente"),
    )
    for key, label in filters_meta:
        value = filtros.get(key, "")
        if value:
            active_filters.append(
                {"title": label, "label": f"{label}: {value}", "fields": [key]}
            )

    # Garantiza perfil para usuarios antiguos que se crearon antes de esta lógica.
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    # Contexto que se pasará a la plantilla para renderizar la información de las ventas y comisiones del usuario.
    context = {
        **_contexto_base_usuario(request, perfil),
        "ultima_conexion": request.user.last_login,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "total_ventas_periodo": total_resultados,
        "comision_aprobada_str": comision_aprobada,
        "comision_aprobada_disponible": comision_aprobada_disponible,
        "ventas": ventas,
        "total_resultados": total_resultados,
        "initial_visible_rows": initial_visible_rows,
        "initial_visible_count": initial_visible_count,
        "active_filters": active_filters,
        "filtros": filtros,
        "matriculas_opciones": matriculas_opciones,
        "idv_opciones": idv_opciones,
        "tipo_venta_opciones": tipo_venta_opciones,
        "dni_opciones": dni_opciones,
        "tipo_cliente_opciones": tipo_cliente_opciones,
        "nombre_cliente_opciones": nombre_cliente_opciones,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "siguiente_direccion": siguiente_direccion,
    }

    return render(request, "comisiones/mis_ventas.html", context)


@login_required
def mis_incidencias(request):

    fecha_desde, fecha_hasta, fecha_desde_date, fecha_hasta_date = _resolve_month_range(
        request.GET.get("desde"), request.GET.get("hasta"), default_to_current=True
    )
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    incidencias_periodo_qs = Incidencia.objects.filter(
        reportado_por=request.user
    ).prefetch_related("ventas")
    if fecha_desde_date:
        incidencias_periodo_qs = incidencias_periodo_qs.filter(
            fecha_incidencia__gte=fecha_desde_date
        )
    if fecha_hasta_date:
        incidencias_periodo_qs = incidencias_periodo_qs.filter(
            fecha_incidencia__lte=fecha_hasta_date
        )

    matriculas_opciones = []
    if incidencias_periodo_qs.filter(es_general=True).exists():
        matriculas_opciones.append("GENERAL")
    matriculas_opciones.extend(
        list(
            Venta.objects.filter(incidencias__in=incidencias_periodo_qs)
            .exclude(matricula__isnull=True)
            .exclude(matricula="")
            .values_list("matricula", flat=True)
            .distinct()
            .order_by("matricula")
        )
    )

    estado_codes = list(
        incidencias_periodo_qs.exclude(estado__isnull=True)
        .exclude(estado="")
        .values_list("estado", flat=True)
        .distinct()
        .order_by("estado")
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

    sort_by = request.GET.get("sort", "fecha").strip().lower()
    sort_dir = request.GET.get("dir", "desc").strip().lower()
    campos_ordenables = {"matricula", "fecha", "tipo", "detalle", "estado"}
    if sort_by not in campos_ordenables:
        sort_by = "fecha"
    if sort_dir not in {"asc", "desc"}:
        sort_dir = "desc"

    reverse_order = sort_dir == "desc"
    if sort_by == "matricula":
        incidencias = list(incidencias)
        incidencias = sorted(
            incidencias,
            key=lambda item: (item.matricula_display.lower(), item.id),
            reverse=reverse_order,
        )
    else:
        campos_orden_db = {
            "fecha": "fecha_incidencia",
            "tipo": "tipo",
            "detalle": "detalle",
            "estado": "estado",
        }
        campo_orden = campos_orden_db.get(sort_by, "fecha_incidencia")
        prefijo = "" if sort_dir == "asc" else "-"
        incidencias = incidencias.order_by(
            f"{prefijo}{campo_orden}", "id" if sort_dir == "asc" else "-id"
        )

    siguiente_direccion = {}
    for campo in campos_ordenables:
        if sort_by == campo and sort_dir == "asc":
            siguiente_direccion[campo] = "desc"
        else:
            siguiente_direccion[campo] = "asc"

    context = {
        **_contexto_base_usuario(request, perfil),
        "ultima_conexion": request.user.last_login,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "incidencias": incidencias,
        "filtros": filtros,
        "matriculas_opciones": matriculas_opciones,
        "estado_opciones": estado_opciones,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "siguiente_direccion": siguiente_direccion,
    }
    return render(request, "comisiones/incidencias_personales.html", context)


@login_required
def mis_comunicaciones(request):
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    fecha_desde, fecha_hasta, fecha_desde_date, fecha_hasta_date = _resolve_month_range(
        request.GET.get("desde"), request.GET.get("hasta"), default_to_current=True
    )

    comunicaciones = [
        {
            "id": 1,
            "boletin": "Boletin de objetivos comerciales",
            "fecha": date(2026, 2, 10),
            "marca": "Nissan",
            "tipo": "Comercial",
        },
        {
            "id": 2,
            "boletin": "Novedades de financiacion Q1",
            "fecha": date(2026, 1, 28),
            "marca": "Renault",
            "tipo": "Financiero",
        },
        {
            "id": 3,
            "boletin": "Cambios de campanas de marca",
            "fecha": date(2026, 1, 16),
            "marca": "Dacia",
            "tipo": "Marketing",
        },
    ]

    comunicaciones = sorted(
        comunicaciones, key=lambda item: item["fecha"], reverse=True
    )
    comunicaciones_periodo = comunicaciones
    if fecha_desde_date:
        comunicaciones_periodo = [
            item for item in comunicaciones_periodo if item["fecha"] >= fecha_desde_date
        ]
    if fecha_hasta_date:
        comunicaciones_periodo = [
            item for item in comunicaciones_periodo if item["fecha"] <= fecha_hasta_date
        ]

    marcas_opciones = sorted({item["marca"] for item in comunicaciones_periodo})
    tipos_opciones = sorted({item["tipo"] for item in comunicaciones_periodo})
    filtros = {
        "marca": request.GET.get("marca", "").strip(),
        "tipo": request.GET.get("tipo", "").strip(),
    }
    sort_by = request.GET.get("sort", "fecha").strip().lower()
    sort_dir = request.GET.get("dir", "desc").strip().lower()
    campos_ordenables = {"boletin", "fecha", "marca", "tipo"}
    if sort_by not in campos_ordenables:
        sort_by = "fecha"
    if sort_dir not in {"asc", "desc"}:
        sort_dir = "desc"

    comunicaciones_filtradas = comunicaciones_periodo
    if filtros["marca"]:
        comunicaciones_filtradas = [
            item
            for item in comunicaciones_filtradas
            if item["marca"].lower() == filtros["marca"].lower()
        ]
    if filtros["tipo"]:
        comunicaciones_filtradas = [
            item
            for item in comunicaciones_filtradas
            if item["tipo"].lower() == filtros["tipo"].lower()
        ]

    reverse_order = sort_dir == "desc"
    if sort_by == "fecha":
        comunicaciones_filtradas = sorted(
            comunicaciones_filtradas,
            key=lambda item: item["fecha"],
            reverse=reverse_order,
        )
    else:
        comunicaciones_filtradas = sorted(
            comunicaciones_filtradas,
            key=lambda item: str(item.get(sort_by, "")).lower(),
            reverse=reverse_order,
        )

    siguiente_direccion = {}
    for campo in campos_ordenables:
        if sort_by == campo and sort_dir == "asc":
            siguiente_direccion[campo] = "desc"
        else:
            siguiente_direccion[campo] = "asc"

    context = {
        **_contexto_base_usuario(request, perfil),
        "ultima_conexion": request.user.last_login,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "filtros": filtros,
        "marcas_opciones": marcas_opciones,
        "tipos_opciones": tipos_opciones,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "siguiente_direccion": siguiente_direccion,
        "comunicaciones": comunicaciones_filtradas,
    }
    return render(request, "comisiones/mis_comunicaciones.html", context)


def _render_pagina_boletin_simple(request, template_name):
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    context = {
        **_contexto_base_usuario(request, perfil),
        "ultima_conexion": request.user.last_login,
    }
    return render(request, template_name, context)


@login_required
def normativas(request):
    return _render_pagina_boletin_simple(request, "comisiones/normativas.html")


@login_required
def manuales(request):
    return _render_pagina_boletin_simple(request, "comisiones/manuales.html")


@login_required
def avisos_sin_leer(request):
    return _render_pagina_boletin_simple(request, "comisiones/avisos_sin_leer.html")


@login_required
def vehiculos_en_uso(request):
    return _render_pagina_boletin_simple(request, "comisiones/vehiculos_en_uso.html")


@login_required
def registrar_incidencia(request):
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    tipo_incidencia_opciones = [
        "Falta venta",
        "Sobra venta",
        "Falta financiacion",
    ]
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
        "tipo": tipo_incidencia_opciones[0],
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

        if form_data["tipo"] not in tipo_incidencia_opciones:
            errores.append("Debes seleccionar un tipo de incidencia válido.")

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
            _enviar_correo_nueva_incidencia(incidencia)
            return redirect("mis_incidencias")

    context = {
        **_contexto_base_usuario(request, perfil),
        "form_data": form_data,
        "matriculas_disponibles": matriculas_disponibles,
        "matriculas_opciones": matriculas_opciones,
        "tipo_incidencia_opciones": tipo_incidencia_opciones,
        "errores": errores,
    }
    return render(request, "comisiones/registrar_incidencia.html", context)


@login_required
def detalle_incidencia_personal(request, incidencia_id):
    fecha_desde, fecha_hasta, fecha_desde_date, fecha_hasta_date = _resolve_month_range(
        request.GET.get("desde"), request.GET.get("hasta")
    )

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
    if not perfil.ha_visto_perfil_inicial:
        perfil.ha_visto_perfil_inicial = True
        perfil.save(update_fields=["ha_visto_perfil_inicial"])

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

    fecha_desde, fecha_hasta, fecha_desde_date, fecha_hasta_date = _resolve_month_range(
        request.GET.get("desde"), request.GET.get("hasta"), default_to_current=True
    )
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
            venta.usuario.get_full_name().strip() if venta.usuario else ""
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

    fecha_desde, fecha_hasta, fecha_desde_date, fecha_hasta_date = _resolve_month_range(
        request.GET.get("desde"), request.GET.get("hasta"), default_to_current=True
    )
    instalacion = request.GET.get("instalacion", "2901: Nissan Orihuela")
    vendedor = request.GET.get("vendedor", "Todos")

    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    incidencias_qs = (
        Incidencia.objects.select_related("reportado_por")
        .prefetch_related("ventas")
        .order_by("-fecha_incidencia", "-id")
    )
    if fecha_desde_date:
        incidencias_qs = incidencias_qs.filter(fecha_incidencia__gte=fecha_desde_date)
    if fecha_hasta_date:
        incidencias_qs = incidencias_qs.filter(fecha_incidencia__lte=fecha_hasta_date)

    vendedor_val = (vendedor or "").strip()
    if vendedor_val and vendedor_val.lower() != "todos":
        incidencias_qs = incidencias_qs.filter(
            Q(reportado_por__username__icontains=vendedor_val)
            | Q(reportado_por__first_name__icontains=vendedor_val)
            | Q(reportado_por__last_name__icontains=vendedor_val)
            | Q(ventas__matricula__icontains=vendedor_val)
        ).distinct()

    incidencias = []
    for incidencia in incidencias_qs:
        usuario = incidencia.reportado_por
        nombre_empleado = (usuario.get_full_name().strip() if usuario else "") or (
            usuario.username if usuario else "Sin asignar"
        )
        incidencias.append(
            {
                "empleado": nombre_empleado,
                "matricula": incidencia.matricula_display,
                "fecha": incidencia.fecha_incidencia.strftime("%d/%m/%Y"),
                "tipo": incidencia.tipo,
                "detalle": incidencia.detalle,
                "estado": incidencia.get_estado_display(),
                "validacion_ok": incidencia.validacion_ok,
            }
        )

    pendientes_revision = incidencias_qs.filter(estado="pte_revision").count()

    context = {
        **_contexto_base_usuario(request, perfil),
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "instalacion": instalacion,
        "vendedor": vendedor,
        "pendientes_revision": pendientes_revision,
        "incidencias": incidencias,
    }
    return render(request, "comisiones/incidencias_gerencia.html", context)


@login_required
def redirigir_por_rol(request):
    user = request.user

    if user.groups.filter(name__in=["Vendedor", "Jefe de ventas"]).exists():
        return redirect("mis_ventas")
    return redirect("comisiones_gerencia")
