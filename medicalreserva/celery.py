"""
Celery configuration for medicalreserva project.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicalreserva.settings')

app = Celery('medicalreserva')

# Load configuration from Django settings, all celery configuration should be namespaced under CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps.
app.autodiscover_tasks()

# ============================================================================
# CELERY BEAT SCHEDULE - Tareas programadas
# ============================================================================
app.conf.beat_schedule = {
    'backup-multicloud-diario': {
        'task': 'app.tasks.backup_multicloud_task',
        'schedule': crontab(hour=0, minute='*/1'),   # cada 1 minuto para pruebas (cambiar a diario en producción)
        'options': {'queue': 'default', 'expires': 300}
    },
    'recordatorio-reserva-proxima': {
        'task': 'app.tasks.recordatorio_reserva_proxima',
        'schedule': crontab(hour='*/6'),  # Cada 6 horas
        'options': {'queue': 'default', 'expires': 300}
    },
    'limpiar-reservas-antiguas': {
        'task': 'app.tasks.limpiar_reservas_antiguas',
        'schedule': crontab(hour=2, minute=0),  # 02:00 todos los días
        'options': {'queue': 'default', 'expires': 300}
    },
}

# Configuración adicional de Celery Beat
app.conf.timezone = 'America/Santiago'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
