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


@shared_task
def backup_multicloud_task():
    """
    Tarea programada para ejecutar el script de backup a MultiCloud (Azure).
    Se ejecuta diariamente a la medianoche (00:00).
    """
    import subprocess
    from datetime import datetime
    
    try:
        script_path = "/app/backup_multicloud.sh"
        
        # Ejecutar el script bash
        result = subprocess.run(
            ['/bin/bash', script_path],
            capture_output=True,
            text=True,
            timeout=3600  # Timeout de 1 hora
        )
        
        # Capturar salida y errores
        stdout = result.stdout
        stderr = result.stderr
        returncode = result.returncode
        
        # Logging de la ejecución
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if returncode == 0:
            logger.info(
                f"[BACKUP_MULTICLOUD] ✓ Ejecutado exitosamente a {timestamp}\n"
                f"STDOUT:\n{stdout}"
            )
            return {
                'status': 'success',
                'timestamp': timestamp,
                'returncode': returncode,
                'message': 'Backup a MultiCloud ejecutado correctamente'
            }
        else:
            logger.error(
                f"[BACKUP_MULTICLOUD] ✗ Error en ejecución a {timestamp}\n"
                f"STDOUT:\n{stdout}\n"
                f"STDERR:\n{stderr}"
            )
            return {
                'status': 'error',
                'timestamp': timestamp,
                'returncode': returncode,
                'message': 'Error durante el backup',
                'error': stderr
            }
            
    except subprocess.TimeoutExpired:
        logger.error("[BACKUP_MULTICLOUD] ✗ Timeout: El script tardó más de 1 hora")
        return {
            'status': 'error',
            'message': 'Timeout: El backup tardó demasiado tiempo'
        }
    except Exception as e:
        logger.error(f"[BACKUP_MULTICLOUD] ✗ Excepción: {str(e)}")
        return {
            'status': 'error',
            'message': f'Excepción durante el backup: {str(e)}'
        }
