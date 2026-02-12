"""Rutas de la app comisiones.

Este modulo define los endpoints funcionales consumidos por perfiles de
gerencia y comerciales.
"""

# -*- coding: utf-8 -*-
from django.urls import path

from . import views

urlpatterns = [
    # Vista principal para gerencia (resumen de comisiones).
    # path("", views.comisiones_gerencia, name="comisiones_gerencia"),
    # Vistas del comercial.
    path("mis_ventas/", views.mis_ventas, name="mis_ventas"),
    path("mis_incidencias/", views.mis_incidencias, name="mis_incidencias"),
    # Registro de una nueva incidencia.
    path(
        "registrar_incidencia/", views.registrar_incidencia, name="registrar_incidencia"
    ),
    # Detalle de una incidencia concreta del usuario autenticado.
    path(
        "mis_incidencias/<int:incidencia_id>/",
        views.detalle_incidencia_personal,
        name="detalle_incidencia_personal",
    ),
    # Perfil del usuario autenticado.
    path("mi_perfil/", views.mi_perfil, name="mi_perfil"),
    # Gestion de incidencias para gerencia.
    path("incidencias/", views.incidencias_gerencia, name="incidencias_gerencia"),
]
