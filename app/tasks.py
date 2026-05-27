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

    reserva = Reserva.objects.select_related(
        'paciente__usuario',
        'doctor'
    ).get(id=reserva_id)

    paciente = reserva.paciente
    doctor = reserva.doctor
    usuario = paciente.usuario

    email_destino = usuario.email

    context = {
        'nombre_paciente': usuario.get_full_name(),
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

    resend.api_key = settings.RESEND_API_KEY

    response = resend.Emails.send({
        "from": settings.RESEND_FROM_EMAIL,
        "to": [email_destino],
        "subject": f"Reserva #{reserva.id} confirmada",
        "html": html_body,
        "text": text_body,
    })

    return {
        "status": "enviado",
        "resend_id": response.get("id")
    }


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
