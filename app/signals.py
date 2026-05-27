"""
Django signals for app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reserva

@receiver(post_save, sender=Reserva)
def reserva_post_save(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta después de guardar una reserva.
    Aquí puedes agregar lógica adicional, como enviar notificaciones o actualizar estadísticas.
    """
    if created:
        print(f"Reserva creada: {instance}")
    else:
        print(f"Reserva actualizada: {instance}")
