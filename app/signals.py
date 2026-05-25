"""
Django signals for app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reserva
from .tasks import enviar_correo_reserva


@receiver(post_save, sender=Reserva)
def reserva_creada(sender, instance, created, **kwargs):
    """
    Signal handler that triggers email task when a reservation is created.
    """
    if created:
        # Trigger Celery task asynchronously
        enviar_correo_reserva.delay(instance.id)
