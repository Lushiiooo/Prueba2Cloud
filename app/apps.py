"""
Application configuration for app.
"""
from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    verbose_name = 'Reservas Médicas'
    
    def ready(self):
        """Import signals when the app is ready."""
        import app.signals
