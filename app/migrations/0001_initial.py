# Generated migration

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150, verbose_name='Nombre Completo')),
                ('especialidad', models.CharField(choices=[('cardiologia', 'Cardiología'), ('pediatria', 'Pediatría'), ('dermatologia', 'Dermatología'), ('neurologia', 'Neurología'), ('oftalmologia', 'Oftalmología'), ('ortopedia', 'Ortopedia'), ('psiquiatria', 'Psiquiatría'), ('oncologia', 'Oncología'), ('general', 'Medicina General')], max_length=50, verbose_name='Especialidad')),
                ('numero_cedula', models.CharField(max_length=50, unique=True, verbose_name='Número de Cédula')),
                ('telefono', models.CharField(blank=True, max_length=20, null=True, verbose_name='Teléfono')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('disponible', models.BooleanField(default=True, verbose_name='Disponible')),
                ('experiencia_anos', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(70)], verbose_name='Años de Experiencia')),
            ],
            options={
                'verbose_name': 'Doctor',
                'verbose_name_plural': 'Doctores',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora', models.DateTimeField(verbose_name='Fecha y Hora de la Reserva')),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('completada', 'Completada'), ('cancelada', 'Cancelada')], default='pendiente', max_length=20, verbose_name='Estado')),
                ('notas', models.TextField(blank=True, null=True, verbose_name='Notas')),
                ('razon_consulta', models.CharField(max_length=255, verbose_name='Razón de la Consulta')),
                ('creada_en', models.DateTimeField(auto_now_add=True, verbose_name='Creada en')),
                ('actualizada_en', models.DateTimeField(auto_now=True, verbose_name='Actualizada en')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservas', to='app.doctor', verbose_name='Doctor')),
            ],
            options={
                'verbose_name': 'Reserva',
                'verbose_name_plural': 'Reservas',
                'ordering': ['-fecha_hora'],
            },
        ),
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_nacimiento', models.DateField(verbose_name='Fecha de Nacimiento')),
                ('telefono', models.CharField(blank=True, max_length=20, null=True, verbose_name='Teléfono')),
                ('direccion', models.TextField(blank=True, null=True, verbose_name='Dirección')),
                ('numero_seguro', models.CharField(blank=True, max_length=50, null=True, verbose_name='Número de Seguro')),
                ('alergias', models.TextField(blank=True, null=True, verbose_name='Alergias')),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='paciente_profile', to='auth.user')),
            ],
            options={
                'verbose_name': 'Paciente',
                'verbose_name_plural': 'Pacientes',
                'ordering': ['usuario__first_name', 'usuario__last_name'],
            },
        ),
        migrations.AddField(
            model_name='reserva',
            name='paciente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservas', to='app.paciente', verbose_name='Paciente'),
        ),
        migrations.AlterUniqueTogether(
            name='reserva',
            unique_together={('doctor', 'fecha_hora')},
        ),
    ]
