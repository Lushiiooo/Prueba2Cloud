"""
Django admin configuration for medicalreserva app.
"""
from django.contrib import admin
from .models import Paciente, Doctor, Reserva


admin.site.register(Paciente)
admin.site.register(Doctor)
admin.site.register(Reserva)
