from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Paciente, Doctor, Reserva
from .serializers import (
    PacienteSerializer,
    DoctorSerializer,
    ReservaSerializer,
    ReservaReadSerializer,
    ReservaWriteSerializer,
)


class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['usuario__first_name', 'usuario__last_name', 'usuario__email']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Paciente.objects.all()
        return Paciente.objects.filter(usuario=user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mi_perfil(self, request):
        try:
            paciente = Paciente.objects.get(usuario=request.user)
            serializer = self.get_serializer(paciente)
            return Response(serializer.data)
        except Paciente.DoesNotExist:
            return Response({'detail': 'No tiene perfil de paciente.'}, status=status.HTTP_404_NOT_FOUND)


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'especialidad', 'email']
    ordering_fields = ['nombre', 'experiencia_anos', 'especialidad']
    ordering = ['nombre']

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        especialidad = request.query_params.get('especialidad', None)
        queryset = self.get_queryset().filter(disponible=True)
        if especialidad:
            queryset = queryset.filter(especialidad=especialidad)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def reservas(self, request, pk=None):
        doctor = self.get_object()
        reservas = doctor.reservas.all()
        serializer = ReservaReadSerializer(reservas, many=True)
        return Response(serializer.data)


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-fecha_hora']

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return ReservaWriteSerializer
        return ReservaReadSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Reserva.objects.all()
        try:
            paciente = Paciente.objects.get(usuario=user)
            return Reserva.objects.filter(paciente=paciente)
        except Paciente.DoesNotExist:
            return Reserva.objects.none()

    def perform_create(self, serializer):
        paciente = get_object_or_404(Paciente, usuario=self.request.user)
        serializer.save(paciente=paciente)

    @action(detail=False, methods=['get'])
    def proximas(self, request):
        now = timezone.now()
        queryset = self.get_queryset().filter(
            fecha_hora__gte=now,
            estado__in=['pendiente', 'confirmada']
        ).order_by('fecha_hora')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        reserva = self.get_object()
        if reserva.estado == 'cancelada':
            return Response(
                {'detail': 'La reserva ya fue cancelada.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if reserva.fecha_hora < timezone.now():
            return Response(
                {'detail': 'No se pueden cancelar reservas pasadas.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        reserva.estado = 'cancelada'
        reserva.save()
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def confirmar(self, request, pk=None):
        reserva = self.get_object()
        if reserva.estado == 'confirmada':
            return Response(
                {'detail': 'La reserva ya está confirmada.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        reserva.estado = 'confirmada'
        reserva.save()
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def completar(self, request, pk=None):
        reserva = self.get_object()
        reserva.estado = 'completada'
        reserva.save()
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)

