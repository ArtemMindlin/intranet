from django.contrib import admin
from .models import Boletin, Comision, Incidencia, LecturaBoletin, Perfil, Venta


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        "matricula",
        "nombre_cliente",
        "usuario",
        "tipo_venta",
        "fecha_venta",
    )
    list_filter = ("tipo_venta", "tipo_cliente", "fecha_venta")
    search_fields = ("matricula", "idv", "dni", "nombre_cliente", "usuario__username")

    def save_model(self, request, obj, form, change):
        es_equipo_ventas = request.user.groups.filter(
            name__in=["Vendedor", "Jefe de ventas"]
        ).exists()
        if not change and es_equipo_ventas:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comision)
class ComisionAdmin(admin.ModelAdmin):
    list_display = ("venta", "monto", "estado", "fecha_creacion")


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reportado_por",
        "matricula_listado",
        "es_general",
        "tipo",
        "estado",
        "validacion_ok",
        "fecha_incidencia",
    )
    list_filter = ("estado", "validacion_ok", "es_general", "fecha_incidencia")
    search_fields = ("tipo", "detalle", "ventas__matricula", "reportado_por__username")
    filter_horizontal = ("ventas",)

    def matricula_listado(self, obj):
        return obj.matricula_display

    matricula_listado.short_description = "Matrícula"

    def save_model(self, request, obj, form, change):
        es_equipo_ventas = request.user.groups.filter(
            name__in=["Vendedor", "Jefe de ventas"]
        ).exists()
        if not change and es_equipo_ventas:
            obj.reportado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "dni",
        "telefono",
        "area",
        "sede",
        "jefe_ventas",
        "gerente",
        "director_comercial",
        "foto_perfil",
    )
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "dni",
        "telefono",
        "area",
        "sede",
        "jefe_ventas__username",
        "jefe_ventas__first_name",
        "jefe_ventas__last_name",
        "gerente__username",
        "gerente__first_name",
        "gerente__last_name",
        "director_comercial__username",
        "director_comercial__first_name",
        "director_comercial__last_name",
    )
    list_select_related = ("user", "jefe_ventas", "gerente", "director_comercial")
    autocomplete_fields = ("user", "jefe_ventas", "gerente", "director_comercial")
    list_filter = ("area", "sede")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "jefe_ventas":
            kwargs["queryset"] = db_field.related_model.objects.filter(
                groups__name="Jefe de ventas"
            ).distinct()
        elif db_field.name == "gerente":
            kwargs["queryset"] = db_field.related_model.objects.filter(
                groups__name="Gerente"
            ).distinct()
        elif db_field.name == "director_comercial":
            kwargs["queryset"] = db_field.related_model.objects.filter(
                groups__name="Director Comercial"
            ).distinct()
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name in {"jefe_ventas", "gerente", "director_comercial"}:
            formfield.label_from_instance = (
                lambda obj: obj.get_full_name().strip() or obj.username
            )
        return formfield


@admin.register(Boletin)
class BoletinAdmin(admin.ModelAdmin):
    list_display = ("boletin", "fecha", "marca", "tipo", "activo")
    list_filter = ("activo", "fecha", "marca", "tipo")
    search_fields = ("boletin", "marca", "tipo")


@admin.register(LecturaBoletin)
class LecturaBoletinAdmin(admin.ModelAdmin):
    list_display = ("boletin", "usuario", "leido_en", "confirmado")
    list_filter = ("confirmado", "leido_en")
    search_fields = ("boletin__boletin", "usuario__username", "usuario__first_name")
