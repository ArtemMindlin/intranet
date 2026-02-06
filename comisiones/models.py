from django.db import models


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


# Create your models here.
class Comision(models.Model):
    """Representa una comisión asociada a una venta"""  # 3

    venta = models.ForeignKey("Venta", on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    PENDIENTE = "pendiente"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    ESTADOS = [
        (PENDIENTE, "Pendiente"),
        (APROBADA, "Aprobada"),
        (RECHAZADA, "Rechazada"),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default=PENDIENTE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.venta} – {self.monto} € – {self.get_estado_display()}"
