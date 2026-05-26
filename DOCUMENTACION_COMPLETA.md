# 📋 Documentación Completa - Medical Reserva Platform

## Tabla de Contenidos
1. [Descripción General](#descripción-general)
2. [Arquitectura Técnica](#arquitectura-técnica)
3. [Modelo de Base de Datos](#modelo-de-base-de-datos)
4. [Sistema CRUD Completo](#sistema-crud-completo)
5. [Diseño & Interfaz de Usuario](#diseño--interfaz-de-usuario)
6. [API REST Endpoints](#api-rest-endpoints)
7. [Configuración de Conexiones](#configuración-de-conexiones)
8. [Autenticación & Permisos](#autenticación--permisos)
9. [Flujo de la Aplicación](#flujo-de-la-aplicación)
10. [Instrucciones de Replicación](#instrucciones-de-replicación)

---

## Descripción General

### Propósito
Medical Reserva es una plataforma web de reservas médicas que permite a los pacientes reservar citas con doctores especializados. Incluye un sistema completo de gestión para administradores.

### Características Principales
- ✅ Registro y autenticación de usuarios
- ✅ Perfil de pacientes con información médica
- ✅ Catálogo de doctores por especialidad
- ✅ Sistema de reservas con disponibilidad
- ✅ Dashboard de pacientes
- ✅ Panel administrativo completo
- ✅ API REST con JWT para integraciones
- ✅ Notificaciones por email (Celery + Redis)

### Stack Tecnológico
```
Backend:      Django 5.0.6 + Django REST Framework 3.14.0
Base de Datos: PostgreSQL 
Cache/Tasks:  Redis 5.0.1 + Celery 5.3.4
Frontend:     HTML5 + Tailwind CSS + Font Awesome
Autenticación: JWT (djangorestframework-simplejwt)
Servidor:     Gunicorn + Docker
```

---

## Arquitectura Técnica

### Estructura de Carpetas Recomendada
```
project-root/
├── medicalreserva/           # Configuración principal del proyecto
│   ├── __init__.py
│   ├── settings.py           # Configuración de Django
│   ├── urls.py               # URLs principales
│   ├── wsgi.py               # WSGI para producción
│   └── celery.py             # Configuración de Celery
│
├── app/                       # Aplicación principal
│   ├── migrations/           # Migraciones de BD
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py  # Cargar datos de prueba
│   ├── __init__.py
│   ├── admin.py              # Admin de Django
│   ├── apps.py
│   ├── models.py             # Modelos de base de datos
│   ├── views.py              # Vistas Web (HTML)
│   ├── api_views.py          # Vistas API (JSON)
│   ├── urls.py               # URLs de la app
│   ├── forms.py              # Formularios Django
│   ├── serializers.py        # Serializers DRF
│   ├── signals.py            # Señales de Django
│   └── tasks.py              # Tareas Celery
│
├── templates/                # Plantillas HTML
│   ├── base.html             # Template base
│   ├── index.html            # Página inicio
│   ├── login.html            # Login
│   ├── registro.html         # Registro
│   ├── dashboard_paciente.html
│   ├── lista_doctores.html
│   ├── detalle_doctor.html
│   ├── crear_reserva.html
│   ├── detalle_reserva.html
│   ├── admin_dashboard.html
│   ├── admin_doctores.html
│   ├── admin_pacientes.html
│   ├── admin_reservas.html
│   └── error.html
│
├── staticfiles/              # Archivos estáticos
├── requirements.txt          # Dependencias Python
├── manage.py                 # CLI de Django
├── Dockerfile               # Configuración Docker
├── docker-compose.yml       # Orquestación de servicios
└── entrypoint.sh            # Script de inicio
```

---

## Modelo de Base de Datos

### Descripción General
La BD utiliza relaciones One-to-One y One-to-Many para conectar usuarios, pacientes, doctores y reservas.

### Tablas y Relaciones

#### 1. **Tabla: auth_user** (Django Built-in)
```sql
-- Tabla de autenticación de Django
id                  INT PRIMARY KEY
username           VARCHAR(150) UNIQUE
password           VARCHAR(128)
email              VARCHAR(254)
first_name         VARCHAR(150)
last_name          VARCHAR(150)
is_active          BOOLEAN
is_staff           BOOLEAN
is_superuser       BOOLEAN
last_login         DATETIME
date_joined        DATETIME
```

#### 2. **Tabla: app_paciente**
```sql
CREATE TABLE app_paciente (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    usuario_id          INT NOT NULL UNIQUE,
    fecha_nacimiento    DATE NOT NULL,
    telefono            VARCHAR(20),
    direccion           TEXT,
    numero_seguro       VARCHAR(50),
    alergias            TEXT,
    FOREIGN KEY (usuario_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- Índices
CREATE INDEX idx_paciente_usuario ON app_paciente(usuario_id);
```

#### 3. **Tabla: app_doctor**
```sql
CREATE TABLE app_doctor (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    nombre              VARCHAR(150) NOT NULL,
    especialidad        VARCHAR(50) NOT NULL,
    numero_cedula       VARCHAR(50) UNIQUE NOT NULL,
    telefono            VARCHAR(20),
    email               VARCHAR(254) NOT NULL,
    disponible          BOOLEAN DEFAULT TRUE,
    experiencia_anos    INT CHECK (experiencia_anos >= 0 AND experiencia_anos <= 70),
    created_at          DATETIME AUTO_TIMESTAMP,
    updated_at          DATETIME AUTO_UPDATE TIMESTAMP
);

-- Índices
CREATE INDEX idx_doctor_especialidad ON app_doctor(especialidad);
CREATE INDEX idx_doctor_cedula ON app_doctor(numero_cedula);
CREATE INDEX idx_doctor_disponible ON app_doctor(disponible);
```

#### 4. **Tabla: app_reserva**
```sql
CREATE TABLE app_reserva (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    paciente_id         BIGINT NOT NULL,
    doctor_id           BIGINT NOT NULL,
    fecha_hora          DATETIME NOT NULL,
    estado              VARCHAR(20) DEFAULT 'pendiente',
    razon_consulta      VARCHAR(255) NOT NULL,
    notas               TEXT,
    creada_en           DATETIME AUTO_TIMESTAMP,
    actualizada_en      DATETIME AUTO_UPDATE TIMESTAMP,
    FOREIGN KEY (paciente_id) REFERENCES app_paciente(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES app_doctor(id) ON DELETE CASCADE,
    UNIQUE KEY unique_doctor_fecha (doctor_id, fecha_hora)
);

-- Índices
CREATE INDEX idx_reserva_paciente ON app_reserva(paciente_id);
CREATE INDEX idx_reserva_doctor ON app_reserva(doctor_id);
CREATE INDEX idx_reserva_fecha_hora ON app_reserva(fecha_hora);
CREATE INDEX idx_reserva_estado ON app_reserva(estado);
```

### Relaciones
```
auth_user
    ├─── (1:1) ──→ app_paciente
    └─── (1:N) ──→ auth_group

app_paciente
    └─── (1:N) ──→ app_reserva

app_doctor
    └─── (1:N) ──→ app_reserva

app_reserva
    ├─── (N:1) ──→ app_paciente
    └─── (N:1) ──→ app_doctor
```

### Estados de Reserva
```python
STATUS_CHOICES = (
    ('pendiente', 'Pendiente'),      # Recién creada
    ('confirmada', 'Confirmada'),    # Confirmada por admin
    ('completada', 'Completada'),    # Consulta realizada
    ('cancelada', 'Cancelada'),      # Cancelada por usuario o admin
)
```

### Especialidades Disponibles
```python
SPECIALTIES = (
    ('cardiologia', 'Cardiología'),
    ('pediatria', 'Pediatría'),
    ('dermatologia', 'Dermatología'),
    ('neurologia', 'Neurología'),
    ('oftalmologia', 'Oftalmología'),
    ('ortopedia', 'Ortopedia'),
    ('psiquiatria', 'Psiquiatría'),
    ('oncologia', 'Oncología'),
    ('general', 'Medicina General'),
)
```

---

## Sistema CRUD Completo

### 1. CRUD de Doctores

#### CREATE
```python
# Views.py - DoctorCreateView
class DoctorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctor_form.html'
    success_url = reverse_lazy('admin_doctores')
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

# URL: /admin-doctores/crear/
# Form Fields: nombre, especialidad, numero_cedula, telefono, email, disponible, experiencia_anos
```

#### READ
```python
# API Endpoint - GET
GET /api/doctores/                      # Listar todos
GET /api/doctores/{id}/                 # Detalles
GET /api/doctores/disponibles/          # Solo disponibles
GET /api/doctores/{id}/reservas/        # Reservas de un doctor

# View - lista_doctores (con filtro por especialidad)
GET /doctores/
GET /doctores/?especialidad=cardiologia
```

#### UPDATE
```python
# Views.py - DoctorUpdateView
class DoctorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctor_form.html'
    success_url = reverse_lazy('admin_doctores')
    
    def test_func(self):
        return self.request.user.is_staff

# URL: /admin-doctores/{id}/editar/
# API: PATCH /api/doctores/{id}/
```

#### DELETE
```python
# Views.py - DoctorDeleteView
class DoctorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Doctor
    template_name = 'doctor_confirm_delete.html'
    success_url = reverse_lazy('admin_doctores')
    
    def test_func(self):
        return self.request.user.is_staff

# URL: /admin-doctores/{id}/eliminar/
# API: DELETE /api/doctores/{id}/
```

#### TOGGLE Disponibilidad
```python
@staff_required
def admin_doctor_toggle(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.disponible = not doctor.disponible
    doctor.save()
    return redirect('admin_doctores')

# URL: /admin-doctor/{id}/toggle/
```

---

### 2. CRUD de Pacientes

#### CREATE
```python
# Registration via Django Auth
class RegistroView(CreateView):
    form_class = RegistroForm
    template_name = 'registro.html'
    success_url = reverse_lazy('dashboard_paciente')
    
    def form_valid(self, form):
        user = form.save()
        # Auto-create Paciente profile via signals
        login(self.request, user)
        return super().form_valid(form)

# URL: /registro/
```

#### READ
```python
# API
GET /api/pacientes/                     # Admin only
GET /api/pacientes/mi_perfil/           # Perfil del usuario actual

# View
dashboard_paciente - muestra info del paciente actual
```

#### UPDATE
```python
# Views.py - PacienteUpdateView
class PacienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Paciente
    form_class = PacienteEditForm
    template_name = 'paciente_form.html'
    success_url = reverse_lazy('dashboard_paciente')
    
    def get_object(self):
        return self.request.user.paciente_profile

# URL: /paciente/editar/
# API: PATCH /api/pacientes/{id}/
```

#### DELETE
```python
# Views.py - PacienteDeleteView
class PacienteDeleteView(LoginRequiredMixin, DeleteView):
    model = Paciente
    template_name = 'paciente_confirm_delete.html'
    success_url = reverse_lazy('index')
    
    def get_object(self):
        return self.request.user.paciente_profile

# URL: /paciente/eliminar/
# API: DELETE /api/pacientes/{id}/
```

---

### 3. CRUD de Reservas

#### CREATE
```python
# Views.py
def crear_reserva(request):
    # Obtiene doctor_id, fecha_hora, razon_consulta del formulario
    # Valida que no exista reserva en la misma fecha/hora
    # Crea la reserva y dispara tarea Celery para enviar email
    
# API
POST /api/reservas/
{
    "doctor": 1,
    "fecha_hora": "2026-06-15T10:00:00Z",
    "razon_consulta": "Dolor de cabeza",
    "notas": "Opcional"
}

# URL: /crear-reserva/
```

#### READ
```python
# Views
GET /dashboard/                         # Todas las reservas del paciente
GET /reserva/{id}/                      # Detalles de una reserva

# API
GET /api/reservas/                      # Listar
GET /api/reservas/{id}/                 # Detalles
GET /api/reservas/proximas/             # Solo próximas del usuario

# Admin
/admin-reservas/                        # Listar todas las reservas
```

#### UPDATE
```python
# Views.py - ReservaUpdateView
class ReservaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reserva_form.html'
    success_url = reverse_lazy('admin_reservas')
    
    def test_func(self):
        return self.request.user.is_staff

# URL: /admin-reservas/{id}/editar/
# API: PATCH /api/reservas/{id}/
```

#### DELETE
```python
# Views.py - ReservaDeleteView
class ReservaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Reserva
    template_name = 'reserva_confirm_delete.html'
    success_url = reverse_lazy('admin_reservas')
    
    def test_func(self):
        return self.request.user.is_staff

# URL: /admin-reservas/{id}/eliminar/
# API: DELETE /api/reservas/{id}/
```

#### Estados
```python
# Confirmar Reserva (Admin)
POST /api/reservas/{id}/confirmar/
URL: /admin-reserva/{id}/confirmar/

# Completar Reserva (Admin)
POST /api/reservas/{id}/completar/
URL: /admin-reserva/{id}/completar/

# Cancelar Reserva (Usuario/Admin)
POST /api/reservas/{id}/cancelar/
URL: /cancelar-reserva/{id}/
```

---

## Diseño & Interfaz de Usuario

### 🎨 Paleta de Colores

| Uso | Color | Hex | RGB | Tailwind |
|-----|-------|-----|-----|----------|
| Primario | Azul Médico | `#0f3a7d` | `15, 58, 125` | `medical-blue` |
| Secundario | Teal Médico | `#00a896` | `0, 168, 150` | `medical-teal` |
| Fondo Claro | Azul Claro | `#e3f2fd` | `227, 242, 253` | `medical-light-blue` |
| Fondo Gris | Gris Claro | `#f5f7fa` | `245, 247, 250` | `medical-gray` |
| Oscuro | Gris Oscuro | `#1a202c` | `26, 32, 44` | `medical-dark` |
| Éxito | Verde | `#10b981` | `16, 185, 129` | `green-500` |
| Advertencia | Amarillo | `#f59e0b` | `245, 158, 11` | `yellow-400` |
| Peligro | Rojo | `#ef4444` | `239, 68, 68` | `red-500` |

### CSS Personalizado

```css
/* Colores Personalizados Tailwind */
colors: {
    'medical-blue': '#0f3a7d',
    'medical-light-blue': '#e3f2fd',
    'medical-teal': '#00a896',
    'medical-gray': '#f5f7fa',
    'medical-dark': '#1a202c',
}

/* Botones */
.btn-primary {
    background-color: #0f3a7d;
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.btn-primary:hover {
    background-color: #0a2856;
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(15, 58, 125, 0.2);
}

.btn-teal {
    background-color: #00a896;
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
}

.btn-teal:hover {
    background-color: #008577;
}

/* Cards */
.card-hover {
    transition: all 0.3s ease;
}

.card-hover:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

/* Gradientes */
.gradient-header {
    background: linear-gradient(135deg, #0f3a7d 0%, #00a896 100%);
    color: white;
}
```

### 🎯 Componentes UI

#### Navbar
```html
<!-- Estilos -->
- Background: Blanco (#ffffff)
- Shadow: md
- Posición: Sticky top-0
- Height: 64px (h-16)
- Border-bottom: 1px solid #e5e7eb

<!-- Elementos -->
- Logo/Brand: font-bold text-xl text-medical-blue
- Links: text-gray-700 hover:text-medical-blue
- Auth Buttons: btn-primary, btn-secondary
```

#### Botones

| Tipo | Clase | Estilo | Caso de Uso |
|------|-------|--------|------------|
| Primario | `.btn-primary` | Azul #0f3a7d | Acciones principales (Agendar, Guardar) |
| Secundario | `.btn-secondary` | Blanco con borde | Acciones secundarias |
| Teal | `.btn-teal` | Teal #00a896 | Acciones confirmadas |
| Danger | `.btn-danger` | Rojo #ef4444 | Cancelar, Eliminar |
| Success | `.btn-success` | Verde #10b981 | Completado, Confirmado |
| Info | `.btn-info` | Azul Claro | Ver detalles |

#### Cards
```html
<!-- Estructura base -->
<div class="bg-white rounded-xl shadow-md p-6 card-hover">
    <div class="border-l-4 border-medical-blue">
        <!-- Contenido -->
    </div>
</div>

<!-- Variantes -->
- Borde izquierdo: medical-blue, medical-teal, green-500, red-500
- Shadow: md (por defecto), lg (hover)
```

#### Formularios
```html
<!-- Input estándar -->
<input 
    class="w-full px-4 py-2 border border-gray-300 rounded-lg 
           focus:outline-none focus:ring-2 focus:ring-medical-blue"
    type="text"
    placeholder="Placeholder"
/>

<!-- Select -->
<select 
    class="w-full px-4 py-2 border-2 border-gray-300 rounded-lg 
           focus:outline-none focus:border-medical-blue transition"
>
    <option>Opción 1</option>
</select>

<!-- Checkbox -->
<input 
    type="checkbox"
    class="w-4 h-4 text-blue-500 rounded focus:ring-2 focus:ring-blue-500"
/>

<!-- Textarea -->
<textarea 
    class="w-full px-4 py-2 border border-gray-300 rounded-lg 
           focus:outline-none focus:ring-2 focus:ring-medical-blue"
    placeholder="Mensaje..."
></textarea>
```

#### Badges/Estados
```html
<!-- Estado Pendiente -->
<span class="inline-block px-3 py-1 rounded-full text-xs font-semibold 
             bg-yellow-100 text-yellow-800">
    Pendiente
</span>

<!-- Estado Confirmada -->
<span class="inline-block px-3 py-1 rounded-full text-xs font-semibold 
             bg-green-100 text-green-800">
    Confirmada
</span>

<!-- Estado Cancelada -->
<span class="inline-block px-3 py-1 rounded-full text-xs font-semibold 
             bg-red-100 text-red-800">
    Cancelada
</span>
```

### 📐 Tipografía

```css
Font Family: Inter (Google Fonts)
Font Weights: 300, 400, 500, 600, 700

Tamaños:
- Títulos H1: 2.25rem (36px) - font-bold
- Títulos H2: 1.875rem (30px) - font-bold
- Títulos H3: 1.5rem (24px) - font-bold
- Subtítulos: 1.125rem (18px) - font-semibold
- Body Regular: 1rem (16px) - font-normal
- Small: 0.875rem (14px) - font-normal
- Extra Small: 0.75rem (12px) - font-semibold uppercase
```

### 🎬 Animaciones

```css
/* Transiciones */
transition: all 0.3s ease
transition: transform 0.3s ease
transition: box-shadow 0.3s ease

/* Hover Effects */
hover:translate-y[-2px]          /* Elevar 2px */
hover:shadow-lg                   /* Aumentar sombra */
hover:text-medical-blue           /* Cambiar color */

/* Focus Effects */
focus:outline-none
focus:ring-2
focus:ring-medical-blue
```

---

## API REST Endpoints

### 🔐 Autenticación

#### Obtener Token JWT
```
POST /api/token/
Content-Type: application/json

{
    "username": "usuario@ejemplo.com",
    "password": "contraseña"
}

Response:
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Refrescar Token
```
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "token_de_refresco"
}

Response:
{
    "access": "nuevo_token_de_acceso"
}
```

### 👨‍⚕️ Endpoints de Doctores

```
# Listar todos los doctores
GET /api/doctores/
Query Params:
  - search: nombre, especialidad o email
  - ordering: nombre, experiencia_anos, especialidad
  - limit: número de resultados

# Obtener detalles de un doctor
GET /api/doctores/{id}/

# Crear doctor (Admin only)
POST /api/doctores/
Content-Type: application/json
{
    "nombre": "Dr. Juan Pérez",
    "especialidad": "cardiologia",
    "numero_cedula": "12345678",
    "telefono": "+34 XXX XXX XXX",
    "email": "juan@ejemplo.com",
    "disponible": true,
    "experiencia_anos": 15
}

# Actualizar doctor (Admin only)
PATCH /api/doctores/{id}/
PUT /api/doctores/{id}/
{
    "disponible": false
}

# Eliminar doctor (Admin only)
DELETE /api/doctores/{id}/

# Obtener doctores disponibles
GET /api/doctores/disponibles/
Query Params:
  - especialidad: cardiologia, pediatria, etc.

# Obtener reservas de un doctor
GET /api/doctores/{id}/reservas/
```

### 👥 Endpoints de Pacientes

```
# Listar pacientes (Admin only)
GET /api/pacientes/

# Obtener perfil del usuario actual
GET /api/pacientes/mi_perfil/
Requires: JWT Token (Authenticated)

# Obtener detalles de un paciente
GET /api/pacientes/{id}/

# Actualizar perfil de paciente
PATCH /api/pacientes/{id}/
PATCH /api/pacientes/mi_perfil/
{
    "fecha_nacimiento": "1990-05-15",
    "telefono": "+34 XXX XXX XXX",
    "direccion": "Calle Principal 123",
    "numero_seguro": "123456789",
    "alergias": "Penicilina"
}

# Eliminar perfil de paciente
DELETE /api/pacientes/{id}/
```

### 📅 Endpoints de Reservas

```
# Listar reservas del usuario autenticado
GET /api/reservas/

# Obtener detalles de una reserva
GET /api/reservas/{id}/

# Crear nueva reserva
POST /api/reservas/
Content-Type: application/json
{
    "doctor": 1,
    "fecha_hora": "2026-06-15T10:00:00Z",
    "razon_consulta": "Dolor de cabeza intenso",
    "notas": "Notas adicionales (opcional)"
}

# Actualizar reserva (Admin only)
PATCH /api/reservas/{id}/
{
    "estado": "confirmada",
    "notas": "Nuevas notas"
}

# Confirmar reserva (Admin only)
POST /api/reservas/{id}/confirmar/

# Completar reserva (Admin only)
POST /api/reservas/{id}/completar/

# Cancelar reserva (Usuario/Admin)
POST /api/reservas/{id}/cancelar/

# Obtener próximas citas
GET /api/reservas/proximas/

# Eliminar reserva (Admin only)
DELETE /api/reservas/{id}/
```

### Códigos de Estado HTTP

| Código | Significado | Caso |
|--------|-------------|------|
| `200` | OK | GET exitoso, actualización exitosa |
| `201` | Created | POST exitoso, recurso creado |
| `204` | No Content | DELETE exitoso |
| `400` | Bad Request | Datos inválidos |
| `401` | Unauthorized | Token inválido o ausente |
| `403` | Forbidden | Sin permisos suficientes |
| `404` | Not Found | Recurso no encontrado |
| `409` | Conflict | Conflicto (ej: doctor ya tiene reserva esa hora) |
| `500` | Server Error | Error interno del servidor |

---

## Configuración de Conexiones

### 🗄️ Configuración de Base de Datos

#### PostgreSQL Local
```python
# medicalreserva/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'medical_reserva',
        'USER': 'medical_user',
        'PASSWORD': 'secure_password_change_me',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### PostgreSQL en AWS RDS
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}
```

#### Archivo .env (variables de entorno)
```ini
# Base de Datos
DB_ENGINE=django.db.backends.postgresql
DB_NAME=medical_reserva
DB_USER=medical_user
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True

# Email (Celery)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Redis
REDIS_URL=redis://localhost:6379

# AWS (opcional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1
```

### 🔌 Configuración de Redis

#### Para Celery
```python
# medicalreserva/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicalreserva.settings')

app = Celery('medicalreserva')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# medicalreserva/settings.py
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
```

### 📧 Configuración de Email (Celery)

```python
# app/tasks.py

from celery import shared_task
from django.core.mail import send_mail

@shared_task
def enviar_correo_reserva(reserva_id):
    from .models import Reserva
    reserva = Reserva.objects.get(id=reserva_id)
    
    subject = f'Reserva Confirmada - Dr. {reserva.doctor.nombre}'
    message = f"""
    Estimado/a {reserva.paciente.usuario.first_name},
    
    Tu reserva ha sido creada exitosamente.
    
    Doctor: Dr. {reserva.doctor.nombre}
    Especialidad: {reserva.doctor.get_especialidad_display()}
    Fecha y Hora: {reserva.fecha_hora}
    Razón: {reserva.razon_consulta}
    
    Estado: {reserva.get_estado_display()}
    """
    
    send_mail(
        subject,
        message,
        'noreply@medicalreserva.com',
        [reserva.paciente.usuario.email],
        fail_silently=False,
    )
```

### 📦 Docker Compose

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: medical_reserva
      POSTGRES_USER: medical_user
      POSTGRES_PASSWORD: secure_password_change_me
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: gunicorn medicalreserva.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  celery:
    build: .
    command: celery -A medicalreserva worker -l info
    volumes:
      - .:/app
    environment:
      - DEBUG=True
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

---

## Autenticación & Permisos

### 🔐 Tipos de Usuarios

| Tipo | Permisos | Acceso |
|------|----------|--------|
| **Anónimo** | Ver doctores, index, login, registro | `/`, `/login/`, `/registro/`, `/doctores/` |
| **Paciente** | Ver reservas, crear reservas, editar perfil | `/dashboard/`, `/crear-reserva/`, `/reserva/{id}/` |
| **Admin/Staff** | Gestionar doctores, pacientes, reservas | `/admin-dashboard/`, `/admin-doctores/`, etc. |
| **Superuser** | Acceso total a Django Admin | `/admin/` |

### 🔑 Mecanismos de Autenticación

#### Session-Based (Web)
```python
# login_required decorator
@login_required
def dashboard_paciente(request):
    paciente = request.user.paciente_profile
    ...

# LoginRequiredMixin (Class-based views)
class DoctorCreateView(LoginRequiredMixin, CreateView):
    ...
```

#### JWT Token-Based (API)
```python
# Rest framework permission classes
permission_classes = [IsAuthenticated]
permission_classes = [IsAdminUser]
permission_classes = [AllowAny]

# Header requerido
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 🚫 Permisos Granulares

```python
# Staff Required
class UserPassesTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

# Paciente Only
def test_func(self):
    return hasattr(self.request.user, 'paciente_profile')

# Admin Only
permission_classes = [IsAdminUser]
```

### 📋 Señales para Auto-crear Perfil

```python
# app/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Paciente

@receiver(post_save, sender=User)
def crear_paciente_profile(sender, instance, created, **kwargs):
    if created and not instance.is_staff:
        Paciente.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_paciente_profile(sender, instance, **kwargs):
    if hasattr(instance, 'paciente_profile'):
        instance.paciente_profile.save()
```

---

## Flujo de la Aplicación

### 1️⃣ Flujo de Registro

```
Usuario Anónimo
    ↓
Hace clic en "Registro"
    ↓
GET /registro/
    ↓ (Completa formulario)
POST /registro/
    ↓
Valida datos
    ↓
Crea User en auth_user
    ↓ (Signal triggered)
Auto-crea Paciente
    ↓
Login automático
    ↓
Redirecciona a /dashboard/
```

### 2️⃣ Flujo de Crear Reserva

```
Usuario Paciente
    ↓
GET /crear-reserva/
    ↓
Selecciona doctor
Selecciona fecha/hora
Ingresa razón de consulta
    ↓
POST /crear-reserva/
    ↓
Valida datos:
  - Doctor existe y disponible
  - Fecha es futura
  - No existe reserva en esa fecha/hora
    ↓
Crea Reserva con estado='pendiente'
    ↓ (Celery task)
Envía email de confirmación
    ↓
Redirecciona a /dashboard/
```

### 3️⃣ Flujo de Administración

```
Admin (Staff)
    ↓
GET /admin-dashboard/
    ↓ (Opciones)
├─ /admin-doctores/
│  ├─ Crear doctor
│  ├─ Editar doctor
│  ├─ Toggle disponibilidad
│  └─ Eliminar doctor
├─ /admin-pacientes/
│  ├─ Listar pacientes
│  ├─ Editar perfil
│  └─ Eliminar paciente
└─ /admin-reservas/
   ├─ Listar todas
   ├─ Crear reserva
   ├─ Confirmar
   ├─ Completar
   ├─ Cancelar
   └─ Eliminar
```

### 4️⃣ Flujo de Estados de Reserva

```
Crear Reserva
    ↓
Estado: PENDIENTE (amarillo)
    ↓
Admin Confirma
    ↓
Estado: CONFIRMADA (verde)
    ↓ (Usuario asiste)
Admin Completa
    ↓
Estado: COMPLETADA (gris)
    
     O
    
Usuario Cancela / Admin Cancela
    ↓
Estado: CANCELADA (rojo)
```

---

## Instrucciones de Replicación

### 📋 Pre-requisitos
- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- Git
- Docker & Docker Compose (opcional)

### 🚀 Instalación Paso a Paso

#### 1. Clonar el proyecto
```bash
git clone <repository-url>
cd Prueba2_Cloud
```

#### 2. Crear entorno virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 4. Crear archivo .env
```ini
SECRET_KEY=django-insecure-your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=medical_reserva
DB_USER=medical_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

REDIS_URL=redis://localhost:6379
```

#### 5. Configurar PostgreSQL
```bash
# Crear base de datos
psql -U postgres
CREATE DATABASE medical_reserva;
CREATE USER medical_user WITH PASSWORD 'your_secure_password';
ALTER ROLE medical_user SET client_encoding TO 'utf8';
ALTER ROLE medical_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE medical_user SET default_transaction_deferrable TO on;
ALTER ROLE medical_user SET default_transaction_deferrable TO on;
ALTER ROLE medical_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE medical_reserva TO medical_user;
\q
```

#### 6. Ejecutar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 7. Crear superuser
```bash
python manage.py createsuperuser
# Ingresa: email, password, confirm password
```

#### 8. Cargar datos de prueba (seed)
```bash
python manage.py seed_data
```

#### 9. Recolectar archivos estáticos
```bash
python manage.py collectstatic --noinput
```

#### 10. Ejecutar servidor de desarrollo
```bash
# Terminal 1 - Django
python manage.py runserver

# Terminal 2 - Celery Worker
celery -A medicalreserva worker -l info

# Terminal 3 - Celery Beat (optional, para tareas programadas)
celery -A medicalreserva beat -l info
```

#### 11. Acceder a la aplicación
```
Web: http://localhost:8000
Admin: http://localhost:8000/admin/
API: http://localhost:8000/api/
```

### 🐳 Instalación con Docker

```bash
# Construir imágenes
docker-compose build

# Ejecutar servicios
docker-compose up -d

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superuser
docker-compose exec web python manage.py createsuperuser

# Cargar datos de prueba
docker-compose exec web python manage.py seed_data

# Ver logs
docker-compose logs -f web
```

### 📊 Estructura de Datos Inicial (Seed)

```python
# Doctores de ejemplo
- Dr. Carlos López (Cardiología, 20 años experiencia)
- Dr. María González (Pediatría, 15 años experiencia)
- Dr. Juan Rodríguez (Dermatología, 10 años experiencia)
- etc.

# Usuarios de prueba
- admin@ejemplo.com (Admin/Staff)
- paciente@ejemplo.com (Paciente)
```

### ✅ Checklist de Verificación

- [ ] BD PostgreSQL funcionando
- [ ] Redis funcionando
- [ ] Migraciones ejecutadas
- [ ] Superuser creado
- [ ] Datos de prueba cargados
- [ ] Servidor Django corriendo (puerto 8000)
- [ ] Celery worker corriendo
- [ ] Login funcionando
- [ ] Crear reserva funciona
- [ ] API endpoints accesibles
- [ ] Emails enviándose (Celery)

---

## 🔧 Troubleshooting

### Error: "psycopg2 connection failed"
```bash
# Verificar PostgreSQL está corriendo
# Windows
psql -U postgres

# Verificar credenciales en .env
```

### Error: "Redis connection refused"
```bash
# Iniciar Redis
redis-server

# En Windows con WSL:
wsl -d <distribution> redis-server
```

### Migraciones no aplican
```bash
# Eliminar migraciones problemáticas y recrear
python manage.py makemigrations --empty app --name fix_schema
python manage.py migrate
```

### Tokens JWT inválidos
```bash
# Regenerar secret key
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## 📞 Contacto & Soporte

Para consultas técnicas o soporte:
- Email: soporte@medicalreserva.com
- Issues: GitHub repository
- Documentación: Este documento

---

**Última actualización:** Mayo 2026  
**Versión:** 1.0  
**Licencia:** MIT
