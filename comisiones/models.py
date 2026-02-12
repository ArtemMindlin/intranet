from datetime import date

from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Venta(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ventas",
        null=True,
        blank=True,
    )
    matricula = models.CharField(max_length=10)
    idv = models.IntegerField()

    TIPO_VENTA_CHOICES = [
        ("EXENTA", "Venta Detall Exenta"),
        ("RENTING", "Venta Renting"),
        ("PARTICULAR", "Venta Detall Particular"),
    ]
    tipo_venta = models.CharField(max_length=20, choices=TIPO_VENTA_CHOICES)

    ud_financiadas = models.PositiveIntegerField(null=True, blank=True)

    dni = models.CharField(max_length=12)

    TIPO_CLIENTE_CHOICES = [
        ("CIF", "CIF (Flotas)"),
        ("NIF", "NIF (Particular)"),
    ]
    tipo_cliente = models.CharField(max_length=3, choices=TIPO_CLIENTE_CHOICES)

    nombre_cliente = models.CharField(max_length=100)

    fecha_venta = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.matricula} - {self.nombre_cliente} - {self.tipo_venta}"


class Comision(models.Model):
    """Representa una comisión asociada a una venta"""

    venta = models.ForeignKey("Venta", on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    facturacion = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    margen_bruto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    imp_costo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    comision_financiera = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    total_beneficio = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    seguros = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    imp_comision = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("aprobada", "Aprobada"),
        ("rechazada", "Rechazada"),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default="pendiente")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.venta} – {self.monto} € – {self.get_estado_display()}"


class Incidencia(models.Model):
    ESTADOS = [
        ("pte_revision", "Pte. revision"),
        ("aceptada", "Aceptada"),
        ("rechazada", "Rechazada"),
    ]

    reportado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="incidencias_reportadas",
        null=True,
        blank=True,
    )
    ventas = models.ManyToManyField("Venta", related_name="incidencias", blank=True)
    es_general = models.BooleanField(default=False)
    fecha_incidencia = models.DateField(default=date.today)
    tipo = models.CharField(max_length=150)
    detalle = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pte_revision")
    validacion_ok = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha_incidencia", "-id"]

    @property
    def matricula_display(self):
        if self.es_general:
            return "GENERAL"
        matriculas = [venta.matricula for venta in self.ventas.all()]
        if not matriculas:
            return "GENERAL"
        return ", ".join(matriculas)

    def __str__(self):
        return f"Incidencia {self.id or '-'} - {self.tipo}"


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sede = models.CharField(max_length=100, blank=True, default="")
    ha_visto_perfil_inicial = models.BooleanField(default=False)
    jefe_ventas = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendedores_asignados",
    )
    gerente = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jefes_ventas_asignados",
    )
    director_comercial = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gerentes_asignados",
    )
    foto_perfil = models.ImageField(upload_to="perfiles/", blank=True, null=True)

    def save(self, *args, **kwargs):
        # Jerarquia automatica:
        # vendedor -> jefe_ventas -> gerente -> director_comercial
        if self.jefe_ventas_id:
            jefe_perfil = self.__class__.objects.filter(user_id=self.jefe_ventas_id).first()
            self.gerente = jefe_perfil.gerente if jefe_perfil else None

            if self.gerente_id:
                gerente_perfil = self.__class__.objects.filter(
                    user_id=self.gerente_id
                ).first()
                self.director_comercial = (
                    gerente_perfil.director_comercial if gerente_perfil else None
                )
            else:
                self.director_comercial = None
        elif self.gerente_id:
            gerente_perfil = self.__class__.objects.filter(user_id=self.gerente_id).first()
            self.director_comercial = (
                gerente_perfil.director_comercial if gerente_perfil else None
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Perfil de {self.user.username}"


@receiver(post_save, sender=User)
def crear_perfil_automatico(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.get_or_create(user=instance)
