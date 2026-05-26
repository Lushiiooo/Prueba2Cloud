# 🚀 Guía Práctica - Replicación de Componentes

## Tabla de Contenidos
1. [Quick Start (5 minutos)](#quick-start-5-minutos)
2. [Replicar Componentes HTML](#replicar-componentes-html)
3. [Código de Ejemplo](#código-de-ejemplo)
4. [Snippets CSS Reutilizables](#snippets-css-reutilizables)
5. [Testing & Validación](#testing--validación)

---

## Quick Start (5 minutos)

### Paso 1: Clonar y Configurar

```bash
# Clonar proyecto
git clone <repository-url>
cd Prueba2_Cloud

# Crear entorno
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Configurar Credenciales

```bash
# Crear .env en la raíz del proyecto
cat > .env << EOF
SECRET_KEY=django-insecure-dev-key
DEBUG=True
DB_NAME=medical_reserva
DB_USER=medical_user
DB_PASSWORD=password123
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EOF
```

### Paso 3: Base de Datos

```bash
# Crear BD PostgreSQL
psql -U postgres -c "CREATE DATABASE medical_reserva;"
psql -U postgres -c "CREATE USER medical_user WITH PASSWORD 'password123';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE medical_reserva TO medical_user;"

# Migraciones
python manage.py migrate

# Crear superuser
python manage.py createsuperuser

# Cargar datos de ejemplo
python manage.py seed_data
```

### Paso 4: Ejecutar Servidor

```bash
# Terminal 1
python manage.py runserver

# Terminal 2 (Celery - opcional en desarrollo)
celery -A medicalreserva worker -l info

# Acceder a:
# http://localhost:8000/
# http://localhost:8000/admin/
```

✅ **¡Listo! La app está corriendo**

---

## Replicar Componentes HTML

### 1. Navbar (Reusable)

```html
<!-- templates/components/navbar.html -->
<nav class="bg-white shadow-md sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
            <!-- Logo -->
            <a href="{% url 'index' %}" class="flex items-center space-x-2">
                <i class="fas fa-heartbeat text-2xl text-medical-blue"></i>
                <span class="navbar-brand">Medical Reserva</span>
            </a>
            
            <!-- Links Centrales -->
            <div class="hidden md:flex space-x-8">
                <a href="{% url 'lista_doctores' %}" class="text-gray-700 hover:text-medical-blue transition font-medium">
                    Doctores
                </a>
                {% if user.is_authenticated %}
                    <a href="{% url 'dashboard_paciente' %}" class="text-gray-700 hover:text-medical-blue transition font-medium">
                        Mi Dashboard
                    </a>
                    {% if user.is_staff %}
                    <a href="{% url 'admin_dashboard' %}" class="text-gray-700 hover:text-medical-blue transition font-medium">
                        Admin
                    </a>
                    {% endif %}
                {% endif %}
            </div>
            
            <!-- Botones Auth -->
            <div class="flex items-center space-x-4">
                {% if user.is_authenticated %}
                    <span class="text-gray-700 hidden md:inline">{{ user.first_name|default:user.username }}</span>
                    <a href="{% url 'logout' %}" class="btn-primary text-white px-4 py-2 rounded-lg transition">
                        Logout
                    </a>
                {% else %}
                    <a href="{% url 'login' %}" class="text-medical-blue font-medium hover:text-medical-dark transition">
                        Login
                    </a>
                    <a href="{% url 'registro' %}" class="btn-primary text-white px-4 py-2 rounded-lg transition">
                        Registro
                    </a>
                {% endif %}
            </div>
        </div>
    </div>
</nav>
```

### 2. Stats Cards (Reusable)

```html
<!-- templates/components/stats_card.html -->
<div class="bg-white rounded-xl shadow-md p-6 border-l-4 {{ border_color }}">
    <div class="flex items-center justify-between">
        <div>
            <p class="text-gray-600 text-sm">{{ title }}</p>
            <p class="text-3xl font-bold text-medical-dark">{{ value }}</p>
            {% if subtitle %}
            <p class="text-xs text-gray-500 mt-1">{{ subtitle }}</p>
            {% endif %}
        </div>
        <i class="fas {{ icon }} text-4xl {{ icon_color }} opacity-50"></i>
    </div>
</div>

<!-- Usar componente -->
{% include 'components/stats_card.html' with title='Total Reservas' value=total_reservas icon='fa-calendar' icon_color='text-medical-light-blue' border_color='border-medical-blue' %}
```

### 3. Doctor Card (Reusable)

```html
<!-- templates/components/doctor_card.html -->
<div class="card-hover bg-white rounded-xl overflow-hidden shadow-md hover:shadow-xl transition">
    <!-- Header con Gradient -->
    <div class="gradient-header text-white p-8 text-center">
        <div class="w-24 h-24 rounded-full bg-white bg-opacity-20 flex items-center justify-center mx-auto mb-4 text-5xl">
            <i class="fas fa-user-md"></i>
        </div>
        <h3 class="text-2xl font-bold">Dr. {{ doctor.nombre }}</h3>
        <p class="text-white text-opacity-90 text-lg">{{ doctor.get_especialidad_display }}</p>
    </div>
    
    <!-- Información -->
    <div class="p-8 space-y-4">
        <!-- Cédula -->
        <div class="flex items-start justify-between pb-4 border-b border-gray-200">
            <span class="text-gray-600 flex items-center space-x-2">
                <i class="fas fa-certificate text-medical-teal"></i>
                <span>Cédula</span>
            </span>
            <span class="font-semibold text-gray-900">{{ doctor.numero_cedula }}</span>
        </div>
        
        <!-- Experiencia -->
        <div class="flex items-start justify-between pb-4 border-b border-gray-200">
            <span class="text-gray-600 flex items-center space-x-2">
                <i class="fas fa-briefcase text-medical-teal"></i>
                <span>Experiencia</span>
            </span>
            <span class="font-semibold text-gray-900">{{ doctor.experiencia_anos }} años</span>
        </div>
        
        <!-- Email -->
        <div class="flex items-start justify-between pb-4 border-b border-gray-200">
            <span class="text-gray-600 flex items-center space-x-2">
                <i class="fas fa-envelope text-medical-teal"></i>
                <span>Email</span>
            </span>
            <span class="font-semibold text-gray-900 text-right truncate">{{ doctor.email }}</span>
        </div>
        
        <!-- Botón -->
        <a href="{% url 'detalle_doctor' doctor.id %}" class="btn-teal text-white w-full text-center py-3 rounded-lg transition block mt-6">
            <i class="fas fa-calendar-check mr-2"></i>Agendar Cita
        </a>
    </div>
</div>
```

### 4. Modal/Dialog (Reusable)

```html
<!-- templates/components/modal.html -->
<div id="{{ modal_id }}" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <!-- Header -->
        <div class="bg-medical-blue text-white px-6 py-4 rounded-t-lg flex justify-between items-center">
            <h2 class="text-lg font-bold">{{ title }}</h2>
            <button onclick="closeModal('{{ modal_id }}')" class="text-white hover:opacity-75">
                <i class="fas fa-times"></i>
            </button>
        </div>
        
        <!-- Content -->
        <div class="px-6 py-4">
            {{ content }}
        </div>
        
        <!-- Footer -->
        <div class="bg-gray-100 px-6 py-3 rounded-b-lg flex justify-end gap-3">
            <button onclick="closeModal('{{ modal_id }}')" class="px-4 py-2 text-gray-700 border rounded-lg hover:bg-gray-50">
                Cancelar
            </button>
            <button class="btn-primary text-white px-4 py-2 rounded-lg">
                {{ action_button_text }}
            </button>
        </div>
    </div>
</div>

<script>
function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}
function openModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}
</script>
```

### 5. Reserva Card (Con Estados)

```html
<!-- templates/components/reserva_card.html -->
<div class="bg-medical-light-blue border-l-4 border-medical-teal rounded-lg p-6 card-hover">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Doctor -->
        <div>
            <p class="text-xs uppercase tracking-wide text-gray-600 font-semibold mb-1">Doctor</p>
            <p class="text-lg font-bold text-medical-dark">Dr. {{ reserva.doctor.nombre }}</p>
            <p class="text-sm text-gray-600">{{ reserva.doctor.get_especialidad_display }}</p>
        </div>
        
        <!-- Fecha -->
        <div>
            <p class="text-xs uppercase tracking-wide text-gray-600 font-semibold mb-1">Fecha y Hora</p>
            <p class="text-lg font-bold text-medical-dark">
                <i class="fas fa-calendar mr-2"></i>{{ reserva.fecha_hora|date:"d/m/Y" }}
            </p>
            <p class="text-sm font-semibold text-medical-teal">
                <i class="fas fa-clock mr-1"></i>{{ reserva.fecha_hora|time:"H:i" }}
            </p>
        </div>
        
        <!-- Razón -->
        <div>
            <p class="text-xs uppercase tracking-wide text-gray-600 font-semibold mb-1">Razón</p>
            <p class="text-sm text-gray-900">{{ reserva.razon_consulta }}</p>
        </div>
        
        <!-- Estado y Acciones -->
        <div class="flex flex-col justify-between">
            <div>
                <p class="text-xs uppercase tracking-wide text-gray-600 font-semibold mb-2">Estado</p>
                <span class="inline-block px-3 py-1 rounded-full text-xs font-semibold 
                    {% if reserva.estado == 'confirmada' %}bg-green-100 text-green-800
                    {% elif reserva.estado == 'pendiente' %}bg-yellow-100 text-yellow-800
                    {% elif reserva.estado == 'completada' %}bg-gray-100 text-gray-800
                    {% elif reserva.estado == 'cancelada' %}bg-red-100 text-red-800
                    {% endif %}">
                    {{ reserva.get_estado_display }}
                </span>
            </div>
            <div class="flex gap-2 mt-2">
                <a href="{% url 'detalle_reserva' reserva.id %}" class="text-xs bg-medical-blue text-white px-3 py-2 rounded transition hover:shadow-md">
                    <i class="fas fa-eye mr-1"></i>Ver
                </a>
                {% if reserva.es_proxima and reserva.estado != 'cancelada' %}
                <a href="{% url 'cancelar_reserva' reserva.id %}" class="text-xs bg-red-500 text-white px-3 py-2 rounded transition hover:shadow-md">
                    <i class="fas fa-times mr-1"></i>Cancelar
                </a>
                {% endif %}
            </div>
        </div>
    </div>
</div>
```

---

## Código de Ejemplo

### Crear un Nuevo Modelo

```python
# app/models.py - Agregar nuevo modelo

from django.db import models
from django.contrib.auth.models import User

class Historial(models.Model):
    """Historial de atención médica"""
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE, related_name='historiales')
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='historiales')
    reserva = models.OneToOneField('Reserva', on_delete=models.SET_NULL, null=True, related_name='historial')
    
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    medicamentos = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Historial'
        verbose_name_plural = 'Historiales'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Historial {self.id} - {self.paciente.usuario.get_full_name()}"
```

### Crear un Formulario

```python
# app/forms.py - Agregar nuevo formulario

from django import forms
from .models import Historial

class HistorialForm(forms.ModelForm):
    class Meta:
        model = Historial
        fields = ['diagnostico', 'tratamiento', 'medicamentos']
        widgets = {
            'diagnostico': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-medical-blue',
                'placeholder': 'Describe el diagnóstico',
                'rows': 4
            }),
            'tratamiento': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-medical-blue',
                'placeholder': 'Describe el tratamiento',
                'rows': 4
            }),
            'medicamentos': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-medical-blue',
                'placeholder': 'Medicamentos recomendados',
                'rows': 3
            }),
        }
```

### Crear un Serializer

```python
# app/serializers.py - Agregar nuevo serializer

from rest_framework import serializers
from .models import Historial

class HistorialSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='paciente.usuario.get_full_name', read_only=True)
    doctor_nombre = serializers.CharField(source='doctor.nombre', read_only=True)
    
    class Meta:
        model = Historial
        fields = ('id', 'paciente', 'paciente_nombre', 'doctor', 'doctor_nombre', 'diagnostico', 'tratamiento', 'medicamentos', 'fecha_creacion')
        read_only_fields = ('id', 'fecha_creacion')
```

### Crear una Vista (Class-Based)

```python
# app/views.py - Agregar nueva vista

from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Historial
from .forms import HistorialForm

class HistorialCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Crear historial para una reserva completada"""
    model = Historial
    form_class = HistorialForm
    template_name = 'historial_form.html'
    success_url = reverse_lazy('admin_reservas')
    
    def test_func(self):
        """Solo staff puede crear historiales"""
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Reserva
        context['reserva'] = Reserva.objects.get(id=self.kwargs.get('reserva_id'))
        return context
    
    def form_valid(self, form):
        from .models import Reserva
        reserva = Reserva.objects.get(id=self.kwargs.get('reserva_id'))
        form.instance.reserva = reserva
        form.instance.paciente = reserva.paciente
        form.instance.doctor = reserva.doctor
        return super().form_valid(form)
```

### Crear un ViewSet de API

```python
# app/api_views.py - Agregar nuevo viewset

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Historial
from .serializers import HistorialSerializer

class HistorialViewSet(viewsets.ModelViewSet):
    queryset = Historial.objects.all()
    serializer_class = HistorialSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Historial.objects.all()
        try:
            paciente = user.paciente_profile
            return Historial.objects.filter(paciente=paciente)
        except:
            return Historial.objects.none()
    
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
```

### Registrar en URLs

```python
# app/urls.py - Agregar nuevas URLs

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

router = DefaultRouter()
router.register(r'historiales', api_views.HistorialViewSet, basename='historial')

urlpatterns = [
    # Rutas existentes...
    path('api/', include(router.urls)),
    
    # Nuevas rutas web
    path('historial/crear/<int:reserva_id>/', views.HistorialCreateView.as_view(), name='historial_create'),
]
```

---

## Snippets CSS Reutilizables

### Botones Personalizados

```css
/* Botones Personalizados */
.btn-primary {
    @apply bg-medical-blue text-white font-semibold px-6 py-3 rounded-lg 
           transition hover:bg-opacity-90 active:scale-95;
    box-shadow: 0 4px 6px rgba(15, 58, 125, 0.1);
}

.btn-primary:hover {
    @apply shadow-lg;
    transform: translateY(-2px);
}

.btn-secondary {
    @apply bg-white text-gray-700 border-2 border-gray-300 font-semibold px-6 py-3 
           rounded-lg transition hover:border-medical-blue hover:text-medical-blue;
}

.btn-teal {
    @apply bg-medical-teal text-white font-semibold px-6 py-3 rounded-lg 
           transition hover:bg-opacity-90;
}

.btn-danger {
    @apply bg-red-500 text-white font-semibold px-6 py-3 rounded-lg 
           transition hover:bg-red-600;
}

.btn-success {
    @apply bg-green-500 text-white font-semibold px-6 py-3 rounded-lg 
           transition hover:bg-green-600;
}

.btn-small {
    @apply text-xs px-3 py-2;
}

.btn-large {
    @apply text-lg px-8 py-4;
}

/* Botones Deshabilitados */
.btn-disabled {
    @apply opacity-50 cursor-not-allowed pointer-events-none;
}

/* Estados de Botones */
.btn:disabled {
    @apply opacity-50 cursor-not-allowed;
}

.btn:active {
    @apply scale-95;
}
```

### Cards y Contenedores

```css
/* Cards */
.card {
    @apply bg-white rounded-xl shadow-md p-6 transition;
}

.card:hover {
    @apply shadow-lg;
}

.card-header {
    @apply border-b border-gray-200 pb-4 mb-4;
}

.card-footer {
    @apply border-t border-gray-200 pt-4 mt-4;
}

/* Cards con bordes coloreados */
.card-blue {
    @apply card border-l-4 border-medical-blue;
}

.card-teal {
    @apply card border-l-4 border-medical-teal;
}

.card-green {
    @apply card border-l-4 border-green-500;
}

.card-red {
    @apply card border-l-4 border-red-500;
}

.card-yellow {
    @apply card border-l-4 border-yellow-400;
}

/* Grid responsivo */
.grid-responsive {
    @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6;
}
```

### Efectos y Transiciones

```css
/* Transiciones */
.transition-all {
    @apply transition-all duration-300 ease-in-out;
}

.hover-lift {
    @apply hover:shadow-lg hover:-translate-y-1 transition-all;
}

.hover-scale {
    @apply hover:scale-105 transition-transform;
}

/* Loading Spinner */
.spinner {
    @apply inline-block w-4 h-4 border-2 border-gray-300 border-t-medical-blue rounded-full animate-spin;
}

/* Gradientes */
.gradient-header {
    @apply bg-gradient-to-r from-medical-blue to-medical-teal text-white;
}

.gradient-bg {
    @apply bg-gradient-to-br from-medical-light-blue to-white;
}

/* Animaciones */
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.animate-slideIn {
    animation: slideIn 0.3s ease-in-out;
}
```

### Formularios

```css
/* Input fields */
.input {
    @apply w-full px-4 py-2 border border-gray-300 rounded-lg 
           focus:outline-none focus:ring-2 focus:ring-medical-blue 
           focus:border-transparent transition;
}

.input:disabled {
    @apply bg-gray-100 cursor-not-allowed;
}

/* Selects */
.select {
    @apply w-full px-4 py-2 border-2 border-gray-300 rounded-lg 
           focus:outline-none focus:border-medical-blue transition
           cursor-pointer;
}

/* Textarea */
.textarea {
    @apply w-full px-4 py-2 border border-gray-300 rounded-lg 
           focus:outline-none focus:ring-2 focus:ring-medical-blue 
           focus:border-transparent resize-vertical;
}

/* Labels */
.label {
    @apply block text-sm font-medium text-gray-700 mb-2;
}

/* Error messages */
.error-message {
    @apply text-red-500 text-sm mt-1 flex items-center;
}

.error-message::before {
    content: "⚠ ";
    @apply mr-1;
}

/* Success messages */
.success-message {
    @apply text-green-500 text-sm mt-1 flex items-center;
}

.success-message::before {
    content: "✓ ";
    @apply mr-1;
}
```

### Responsive Utilities

```css
/* Hide/Show basado en viewport */
@media (max-width: 768px) {
    .hide-mobile {
        @apply hidden;
    }
}

@media (min-width: 768px) {
    .show-desktop {
        @apply block;
    }
}

/* Padding responsivo */
.px-safe {
    @apply px-4 md:px-6 lg:px-8;
}

.py-safe {
    @apply py-4 md:py-6 lg:py-8;
}

/* Max width containers */
.container-wide {
    @apply max-w-7xl mx-auto;
}

.container-normal {
    @apply max-w-4xl mx-auto;
}

.container-narrow {
    @apply max-w-2xl mx-auto;
}
```

---

## Testing & Validación

### Pruebas Unitarias

```python
# app/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Paciente, Doctor, Reserva
from django.utils import timezone

class PacienteTestCase(TestCase):
    def setUp(self):
        """Preparar datos de prueba"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123'
        )
        self.paciente = self.user.paciente_profile
    
    def test_paciente_creation(self):
        """Verificar que se crea perfil de paciente"""
        self.assertEqual(self.paciente.usuario, self.user)
        self.assertTrue(hasattr(self.user, 'paciente_profile'))
    
    def test_paciente_str(self):
        """Verificar representación en string"""
        expected = f"Paciente: {self.user.get_full_name() or self.user.username}"
        self.assertEqual(str(self.paciente), expected)

class DoctorTestCase(TestCase):
    def setUp(self):
        """Preparar datos de prueba"""
        self.doctor = Doctor.objects.create(
            nombre='Dr. Juan García',
            especialidad='cardiologia',
            numero_cedula='12345678',
            email='juan@ejemplo.com',
            experiencia_anos=10
        )
    
    def test_doctor_creation(self):
        """Verificar creación de doctor"""
        self.assertEqual(self.doctor.nombre, 'Dr. Juan García')
        self.assertTrue(self.doctor.disponible)
    
    def test_doctor_str(self):
        """Verificar representación en string"""
        expected = f"Dr. {self.doctor.nombre} - Cardiología"
        self.assertEqual(str(self.doctor), expected)

class ReservaTestCase(TestCase):
    def setUp(self):
        """Preparar datos de prueba"""
        self.user = User.objects.create_user(
            username='paciente',
            password='pass123'
        )
        self.doctor = Doctor.objects.create(
            nombre='Dr. Test',
            especialidad='general',
            numero_cedula='99999999',
            email='test@doc.com'
        )
        self.reserva = Reserva.objects.create(
            paciente=self.user.paciente_profile,
            doctor=self.doctor,
            fecha_hora=timezone.now() + timezone.timedelta(days=1),
            razon_consulta='Checkup general'
        )
    
    def test_reserva_creation(self):
        """Verificar creación de reserva"""
        self.assertEqual(self.reserva.estado, 'pendiente')
        self.assertTrue(self.reserva.es_proxima)
    
    def test_unique_doctor_fecha(self):
        """Verificar que no se permiten dos reservas en la misma hora"""
        with self.assertRaises(Exception):
            Reserva.objects.create(
                paciente=self.user.paciente_profile,
                doctor=self.doctor,
                fecha_hora=self.reserva.fecha_hora,
                razon_consulta='Otra razón'
            )
```

### Pruebas de API

```python
# app/tests_api.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Doctor

class DoctorAPITestCase(APITestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            nombre='Dr. API Test',
            especialidad='pediatria',
            numero_cedula='11111111',
            email='api@test.com'
        )
    
    def test_get_doctors_list(self):
        """Prueba GET /api/doctores/"""
        response = self.client.get('/api/doctores/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_doctor_detail(self):
        """Prueba GET /api/doctores/{id}/"""
        response = self.client.get(f'/api/doctores/{self.doctor.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Dr. API Test')
    
    def test_create_doctor_unauthorized(self):
        """Prueba que no se puede crear sin autenticación"""
        data = {
            'nombre': 'Dr. Nuevo',
            'especialidad': 'oncologia',
            'numero_cedula': '22222222',
            'email': 'nuevo@test.com'
        }
        response = self.client.post('/api/doctores/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

### Validación Manual

```bash
# 1. Probar login
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# 2. Guardar el token
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# 3. Probar endpoint autenticado
curl -X GET http://localhost:8000/api/pacientes/mi_perfil/ \
  -H "Authorization: Bearer $TOKEN"

# 4. Crear reserva (POST)
curl -X POST http://localhost:8000/api/reservas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor": 1,
    "fecha_hora": "2026-06-20T14:00:00Z",
    "razon_consulta": "Dolor de cabeza"
  }'

# 5. Ver próximas reservas
curl -X GET http://localhost:8000/api/reservas/proximas/ \
  -H "Authorization: Bearer $TOKEN"
```

---

**Última actualización:** Mayo 2026
