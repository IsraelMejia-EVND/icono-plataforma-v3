from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Usuario(AbstractUser):
    pass

class Tendencia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Prenda(models.Model):
    nombre = models.CharField(max_length=120)
    enlace_externo = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return self.nombre


class Outfit(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField()
    tendencia = models.ForeignKey(Tendencia, on_delete=models.PROTECT)
    prendas = models.ManyToManyField(Prenda)
    publicado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre


class Favorito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    outfit = models.ForeignKey(Outfit, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "outfit"],
                name="core_favorito_usuario_outfit_unico",
            ),
        ]

class Comentario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    outfit = models.ForeignKey(Outfit, on_delete=models.CASCADE)
    texto = models.CharField(max_length=500)
    calificacion = models.PositiveSmallIntegerField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "outfit"],
                name="core_comentario_usuario_outfit_unico",
            ),
            models.CheckConstraint(
                condition=models.Q(calificacion__gte=1, calificacion__lte=5),
                name="core_comentario_calificacion_1_a_5",
            ),
        ]

class PerfilEstilo(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    tendencia_preferida = models.ForeignKey(
        Tendencia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    objetivo = models.CharField(max_length=300, blank=True)

class Cita(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        CONFIRMADA = "confirmada", "Confirmada"
        COMPLETADA = "completada", "Completada"
        CANCELADA = "cancelada", "Cancelada"

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="citas_como_cliente",
    )
    asesor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="citas_como_asesor",
    )
    fecha_hora = models.DateTimeField()
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )