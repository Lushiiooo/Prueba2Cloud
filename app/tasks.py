"""
Celery tasks for medicalreserva app.
"""
from celery import shared_task
import logging
from django.utils import timezone
from datetime import timedelta
from app.models import Reserva

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def recordatorio_reserva_proxima(self):
    """
    Tarea periódica que envía recordatorios para reservas próximas (en 24 horas).
    Incluye lógica de reintento en caso de fallo.
    """
    try:
        ahora = timezone.now()
        manana = ahora + timedelta(hours=24)
        
        reservas_proximas = Reserva.objects.filter(
            fecha_hora__range=[ahora, manana],
            estado__in=['pendiente', 'confirmada']
        )
        
        for reserva in reservas_proximas:
            logger.info(f"[RECORDATORIO] Reserva #{reserva.id} próxima en 24 horas")
            # Aquí integrarías tu lógica de envío de email o SMS
            print(f"RECORDATORIO: Reserva #{reserva.id} de {reserva.paciente.usuario.get_full_name()} con Dr. {reserva.doctor.nombre} en 24 horas")
        
        return {
            'status': 'success',
            'recordatorios_enviados': reservas_proximas.count()
        }
    except Exception as exc:
        logger.error(f"Error en recordatorio_reserva_proxima: {exc}")
        # Reintenta la tarea en 60 segundos si ocurre un error
        raise self.retry(exc=exc, countdown=60)


@shared_task
def limpiar_reservas_antiguas():
    """
    Tarea periódica que marca como completadas las reservas que ya pasaron.
    """
    try:
        ahora = timezone.now()
        
        reservas_pasadas = Reserva.objects.filter(
            fecha_hora__lt=ahora,
            estado__in=['pendiente', 'confirmada']
        )
        
        count = reservas_pasadas.update(estado='completada')
        
        logger.info(f"[LIMPIAR] {count} reservas marcadas como completadas")
        print(f"LIMPIAR: {count} reservas marcadas como completadas")
        
        return {
            'status': 'success',
            'reservas_completadas': count
        }
    except Exception as exc:
        logger.error(f"Error en limpiar_reservas_antiguas: {exc}")
        return {'status': 'error', 'message': str(exc)}