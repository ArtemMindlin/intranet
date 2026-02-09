from django.contrib import admin
from .models import Venta, Comision, Perfil


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("matricula", "nombre_cliente", "tipo_venta", "fecha_venta")


@admin.register(Comision)
class ComisionAdmin(admin.ModelAdmin):
    list_display = ("venta", "monto", "estado", "fecha_creacion")


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "sede", "foto_perfil")
