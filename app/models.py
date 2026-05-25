"""
Models for the medical reservation platform.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Paciente(models.Model):
    """Patient profile linked to a User."""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='paciente_profile')
    fecha_nacimiento = models.DateField(verbose_name='Fecha de Nacimiento')
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono')
    direccion = models.TextField(blank=True, null=True, verbose_name='Dirección')
    numero_seguro = models.CharField(max_length=50, blank=True, null=True, verbose_name='Número de Seguro')
    alergias = models.TextField(blank=True, null=True, verbose_name='Alergias')
    
    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['usuario__first_name', 'usuario__last_name']
    
    def __str__(self):
        return f"Paciente: {self.usuario.get_full_name() or self.usuario.username}"


class Doctor(models.Model):
    """Doctor profile independent entity."""
    SPECIALTIES = (
        ('cardiologia', 'Cardiología'),
        ('pediatria', 'Pediatría'),
        ('dermatologia', 'Dermatología'),
        ('neurologia', 'Neurología'),
        ('oftalmologia', 'Oftalmología'),
        ('ortopedia', 'Ortopedia'),
        ('psiquiatria', 'Psiquiatría'),
        ('oncologia', 'Oncología'),
        ('general', 'Medicina General'),
    )
    
    nombre = models.CharField(max_length=150, verbose_name='Nombre Completo')
    especialidad = models.CharField(max_length=50, choices=SPECIALTIES, verbose_name='Especialidad')
    numero_cedula = models.CharField(max_length=50, unique=True, verbose_name='Número de Cédula')
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono')
    email = models.EmailField(verbose_name='Email')
    disponible = models.BooleanField(default=True, verbose_name='Disponible')
    experiencia_anos = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(70)],
        verbose_name='Años de Experiencia'
    )
    
    class Meta:
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctores'
        ordering = ['nombre']
    
    def __str__(self):
        return f"Dr. {self.nombre} - {self.get_especialidad_display()}"


class Reserva(models.Model):
    """Appointment/Reservation model."""
    STATUS_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    )
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='reservas', verbose_name='Paciente')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reservas', verbose_name='Doctor')
    fecha_hora = models.DateTimeField(verbose_name='Fecha y Hora de la Reserva')
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente', verbose_name='Estado')
    notas = models.TextField(blank=True, null=True, verbose_name='Notas')
    razon_consulta = models.CharField(max_length=255, verbose_name='Razón de la Consulta')
    creada_en = models.DateTimeField(auto_now_add=True, verbose_name='Creada en')
    actualizada_en = models.DateTimeField(auto_now=True, verbose_name='Actualizada en')
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_hora']
        unique_together = ['doctor', 'fecha_hora']
    
    def __str__(self):
        return f"Reserva {self.id} - {self.paciente} con {self.doctor.nombre} ({self.get_estado_display()})"
    
    @property
    def es_proxima(self):
        """Check if the appointment is in the future."""
        return self.fecha_hora > timezone.now()
    
    @property
    def horas_restantes(self):
        """Get hours remaining until the appointment."""
        if self.es_proxima:
            delta = self.fecha_hora - timezone.now()
            return delta.total_seconds() // 3600
        return 0
