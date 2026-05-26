"""
Views for medicalreserva app.
"""
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse_lazy
from .models import Reserva, Paciente, Doctor
from .forms import DoctorForm, PacienteEditForm, ReservaForm, RegistroForm
from .tasks import enviar_correo_reserva
from datetime import datetime


def index(request):
    """Home page view."""
    if request.user.is_authenticated:
        # Si es un admin, redirige al panel de administración
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        # Si es un paciente autenticado, redirige al dashboard
        return redirect('dashboard_paciente')
    
    context = {
        'doctores_destacados': Doctor.objects.filter(disponible=True)[:6],
        'total_doctores': Doctor.objects.filter(disponible=True).count(),
        'total_pacientes': Paciente.objects.count(),
        'total_reservas': Reserva.objects.filter(estado='completada').count(),
    }
    return render(request, 'index.html', context)


@login_required
def dashboard_paciente(request):
    """Patient dashboard - lista de reservas del paciente."""
    # Si es un admin, redirige al panel de administración
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')
    
    try:
        paciente = request.user.paciente_profile
    except Paciente.DoesNotExist:
        # Si el usuario no es un paciente registrado, ir a una página de error o crear su perfil
        return render(request, 'paciente_profile_required.html')
    
    # Obtener las reservas del paciente
    todas_las_reservas = Reserva.objects.filter(paciente=paciente).order_by('-fecha_hora')
    
    # Separar reservas futuras y pasadas
    ahora = timezone.now()
    reservas_futuras = todas_las_reservas.filter(fecha_hora__gte=ahora)
    reservas_pasadas = todas_las_reservas.filter(fecha_hora__lt=ahora)
    
    context = {
        'paciente': paciente,
        'reservas_futuras': reservas_futuras,
        'reservas_pasadas': reservas_pasadas,
        'todas_las_reservas': todas_las_reservas,
        'total_reservas': todas_las_reservas.count(),
        'reservas_proximas': reservas_futuras.count(),
    }
    return render(request, 'dashboard_paciente.html', context)


@login_required
def detalle_reserva(request, reserva_id):
    """Detail view for a specific reservation."""
    try:
        paciente = request.user.paciente_profile
    except Paciente.DoesNotExist:
        return redirect('index')
    
    try:
        reserva = Reserva.objects.get(id=reserva_id, paciente=paciente)
    except Reserva.DoesNotExist:
        return render(request, '404.html', status=404)
    
    context = {
        'reserva': reserva,
        'paciente': paciente,
    }
    return render(request, 'detalle_reserva.html', context)


@login_required(login_url='login')
def crear_reserva(request):
    """
    Vista para crear una nueva reserva de forma manual,
    evitando conflictos con las validaciones del ReservaForm de admin.
    """
    # ====================================================================================
    # LOG CRÍTICO #1: CONFIRMAR QUE LA VISTA SE EJECUTA
    # ====================================================================================
    import sys
    import logging
    
    logger = logging.getLogger('django')
    
    print("\n" + "█"*100, file=sys.stderr)
    print(f"█ [CREAR_RESERVA] ¡¡¡ VISTA EJECUTADA !!! Método: {request.method}", file=sys.stderr)
    print(f"█ [CREAR_RESERVA] Ruta: {request.path}", file=sys.stderr)
    print(f"█ [CREAR_RESERVA] Usuario autenticado: {request.user.is_authenticated}", file=sys.stderr)
    print(f"█ [CREAR_RESERVA] Usuario: {request.user}", file=sys.stderr)
    print("█"*100, file=sys.stderr)
    
    logger.warning(f"[CREAR_RESERVA] VISTA EJECUTADA - Método: {request.method}, Usuario: {request.user}")
    
    # ====================================================================================
    # LOG CRÍTICO #2: OBTENER PACIENTE
    # ====================================================================================
    paciente = None
    try:
        paciente = request.user.paciente_profile
        print(f"█ [✓] Paciente ENCONTRADO: {paciente}", file=sys.stderr)
        logger.warning(f"[CREAR_RESERVA] Paciente encontrado: {paciente}")
    except Paciente.DoesNotExist as e:
        print(f"█ [✗✗✗] PACIENTE NO EXISTE - Redirigiendo a index", file=sys.stderr)
        print(f"█ Error: {e}", file=sys.stderr)
        logger.error(f"[CREAR_RESERVA] Paciente NO EXISTE para usuario: {request.user}")
        return redirect('index')
    except AttributeError as e:
        print(f"█ [✗✗✗] ATRIBUTO ERROR - Usuario podría no estar autenticado", file=sys.stderr)
        print(f"█ Error: {e}", file=sys.stderr)
        logger.error(f"[CREAR_RESERVA] AttributeError: {e}")
        return redirect('login')
    except Exception as e:
        print(f"█ [✗✗✗] ERROR DESCONOCIDO obteniendo paciente", file=sys.stderr)
        print(f"█ Error: {type(e).__name__}: {e}", file=sys.stderr)
        logger.error(f"[CREAR_RESERVA] Error desconocido: {type(e).__name__}: {e}")
        return redirect('index')
    
    # ====================================================================================
    # LOG CRÍTICO #3: OBTENER DOCTORES
    # ====================================================================================
    doctores = Doctor.objects.filter(disponible=True)
    print(f"█ [✓] Doctores disponibles: {doctores.count()}", file=sys.stderr)
    logger.warning(f"[CREAR_RESERVA] Doctores disponibles: {doctores.count()}")
    
    # ====================================================================================
    # PROCESAMIENTO DE POST
    # ====================================================================================
    if request.method == 'POST':
        print(f"\n█ [POST] ========== PROCESANDO FORMULARIO POST ==========", file=sys.stderr)
        print(f"█ [POST] POST data completo: {dict(request.POST)}", file=sys.stderr)
        logger.warning(f"[CREAR_RESERVA] POST data: {dict(request.POST)}")
        
        # Obtener valores
        doctor_id = request.POST.get('doctor_id', '').strip()
        fecha_hora_str = request.POST.get('fecha_hora', '').strip()
        razon_consulta = request.POST.get('razon_consulta', '').strip()
        
        # ====================================================================================
        # LOG CRÍTICO #4: MOSTRAR VALORES RECIBIDOS
        # ====================================================================================
        print(f"\n█ [VALORES RECIBIDOS]", file=sys.stderr)
        print(f"█   doctor_id='{doctor_id}' (len={len(doctor_id)}, vacío={not doctor_id})", file=sys.stderr)
        print(f"█   fecha_hora='{fecha_hora_str}' (len={len(fecha_hora_str)}, vacío={not fecha_hora_str})", file=sys.stderr)
        print(f"█   razon_consulta='{razon_consulta}' (len={len(razon_consulta)}, vacío={not razon_consulta})", file=sys.stderr)
        
        logger.warning(f"[CREAR_RESERVA] doctor_id='{doctor_id}', fecha_hora='{fecha_hora_str}', razon='{razon_consulta}'")
        
        # ====================================================================================
        # VALIDACIÓN #1: DOCTOR_ID
        # ====================================================================================
        if not doctor_id:
            print(f"█ [✗] VALIDACIÓN FALLIDA: doctor_id está vacío", file=sys.stderr)
            logger.error(f"[CREAR_RESERVA] Validación fallida: doctor_id vacío")
            return render(request, 'crear_reserva.html', {
                'error': 'Por favor selecciona un doctor.',
                'doctores': doctores,
                'especialidades': Doctor.SPECIALTIES,
            })
        print(f"█ [✓] doctor_id válido: {doctor_id}", file=sys.stderr)
        
        # ====================================================================================
        # VALIDACIÓN #2: FECHA_HORA
        # ====================================================================================
        if not fecha_hora_str:
            print(f"█ [✗] VALIDACIÓN FALLIDA: fecha_hora está vacío", file=sys.stderr)
            logger.error(f"[CREAR_RESERVA] Validación fallida: fecha_hora vacío")
            return render(request, 'crear_reserva.html', {
                'error': 'Por favor completa la fecha y hora.',
                'doctores': doctores,
                'especialidades': Doctor.SPECIALTIES,
            })
        print(f"█ [✓] fecha_hora válida: {fecha_hora_str}", file=sys.stderr)
        
        # ====================================================================================
        # VALIDACIÓN #3: RAZON_CONSULTA
        # ====================================================================================
        if not razon_consulta:
            print(f"█ [✗] VALIDACIÓN FALLIDA: razon_consulta está vacío", file=sys.stderr)
            logger.error(f"[CREAR_RESERVA] Validación fallida: razon_consulta vacío")
            return render(request, 'crear_reserva.html', {
                'error': 'Por favor ingresa la razón de la consulta.',
                'doctores': doctores,
                'especialidades': Doctor.SPECIALTIES,
            })
        print(f"█ [✓] razon_consulta válida: {razon_consulta}", file=sys.stderr)
        
        # ====================================================================================
        # PROCESAMIENTO DE FECHA
        # ====================================================================================
        try:
            print(f"\n█ [PARSING] Parseando fecha_hora: '{fecha_hora_str}'", file=sys.stderr)
            fecha_dt = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M')
            print(f"█ [✓] Parseado sin zona: {fecha_dt}", file=sys.stderr)
            
            fecha_dt = timezone.make_aware(fecha_dt)
            print(f"█ [✓] Convertido a timezone-aware: {fecha_dt}", file=sys.stderr)
            logger.warning(f"[CREAR_RESERVA] Fecha parseada: {fecha_dt}")
            
        except ValueError as ve:
            print(f"█ [✗✗✗] ERROR DE PARSING: {type(ve).__name__}: {ve}", file=sys.stderr)
            logger.error(f"[CREAR_RESERVA] ValueError al parsear: {ve}")
            return render(request, 'crear_reserva.html', {
                'error': f'Formato de fecha incorrecto. Recibido: "{fecha_hora_str}"',
                'doctores': doctores,
                'especialidades': Doctor.SPECIALTIES,
            })
        
        # ====================================================================================
        # OBTENER DOCTOR
        # ====================================================================================
        try:
            print(f"\n█ [DB] Buscando doctor: id={doctor_id}, disponible=True", file=sys.stderr)
            doctor = Doctor.objects.get(id=doctor_id, disponible=True)
            print(f"█ [✓] Doctor encontrado: {doctor}", file=sys.stderr)
            logger.warning(f"[CREAR_RESERVA] Doctor encontrado: {doctor}")
            
        except Doctor.DoesNotExist:
            print(f"█ [✗✗✗] DOCTOR NO ENCONTRADO: id={doctor_id}", file=sys.stderr)
            logger.error(f"[CREAR_RESERVA] Doctor NO ENCONTRADO: {doctor_id}")
            return render(request, 'crear_reserva.html', {
                'error': 'El doctor seleccionado no existe o no está disponible.',
                'doctores': doctores,
                'especialidades': Doctor.SPECIALTIES,
            })
        
        # ====================================================================================
        # VALIDAR DISPONIBILIDAD
        # ====================================================================================
        print(f"\n█ [DISPONIBILIDAD] Verificando conflictos...", file=sys.stderr)
        conflicto = Reserva.objects.filter(doctor=doctor, fecha_hora=fecha_dt)
        if conflicto.exists():
            print(f"█ [✗] CONFLICTO ENCONTRADO", file=sys.stderr)
            logger.warning(f"[CREAR_RESERVA] Conflicto de horario")
            return render(request, 'crear_reserva.html', {
                'error': 'El doctor NO está disponible en ese horario.',
                'doctores': doctores,
                'especialidades': Doctor.SPECIALTIES,
            })
        print(f"█ [✓] Horario disponible", file=sys.stderr)
        
        # ====================================================================================
        # VALIDAR FECHA EN FUTURO
        # ====================================================================================
        ahora = timezone.now()
        print(f"\n█ [FECHA FUTURA] Validando: {fecha_dt} > {ahora}", file=sys.stderr)
        if fecha_dt <= ahora:
            print(f"█ [✗] FECHA EN PASADO", file=sys.stderr)
            logger.warning(f"[CREAR_RESERVA] Fecha en pasado")
            return render(request, 'crear_reserva.html', {
                'error': 'La fecha debe ser en el futuro.',
                'doctores': doctores,
                'especialidades': Doctor.SPECIALTIES,
            })
        print(f"█ [✓] Fecha es futura", file=sys.stderr)
        
        # ====================================================================================
        # CREAR RESERVA
        # ====================================================================================
        try:
            print(f"\n█ [CREAR] Creando reserva...", file=sys.stderr)
            print(f"█   - paciente: {paciente}", file=sys.stderr)
            print(f"█   - doctor: {doctor}", file=sys.stderr)
            print(f"█   - fecha_hora: {fecha_dt}", file=sys.stderr)
            print(f"█   - razon_consulta: {razon_consulta}", file=sys.stderr)
            
            reserva = Reserva.objects.create(
                paciente=paciente,
                doctor=doctor,
                fecha_hora=fecha_dt,
                razon_consulta=razon_consulta,
                estado='pendiente'
            )
            print(f"█ [✓✓✓] RESERVA CREADA: {reserva} (ID: {reserva.id})", file=sys.stderr)
            logger.warning(f"[CREAR_RESERVA] ✓✓✓ RESERVA CREADA: {reserva.id}")
            
            # Enviar correo
            try:
                print(f"█ [EMAIL] Enviando correo...", file=sys.stderr)
                enviar_correo_reserva.delay(reserva.id)
                print(f"█ [✓] Correo enviado a Celery", file=sys.stderr)
            except Exception as email_error:
                print(f"█ [⚠] Error en correo (no crítico): {email_error}", file=sys.stderr)
                logger.warning(f"[CREAR_RESERVA] Error en correo: {email_error}")
            
            print(f"█ [REDIRECT] Redirigiendo a detalle_reserva id={reserva.id}", file=sys.stderr)
            return redirect('detalle_reserva', reserva_id=reserva.id)
            
        except Exception as create_error:
            print(f"█ [✗✗✗] ERROR AL CREAR: {type(create_error).__name__}: {create_error}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            logger.error(f"[CREAR_RESERVA] Error al crear: {create_error}", exc_info=True)
            return render(request, 'crear_reserva.html', {
                'error': f'Error: {str(create_error)}',
                'doctores': doctores,
                'especialidades': Doctor.SPECIALTIES,
            })
    
    # ====================================================================================
    # GET: MOSTRAR FORMULARIO
    # ====================================================================================
    print(f"\n█ [GET] Mostrando formulario vacío", file=sys.stderr)
    context = {
        'doctores': doctores,
        'paciente': paciente,
        'especialidades': Doctor.SPECIALTIES,
    }
    return render(request, 'crear_reserva.html', context)

@login_required
def cancelar_reserva(request, reserva_id):
    """Cancel a reservation."""
    try:
        paciente = request.user.paciente_profile
    except Paciente.DoesNotExist:
        return redirect('index')
    
    try:
        reserva = Reserva.objects.get(id=reserva_id, paciente=paciente)
        
        if reserva.estado == 'cancelada':
            return render(request, 'error.html', {'mensaje': 'Esta reserva ya fue cancelada.'})
        
        if reserva.fecha_hora < timezone.now():
            return render(request, 'error.html', {'mensaje': 'No puedes cancelar una reserva pasada.'})
        
        reserva.estado = 'cancelada'
        reserva.save()
        
        return redirect('dashboard_paciente')
    
    except Reserva.DoesNotExist:
        return render(request, '404.html', status=404)


def lista_doctores(request):
    """List all available doctors."""
    especialidad = request.GET.get('especialidad', '')
    
    doctores = Doctor.objects.filter(disponible=True)
    
    if especialidad:
        doctores = doctores.filter(especialidad=especialidad)
    
    context = {
        'doctores': doctores,
        'especialidades': Doctor.SPECIALTIES,
        'especialidad_seleccionada': especialidad,
    }
    return render(request, 'lista_doctores.html', context)


def detalle_doctor(request, doctor_id):
    """Doctor detail view."""
    try:
        doctor = Doctor.objects.get(id=doctor_id)
    except Doctor.DoesNotExist:
        return render(request, '404.html', status=404)
    
    # Obtener sus próximas reservas
    ahora = timezone.now()
    reservas_proximas = doctor.reservas.filter(
        fecha_hora__gte=ahora,
        estado__in=['pendiente', 'confirmada']
    ).order_by('fecha_hora')[:10]
    
    context = {
        'doctor': doctor,
        'reservas_proximas': reservas_proximas,
    }
    return render(request, 'detalle_doctor.html', context)


# ==================== ADMIN PERSONALIZADO ====================

@login_required
def admin_dashboard(request):
    """Panel de administración personalizado."""
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('index')
    
    context = {
        'total_doctores': Doctor.objects.count(),
        'total_pacientes': Paciente.objects.count(),
        'total_reservas': Reserva.objects.count(),
        'reservas_pendientes': Reserva.objects.filter(estado='pendiente').count(),
        'reservas_confirmadas': Reserva.objects.filter(estado='confirmada').count(),
        'reservas_completadas': Reserva.objects.filter(estado='completada').count(),
        'reservas_canceladas': Reserva.objects.filter(estado='cancelada').count(),
        'doctores_disponibles': Doctor.objects.filter(disponible=True).count(),
        'doctores_no_disponibles': Doctor.objects.filter(disponible=False).count(),
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
def admin_doctores(request):
    """Gestionar doctores."""
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('index')
    
    doctores = Doctor.objects.all().order_by('nombre')
    
    context = {
        'doctores': doctores,
        'total': doctores.count(),
    }
    return render(request, 'admin_doctores.html', context)


@login_required
def admin_pacientes(request):
    """Gestionar pacientes."""
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('index')
    
    pacientes = Paciente.objects.all().order_by('usuario__first_name')
    
    context = {
        'pacientes': pacientes,
        'total': pacientes.count(),
    }
    return render(request, 'admin_pacientes.html', context)


@login_required
def admin_reservas(request):
    """Gestionar reservas."""
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('index')
    
    estado_filter = request.GET.get('estado', '')
    reservas = Reserva.objects.all().order_by('-fecha_hora')
    
    if estado_filter:
        reservas = reservas.filter(estado=estado_filter)
    
    context = {
        'reservas': reservas,
        'total': reservas.count(),
        'estado_filter': estado_filter,
        'estados': ['pendiente', 'confirmada', 'completada', 'cancelada'],
    }
    return render(request, 'admin_reservas.html', context)


@login_required
def admin_reserva_confirmar(request, reserva_id):
    """Confirmar una reserva."""
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('index')
    
    try:
        reserva = Reserva.objects.get(id=reserva_id)
        reserva.estado = 'confirmada'
        reserva.save()
    except Reserva.DoesNotExist:
        pass
    
    return redirect('admin_reservas')


@login_required
def admin_reserva_completar(request, reserva_id):
    """Marcar una reserva como completada."""
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('index')
    
    try:
        reserva = Reserva.objects.get(id=reserva_id)
        reserva.estado = 'completada'
        reserva.save()
    except Reserva.DoesNotExist:
        pass
    
    return redirect('admin_reservas')


@login_required
def admin_reserva_cancelar(request, reserva_id):
    """Cancelar una reserva."""
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('index')
    
    try:
        reserva = Reserva.objects.get(id=reserva_id)
        reserva.estado = 'cancelada'
        reserva.save()
    except Reserva.DoesNotExist:
        pass
    
    return redirect('admin_reservas')


@login_required
def admin_doctor_toggle(request, doctor_id):
    """Activar/Desactivar disponibilidad de un doctor."""
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('index')
    
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        doctor.disponible = not doctor.disponible
        doctor.save()
    except Doctor.DoesNotExist:
        pass
    
    return redirect('admin_doctores')


# ==================== CBV CRUD OPERATIONS ====================

# ========== DOCTOR CRUD ==========

class DoctorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new doctor (Admin only)."""
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctor_form.html'
    success_url = reverse_lazy('admin_doctores')
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Crear'
        context['title'] = 'Crear Nuevo Doctor'
        return context


class DoctorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing doctor (Admin only)."""
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctor_form.html'
    success_url = reverse_lazy('admin_doctores')
    pk_url_kwarg = 'doctor_id'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Editar'
        context['title'] = f'Editar Doctor: {self.object.nombre}'
        return context


class DoctorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a doctor (Admin only)."""
    model = Doctor
    template_name = 'doctor_confirm_delete.html'
    success_url = reverse_lazy('admin_doctores')
    pk_url_kwarg = 'doctor_id'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


# ========== PATIENT CRUD ==========

class PacienteUpdateView(LoginRequiredMixin, UpdateView):
    """Update patient profile (Own profile only)."""
    model = Paciente
    form_class = PacienteEditForm
    template_name = 'paciente_form.html'
    success_url = reverse_lazy('dashboard_paciente')
    
    def get_object(self, queryset=None):
        return self.request.user.paciente_profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Perfil'
        return context


class PacienteDeleteView(LoginRequiredMixin, DeleteView):
    """Delete patient account (Own account only)."""
    model = Paciente
    template_name = 'paciente_confirm_delete.html'
    success_url = reverse_lazy('index')
    
    def get_object(self, queryset=None):
        return self.request.user.paciente_profile
    
    def delete(self, request, *args, **kwargs):
        """Delete patient and associated user account."""
        paciente = self.get_object()
        user = paciente.usuario
        response = super().delete(request, *args, **kwargs)
        user.delete()
        return response


# ========== ADMIN PATIENT MANAGEMENT ==========

class AdminPacienteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update patient profile (Admin only - can edit any patient)."""
    model = Paciente
    form_class = PacienteEditForm
    template_name = 'paciente_form.html'
    success_url = reverse_lazy('admin_pacientes')
    pk_url_kwarg = 'paciente_id'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar Paciente: {self.object.usuario.first_name} {self.object.usuario.last_name}'
        return context


class AdminPacienteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete patient account (Admin only - can delete any patient)."""
    model = Paciente
    template_name = 'paciente_confirm_delete.html'
    success_url = reverse_lazy('admin_pacientes')
    pk_url_kwarg = 'paciente_id'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def delete(self, request, *args, **kwargs):
        """Delete patient and associated user account."""
        paciente = self.get_object()
        user = paciente.usuario
        response = super().delete(request, *args, **kwargs)
        user.delete()
        return response


# ========== RESERVATION CRUD (Admin only) ==========

class ReservaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new reservation (Admin only)."""
    model = Reserva
    form_class = ReservaForm
    template_name = 'reserva_form.html'
    success_url = reverse_lazy('admin_reservas')
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Crear'
        context['title'] = 'Crear Nueva Reserva'
        return context


class ReservaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing reservation (Admin only)."""
    model = Reserva
    form_class = ReservaForm
    template_name = 'reserva_form.html'
    success_url = reverse_lazy('admin_reservas')
    pk_url_kwarg = 'reserva_id'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Editar'
        context['title'] = f'Editar Reserva: {self.object.id}'
        return context


class ReservaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a reservation (Admin only)."""
    model = Reserva
    template_name = 'reserva_confirm_delete.html'
    success_url = reverse_lazy('admin_reservas')
    pk_url_kwarg = 'reserva_id'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


# ========== REGISTRATION ==========

class RegistroView(CreateView):
    """User registration view with automatic patient profile creation and auto-login."""
    form_class = RegistroForm
    template_name = 'registro.html'
    success_url = reverse_lazy('dashboard_paciente')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registro de Paciente'
        return context
    
    def form_valid(self, form):
        """Save user (and associated Paciente profile via form.save()) and auto-login."""
        user = form.save()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return redirect(self.success_url)
