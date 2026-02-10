from django.urls import path
from . import views

urlpatterns = [
    # path("", views.comisiones_gerencia, name="comisiones_gerencia"),
    path("mis_ventas/", views.mis_ventas, name="mis_ventas"),
    path("mis_incidencias/", views.mis_incidencias, name="mis_incidencias"),
    path("registrar_incidencia/", views.registrar_incidencia, name="registrar_incidencia"),
    path(
        "mis_incidencias/<int:incidencia_id>/",
        views.detalle_incidencia_personal,
        name="detalle_incidencia_personal",
    ),
    path(
        "restablecer_contrasenya/",
        views.restablecer_contrasenya,
        name="restablecer_contrasenya",
    ),
    path("mi_perfil/", views.mi_perfil, name="mi_perfil"),
    path("comisiones/", views.comisiones_gerencia, name="comisiones_gerencia"),
    path("incidencias/", views.incidencias_gerencia, name="incidencias_gerencia"),
]
