from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Paciente, Doctor, Reserva


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)


class PacienteSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)
    usuario_id = serializers.IntegerField(write_only=True, required=False)
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Paciente
        fields = ('id', 'usuario', 'usuario_id', 'nombre_completo', 'fecha_nacimiento', 'telefono', 'direccion', 'numero_seguro', 'alergias')
        read_only_fields = ('id', 'usuario', 'nombre_completo')

    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username

    def create(self, validated_data):
        usuario_id = validated_data.pop('usuario_id', None)
        if usuario_id:
            validated_data['usuario_id'] = usuario_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('usuario_id', None)
        return super().update(instance, validated_data)


class DoctorSerializer(serializers.ModelSerializer):
    especialidad_display = serializers.CharField(source='get_especialidad_display', read_only=True)

    class Meta:
        model = Doctor
        fields = ('id', 'nombre', 'especialidad', 'especialidad_display', 'numero_cedula', 'telefono', 'email', 'disponible', 'experiencia_anos')
        read_only_fields = ('id', 'especialidad_display')


class ReservaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = ('id', 'paciente', 'doctor', 'fecha_hora', 'estado', 'notas', 'razon_consulta')
        read_only_fields = ('id',)

    def validate_fecha_hora(self, value):
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError('La fecha debe ser en el futuro.')
        return value


class ReservaReadSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='paciente.usuario.get_full_name', read_only=True)
    doctor_nombre = serializers.CharField(source='doctor.nombre', read_only=True)
    especialidad = serializers.CharField(source='doctor.get_especialidad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Reserva
        fields = ('id', 'paciente', 'paciente_nombre', 'doctor', 'doctor_nombre', 'especialidad', 'fecha_hora', 'estado', 'estado_display', 'razon_consulta', 'notas', 'creada_en', 'actualizada_en')
        read_only_fields = ('id', 'creada_en', 'actualizada_en')


class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = '__all__'
        read_only_fields = ('id', 'creada_en', 'actualizada_en')
