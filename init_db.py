#!/usr/bin/env python
"""
Script para inicializar la base de datos con datos de prueba.
Se ejecuta automáticamente después de las migraciones.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicalreserva.settings')
django.setup()

from app.models import Paciente, Doctor
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

def crear_doctores():
    """Crear doctores de prueba si no existen"""
    doctores = [
        {
            'nombre': 'Dr. Carlos López Martínez',
            'especialidad': 'cardiologia',
            'cedula': 'MED001',
            'telefono': '555-0001',
            'email': 'carlos.lopez@clinic.com',
            'experiencia_anos': 18
        },
        {
            'nombre': 'Dra. María García Rodríguez',
            'especialidad': 'pediatria',
            'cedula': 'MED002',
            'telefono': '555-0002',
            'email': 'maria.garcia@clinic.com',
            'experiencia_anos': 12
        },
        {
            'nombre': 'Dr. Juan Fernández Silva',
            'especialidad': 'dermatologia',
            'cedula': 'MED003',
            'telefono': '555-0003',
            'email': 'juan.fernandez@clinic.com',
            'experiencia_anos': 15
        },
        {
            'nombre': 'Dra. Ana Martínez López',
            'especialidad': 'neurologia',
            'cedula': 'MED004',
            'telefono': '555-0004',
            'email': 'ana.martinez@clinic.com',
            'experiencia_anos': 20
        },
        {
            'nombre': 'Dr. Roberto Sánchez Gómez',
            'especialidad': 'oftalmologia',
            'cedula': 'MED005',
            'telefono': '555-0005',
            'email': 'roberto.sanchez@clinic.com',
            'experiencia_anos': 14
        },
        {
            'nombre': 'Dra. Patricia Díaz Ruiz',
            'especialidad': 'ortopedia',
            'cedula': 'MED006',
            'telefono': '555-0006',
            'email': 'patricia.diaz@clinic.com',
            'experiencia_anos': 16
        },
    ]

    for doc_data in doctores:
        doctor, created = Doctor.objects.get_or_create(
            numero_cedula=doc_data['cedula'],
            defaults={
                'nombre': doc_data['nombre'],
                'especialidad': doc_data['especialidad'],
                'telefono': doc_data['telefono'],
                'email': doc_data['email'],
                'disponible': True,
                'experiencia_anos': doc_data['experiencia_anos'],
            }
        )
        status = "✅ Creado" if created else "⏭️ Ya existe"
        print(f"{status}: {doctor.nombre} ({doctor.especialidad})")


def crear_pacientes():
    """Crear pacientes de prueba si no existen"""
    pacientes = [
        {
            'username': 'paciente1',
            'password': 'demo1234',
            'first_name': 'Juan',
            'last_name': 'Pérez García',
            'email': 'juan.perez@email.com',
            'fecha_nacimiento': '1990-05-15',
            'telefono': '555-1001',
            'numero_seguro': 'SEG001',
            'alergias': 'Penicilina'
        },
        {
            'username': 'paciente2',
            'password': 'demo1234',
            'first_name': 'María',
            'last_name': 'López Martínez',
            'email': 'maria.lopez@email.com',
            'fecha_nacimiento': '1988-08-22',
            'telefono': '555-1002',
            'numero_seguro': 'SEG002',
            'alergias': 'Aspirina'
        },
        {
            'username': 'paciente3',
            'password': 'demo1234',
            'first_name': 'Carlos',
            'last_name': 'González Ruiz',
            'email': 'carlos.gonzalez@email.com',
            'fecha_nacimiento': '1995-12-03',
            'telefono': '555-1003',
            'numero_seguro': 'SEG003',
            'alergias': 'Ninguna'
        },
    ]

    for pac_data in pacientes:
        usuario, user_created = User.objects.get_or_create(
            username=pac_data['username'],
            defaults={
                'first_name': pac_data['first_name'],
                'last_name': pac_data['last_name'],
                'email': pac_data['email'],
                'password': '!invalid-placeholder',
                'last_login': timezone.now(),
            }
        )
        
        # Si el usuario acaba de crearse, establecer la contraseña correctamente
        if user_created:
            usuario.set_password(pac_data['password'])
            usuario.save()

        paciente, created = Paciente.objects.get_or_create(
            usuario=usuario,
            defaults={
                'fecha_nacimiento': pac_data['fecha_nacimiento'],
                'telefono': pac_data['telefono'],
                'numero_seguro': pac_data['numero_seguro'],
                'alergias': pac_data['alergias'],
            }
        )
        
        status = "✅ Creado" if created else "⏭️ Ya existe"
        print(f"{status}: {usuario.first_name} {usuario.last_name} ({usuario.username})")


def crear_admin():
    """Crear usuario admin si no existe"""
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'email': 'admin@medicalreserva.com',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    
    if created:
        admin_user.set_password('admin1234')
        admin_user.save()
        print("✅ Creado: Admin (admin@medicalreserva.com)")
    else:
        print("⏭️ Admin ya existe")


if __name__ == '__main__':
    print("\n📊 Inicializando base de datos...\n")
    
    print("👨‍⚕️ Creando doctores:")
    crear_doctores()
    
    print("\n👥 Creando pacientes:")
    crear_pacientes()
    
    print("\n👑 Creando administrador:")
    crear_admin()
    
    print("\n✅ Base de datos inicializada correctamente!\n")
