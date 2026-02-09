from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Venta(models.Model):
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
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("aprobada", "Aprobada"),
        ("rechazada", "Rechazada"),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default="pendiente")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.venta} – {self.monto} € – {self.get_estado_display()}"


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sede = models.CharField(max_length=100, blank=True, default="")
    foto_perfil = models.ImageField(upload_to="perfiles/", blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"


@receiver(post_save, sender=User)
def crear_perfil_automatico(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.get_or_create(user=instance)
