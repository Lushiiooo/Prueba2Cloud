"""
Comando personalizado para sembrar datos de prueba en la base de datos.
Uso: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Doctor, Paciente, Reserva
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Siembra datos de prueba en la base de datos (idempotente - no crea duplicados)'

    def handle(self, *args, **options):
        """
        Método principal que ejecuta el sembrado de datos.
        """
        self.stdout.write(self.style.WARNING('🔍 Verificando estado de la base de datos...'))

        # Verificar si ya existen doctores
        if Doctor.objects.exists():
            self.stdout.write(
                self.style.SUCCESS('✓ La base de datos ya contiene doctores. No se crearán duplicados.')
            )
            return

        self.stdout.write(self.style.WARNING('📝 Base de datos vacía. Iniciando sembrado de datos...'))

        # 1. Crear superusuario si no existe
        self._create_admin_user()

        # 2. Crear doctores de prueba
        self._create_test_doctors()

        # 3. Crear paciente de prueba
        self._create_test_patient()

        self.stdout.write(self.style.SUCCESS('✅ Sembrado de datos completado exitosamente.'))

    def _create_admin_user(self):
        """Crea un usuario administrador si no existe."""
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('ℹ️  Usuario admin ya existe. Omitiendo...'))
            return

        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@medicalreserva.com',
            password='admin123',
            first_name='Admin',
            last_name='Sistema'
        )
        self.stdout.write(
            self.style.SUCCESS(f'✓ Superusuario creado: {admin_user.username} (Contraseña: admin123)')
        )

    def _create_test_doctors(self):
        """Crea 3 doctores de prueba."""
        doctors_data = [
            {
                'nombre': 'Dr. Carlos Martínez López',
                'especialidad': 'cardiologia',
                'numero_cedula': 'CD-001-2024',
                'telefono': '+34 912 345 678',
                'email': 'carlos.martinez@medicalreserva.com',
                'disponible': True,
                'experiencia_anos': 15,
            },
            {
                'nombre': 'Dra. María González Ruiz',
                'especialidad': 'pediatria',
                'numero_cedula': 'CD-002-2024',
                'telefono': '+34 913 456 789',
                'email': 'maria.gonzalez@medicalreserva.com',
                'disponible': True,
                'experiencia_anos': 12,
            },
            {
                'nombre': 'Dr. Juan Rodríguez Torres',
                'especialidad': 'general',
                'numero_cedula': 'CD-003-2024',
                'telefono': '+34 914 567 890',
                'email': 'juan.rodriguez@medicalreserva.com',
                'disponible': True,
                'experiencia_anos': 20,
            },
        ]

        created_count = 0
        for doctor_data in doctors_data:
            # Verificar si el doctor ya existe por cédula
            if Doctor.objects.filter(numero_cedula=doctor_data['numero_cedula']).exists():
                self.stdout.write(self.style.WARNING(f"ℹ️  Doctor con cédula {doctor_data['numero_cedula']} ya existe."))
                continue

            doctor = Doctor.objects.create(**doctor_data)
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'✓ Doctor creado: {doctor.nombre} ({doctor.get_especialidad_display()})')
            )

        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'✓ Total de doctores creados: {created_count}'))

    def _create_test_patient(self):
        """Crea un paciente de prueba."""
        # Verificar si el usuario paciente de prueba ya existe
        if User.objects.filter(username='paciente_test').exists():
            self.stdout.write(self.style.WARNING('ℹ️  Usuario paciente_test ya existe. Omitiendo...'))
            return

        # Crear usuario paciente
        user = User.objects.create_user(
            username='paciente_test',
            email='paciente@medicalreserva.com',
            password='paciente123',
            first_name='Juan',
            last_name='Pérez García'
        )

        # Crear perfil de paciente
        paciente = Paciente.objects.create(
            usuario=user,
            fecha_nacimiento='1985-03-15',
            telefono='+34 915 678 901',
            direccion='Calle Principal 123, Apto 4B, Madrid, España',
            numero_seguro='1234567890ABC',
            alergias='Penicilina, Mariscos'
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Paciente de prueba creado: {paciente.usuario.get_full_name()} (Usuario: paciente_test, Contraseña: paciente123)'
            )
        )

        # Crear una reserva de prueba
        self._create_test_reservation(paciente)

    def _create_test_reservation(self, paciente):
        """Crea una reserva de prueba para el paciente."""
        # Obtener el primer doctor creado
        doctor = Doctor.objects.first()
        if not doctor:
            self.stdout.write(self.style.WARNING('⚠️  No hay doctores disponibles para crear reserva.'))
            return

        # Crear una cita para mañana a las 14:00
        fecha_reserva = timezone.now() + timedelta(days=1)
        fecha_reserva = fecha_reserva.replace(hour=14, minute=0, second=0, microsecond=0)

        try:
            reserva = Reserva.objects.create(
                paciente=paciente,
                doctor=doctor,
                fecha_hora=fecha_reserva,
                estado='confirmada',
                razon_consulta='Revisión médica general',
                notas='Primera cita de prueba'
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Reserva de prueba creada: {paciente.usuario.first_name} con {doctor.nombre} el {fecha_reserva.strftime("%d/%m/%Y %H:%M")}'
                )
            )
        except Exception as e:
            # Si la cita ya existe (unique_together), no es un error grave
            self.stdout.write(self.style.WARNING(f'ℹ️  No se pudo crear la reserva: {str(e)}'))
