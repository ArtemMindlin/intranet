"""Rutas de la app comisiones.

Este modulo define los endpoints funcionales consumidos por perfiles de
gerencia y comerciales.
"""

# -*- coding: utf-8 -*-
from django.urls import path

from . import views

urlpatterns = [
    # Vista principal para gerencia (resumen de comisiones).
    # Temporalmente desactivada.
    path("", views.comisiones_gerencia, name="comisiones_gerencia"),
    # Vista activa del comercial.
    path("mis_ventas/", views.mis_ventas, name="mis_ventas"),
    # Vistas de incidencias del comercial.
    path("mis_incidencias/", views.mis_incidencias, name="mis_incidencias"),
    path("boletin/", views.mis_comunicaciones, name="boletin"),
    path(
        "mis_comunicaciones/",
        views.mis_comunicaciones,
        name="mis_comunicaciones",
    ),
    path("normativas/", views.normativas, name="normativas"),
    path("manuales/", views.manuales, name="manuales"),
    path("avisos_sin_leer/", views.avisos_sin_leer, name="avisos_sin_leer"),
    path("vehiculos_en_uso/", views.vehiculos_en_uso, name="vehiculos_en_uso"),
    path(
        "mis_comunicaciones/boletin/<int:boletin_id>/descargar/",
        views.descargar_boletin_mock,
        name="descargar_boletin_mock",
    ),
    path(
        "registrar_incidencia/",
        views.registrar_incidencia,
        name="registrar_incidencia",
    ),
    path(
        "mis_incidencias/<int:incidencia_id>/",
        views.detalle_incidencia_personal,
        name="detalle_incidencia_personal",
    ),
    path("mi_perfil/", views.mi_perfil, name="mi_perfil"),
    path("incidencias/", views.incidencias_gerencia, name="incidencias_gerencia"),
]
