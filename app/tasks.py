"""
Celery tasks for medicalreserva app.
"""
from celery import shared_task
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 30},
    name='app.tasks.enviar_correo_reserva',
)
def enviar_correo_reserva(self, reserva_id):

    import resend
    from django.conf import settings
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from app.models import Reserva

    try:
        # Validar que la API key esté configurada
        api_key = settings.RESEND_API_KEY
        if not api_key:
            logger.error(f"[RESEND ERROR] RESEND_API_KEY no está configurada")
            return {
                "status": "error",
                "message": "RESEND_API_KEY no está configurada"
            }

        reserva = Reserva.objects.select_related(
            'paciente__usuario',
            'doctor'
        ).get(id=reserva_id)

        paciente = reserva.paciente
        doctor = reserva.doctor
        usuario = paciente.usuario

        # Enviar siempre a este email (configurado por el administrador)
        email_destino = 'servidor12minecraft21@gmail.com'

        logger.info(f"[RESEND] Preparando correo para la reserva #{reserva.id}")
        logger.info(f"[RESEND] Email destino: {email_destino}")
        logger.info(f"[RESEND] From: {settings.RESEND_FROM_EMAIL}")

        context = {
            'nombre_paciente': usuario.get_full_name(),
            'email_paciente': usuario.email,
            'reserva_id': reserva.id,
            'doctor_nombre': doctor.nombre,
            'especialidad': doctor.get_especialidad_display(),
            'fecha_hora': reserva.fecha_hora.strftime('%d/%m/%Y %H:%M'),
            'razon_consulta': reserva.razon_consulta,
            'estado': reserva.get_estado_display(),
        }

        html_body = render_to_string(
            'emails/confirmacion_reserva.html',
            context
        )

        text_body = strip_tags(html_body)

        resend.api_key = api_key

        logger.info(f"[RESEND] Enviando correo con Resend API...")

        response = resend.Emails.send({
            "from": settings.RESEND_FROM_EMAIL,
            "to": [email_destino],
            "subject": f"Reserva #{reserva.id} confirmada - {usuario.get_full_name()}",
            "html": html_body,
            "text": text_body,
        })

        logger.info(f"[RESEND] Respuesta: {response}")

        if response.get("id"):
            logger.info(f"[RESEND] Correo enviado exitosamente. ID: {response.get('id')}")
            return {
                "status": "enviado",
                "resend_id": response.get("id")
            }
        else:
            error_msg = response.get("message", "Error desconocido")
            logger.error(f"[RESEND ERROR] {error_msg}")
            return {
                "status": "error",
                "message": error_msg
            }

    except Exception as e:
        logger.error(f"[RESEND ERROR] Excepción al enviar correo para reserva #{reserva_id}: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=30, max_retries=3)


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
