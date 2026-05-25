"""
Celery tasks for medicalreserva app.
"""
from celery import shared_task
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def enviar_correo_reserva(self, reserva_id):
    """
    Simula el envío de un correo de confirmación de reserva.
    En producción, aquí usarías un servicio de email real (SendGrid, AWS SES, etc.)
    """
    from app.models import Reserva
    
    try:
        reserva = Reserva.objects.get(id=reserva_id)
        
        # Simular envío de correo (en producción aquí usarías django.core.mail.send_mail)
        mensaje = f"""
        ╔════════════════════════════════════════════════════════════════╗
        ║                   CONFIRMACIÓN DE RESERVA MÉDICA               ║
        ╚════════════════════════════════════════════════════════════════╝
        
        Estimado/a {reserva.paciente.usuario.get_full_name()},
        
        Su reserva ha sido registrada correctamente en el sistema.
        
        📋 DETALLES DE LA RESERVA:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        • ID de Reserva: #{reserva.id}
        • Doctor: Dr. {reserva.doctor.nombre}
        • Especialidad: {reserva.doctor.get_especialidad_display()}
        • Fecha y Hora: {reserva.fecha_hora.strftime('%d/%m/%Y %H:%M')}
        • Razón de la Consulta: {reserva.razon_consulta}
        • Estado: {reserva.get_estado_display()}
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        ⏰ RECORDATORIOS IMPORTANTES:
        • Por favor, llegar 10 minutos antes de la cita
        • Llevar su documento de identidad
        • En caso de cambios, notificar con 24 horas de anticipación
        
        📞 ¿NECESITAS AYUDA?
        Para cambios o cancelaciones, contacta al: +1-800-MEDICAL
        O responde este correo directamente.
        
        ¡Esperamos brindarte la mejor atención!
        
        Medical Reserva Platform 🏥
        """
        
        logger.info(f"[CELERY TASK] Tarea enviando correo para la reserva #{reserva.id}")
        logger.info(f"[CORREO ENVIADO A] {reserva.paciente.usuario.email}")
        print(mensaje)
        
        return {
            'status': 'success',
            'message': f'Correo enviado para la reserva #{reserva.id}',
            'timestamp': timezone.now().isoformat()
        }
    
    except Reserva.DoesNotExist:
        logger.error(f"[CELERY ERROR] Reserva #{reserva_id} no encontrada")
        return {
            'status': 'error',
            'message': f'Reserva #{reserva_id} no encontrada'
        }
    
    except Exception as e:
        logger.error(f"[CELERY ERROR] Error al enviar correo para la reserva #{reserva_id}: {str(e)}")
        self.retry(exc=e, countdown=60, max_retries=3)


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
