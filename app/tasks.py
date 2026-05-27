"""
Celery tasks for medicalreserva app.
"""
from celery import shared_task
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def recordatorio_reserva_proxima():
    """
    Tarea periódica que envía recordatorios para reservas próximas (en 24 horas).
    """
    from app.models import Reserva
    from django.utils import timezone
    from datetime import timedelta
    
    ahora = timezone.now()
    manana = ahora + timedelta(hours=24)
    
    reservas_proximas = Reserva.objects.filter(
        fecha_hora__range=[ahora, manana],
        estado__in=['pendiente', 'confirmada']
    )
    
    for reserva in reservas_proximas:
        logger.info(f"[RECORDATORIO] Reserva #{reserva.id} próxima en 24 horas")
        print(f"RECORDATORIO: Reserva #{reserva.id} de {reserva.paciente.usuario.get_full_name()} con Dr. {reserva.doctor.nombre} en 24 horas")
    
    return {
        'status': 'success',
        'recordatorios_enviados': reservas_proximas.count()
    }


@shared_task
def limpiar_reservas_antiguas():
    """
    Tarea periódica que marca como completadas las reservas que ya pasaron.
    """
    from app.models import Reserva
    from django.utils import timezone
    
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
