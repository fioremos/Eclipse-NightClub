from django.db import models
from django.core.validators import MinValueValidator

class SolicitudConsulta(models.Model):
    TIPO_CHOICES = [
        ('mesa', 'Reserva de Mesa'),
        ('evento', 'Evento Privado'),
        ('general', 'Consulta General'),
    ]

    nombre_completo = models.CharField(max_length=50)
    correo_electronico = models.EmailField()
    tipo_consulta_cliente = models.CharField(max_length=20, choices=TIPO_CHOICES, default='general')
    fecha_reserva = models.DateField(null=True, blank=True)
    cantidad_personas = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)]
    )
    mensaje = models.TextField()
    categoria_asignada = models.CharField(max_length=50, default='General')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        mensaje_minuscula = self.mensaje.lower()

        if any(palabra in mensaje_minuscula for palabra in ["precio", "costo", "tarifa", "compra"]):
            self.categoria_asignada = 'Comercial'
        elif any(palabra in mensaje_minuscula for palabra in ["soporte", "error", "problema", "ayuda"]):
            self.categoria_asignada = 'Tecnica'
        elif any(palabra in mensaje_minuscula for palabra in ["trabajo", "cv", "empleo", "linkedin"]):
            self.categoria_asignada = 'RRHH'
        else:
            self.categoria_asignada = 'General'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_completo} - {self.tipo_consulta_cliente}-{self.fecha_creacion}"

class UsuarioPermitido(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    codigo_validation = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.nombre} ({self.email})"

class Meta:
    verbose_name = "Usuario Permitido"
    verbose_name = "Usuarios Permitidos"

class RegistroReserva(SolicitudConsulta):
    class Meta:
        proxy = True
        verbose_name = "Reserva de Mesa"
        verbose_name_plural = "RESERVAS DE MESAS"

class RegistroConsulta(SolicitudConsulta):
    class Meta:
        proxy = True
        verbose_name = "Consulta General"
        verbose_name_plural = "CONSULTAS GENERALES"

class RegistroEvento(SolicitudConsulta):
    class Meta:
        proxy = True
        verbose_name = "Evento Privado"
        verbose_name_plural = "EVENTOS PRIVADOS"