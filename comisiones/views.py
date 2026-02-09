from calendar import monthrange
from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

# Datos mockeados para mostrar en la plantilla. En un entorno real, estos datos se obtendrían de una consulta a SQL Server.
from .mock_data import VENTAS, COMISION_APROBADA, INCIDENCIAS
from .models import Perfil


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


# @login_required
# def inicio(request):
#     return HttpResponse("Bienvenido a la sección de Comisiones")


@login_required
def mis_ventas(request):
    # Obtienemos las fechas de inicio y fin del mes actual para mostrar un rango por defecto.
    today = date.today()
    first_day = today.replace(day=1)
    last_day = today.replace(day=monthrange(today.year, today.month)[1])

    # Si el usuario ha proporcionado fechas en la consulta, las usamos; de lo contrario, usamos el rango del mes actual.
    fecha_desde = request.GET.get("desde") or first_day.strftime("%Y-%m-%d")
    fecha_hasta = request.GET.get("hasta") or last_day.strftime("%Y-%m-%d")

    # Datos mockeados
    ventas = VENTAS
    comision_aprobada = COMISION_APROBADA

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
        "ventas": ventas,
    }

    return render(request, "comisiones/mis_ventas.html", context)


@login_required
def mis_incidencias(request):
    today = date.today()
    first_day = today.replace(day=1)
    last_day = today.replace(day=monthrange(today.year, today.month)[1])

    fecha_desde = request.GET.get("desde") or first_day.strftime("%Y-%m-%d")
    fecha_hasta = request.GET.get("hasta") or last_day.strftime("%Y-%m-%d")
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    incidencias = INCIDENCIAS

    context = {
        **_contexto_base_usuario(request, perfil),
        "ultima_conexion": request.user.last_login,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "incidencias": incidencias,
    }
    return render(request, "comisiones/incidencias_personales.html", context)


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
    fecha_desde = request.GET.get("desde") or first_day.strftime("%Y-%m-%d")
    fecha_hasta = request.GET.get("hasta") or last_day.strftime("%Y-%m-%d")
    instalacion = request.GET.get("instalacion", "2901: Nissan Orihuela")
    vendedor = request.GET.get("vendedor", "Todos")

    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    filas = [
        {
            "matricula": "2127MXT",
            "ventas_idv": "2398695",
            "facturacion": "31.448,76 €",
            "margen_bruto": "1.083,57 €",
            "imp_costo": "38.021,72 €",
            "comision_financiera": "307,50 €",
            "total_beneficio": "1.083,57 €",
            "seguros": "2",
            "imp_comision": "450 €",
            "estado": "VENTA DETALL EXENTA",
            "tipo_cliente": "CIF (FLOTAS)",
        },
        {
            "matricula": "0453MXZ",
            "ventas_idv": "2412606",
            "facturacion": "22.205,71 €",
            "margen_bruto": "1.694,88 €",
            "imp_costo": "27.669,93 €",
            "comision_financiera": "307,50 €",
            "total_beneficio": "977,35 €",
            "seguros": "",
            "imp_comision": "225 €",
            "estado": "VENTA RENTING",
            "tipo_cliente": "CIF (FLOTAS)",
        },
        {
            "matricula": "0422MXR",
            "ventas_idv": "2442228",
            "facturacion": "32.144,62 €",
            "margen_bruto": "2.723,34 €",
            "imp_costo": "32.117,36 €",
            "comision_financiera": "- €",
            "total_beneficio": "1.168,08 €",
            "seguros": "",
            "imp_comision": "500 €",
            "estado": "VENTA DETALL PARTICULAR",
            "tipo_cliente": "NIF (PARTICULAR)",
        },
        {
            "matricula": "1084MXR",
            "ventas_idv": "2440829",
            "facturacion": "17.375,75 €",
            "margen_bruto": "-45,58 €",
            "imp_costo": "18.482,95 €",
            "comision_financiera": "- €",
            "total_beneficio": "100,15 €",
            "seguros": "",
            "imp_comision": "0 €",
            "estado": "VENTA DETALL PARTICULAR",
            "tipo_cliente": "NIF (PARTICULAR)",
        },
        {
            "matricula": "9178MXV",
            "ventas_idv": "2446855",
            "facturacion": "13.916,5 €",
            "margen_bruto": "583,56 €",
            "imp_costo": "13.332,94 €",
            "comision_financiera": "- €",
            "total_beneficio": "858,34 €",
            "seguros": "",
            "imp_comision": "150 €",
            "estado": "VENTA DETALL PARTICULAR",
            "tipo_cliente": "NIF (PARTICULAR)",
        },
    ]

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
