"""Enrutamiento principal del proyecto intranet.

Este modulo centraliza las rutas globales (admin y autenticacion) y delega
las rutas funcionales al modulo `comisiones`.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

import comisiones.views

urlpatterns = [
    # Entrada raiz del sitio: muestra el formulario de inicio de sesion.
    path("", auth_views.LoginView.as_view(), name="root_login"),
    # Panel de administracion nativo de Django.
    path("admin/", admin.site.urls),
    # Espacio de rutas de la aplicacion de negocio.
    path("comisiones/", include("comisiones.urls")),
    # Endpoints de autenticacion.
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    # Redireccion posterior al login segun el rol del usuario.
    path(
        "redirigir/",
        comisiones.views.redirigir_por_rol,
        name="redirigir_por_rol",
    ),
]

if settings.DEBUG:
    # En desarrollo, Django sirve archivos de MEDIA de forma local.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
