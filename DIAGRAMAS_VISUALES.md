# 🎯 Guía Visual - Medical Reserva Platform

## Diagrama General del Sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MEDICAL RESERVA PLATFORM                         │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   FRONTEND       │         │   BACKEND        │         │   BASE DE DATOS  │
│  (HTML+Tailwind) │◄───────►│   (Django 5.0)   │◄───────►│  (PostgreSQL)    │
└──────────────────┘         └──────────────────┘         └──────────────────┘
       ↑                             ↑
       │                             │
       │                             ├─────────────┬──────────────┐
       │                             │             │              │
       └─────────────────────────────┘         ┌────────┐    ┌─────────┐
                                               │ Redis  │    │ Celery  │
                                               │(Cache) │    │(Tasks)  │
                                               └────────┘    └─────────┘
```

## Arquitectura de Capas

```
┌────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                       │
│  (Templates HTML, Tailwind CSS, Font Awesome Icons)       │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│                     VIEWS LAYER                            │
│  ├─ Function-Based Views (Páginas web)                    │
│  ├─ Class-Based Views (CRUD)                              │
│  └─ API ViewSets (REST endpoints)                         │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│                  BUSINESS LOGIC LAYER                      │
│  ├─ Serializers (Validación de datos)                     │
│  ├─ Forms (Validación de formularios)                     │
│  └─ Tasks (Procesos asincronos con Celery)                │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│                    MODELS LAYER                            │
│  ├─ Paciente                                               │
│  ├─ Doctor                                                 │
│  ├─ Reserva                                                │
│  └─ User (Django Auth)                                     │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│                  DATABASE LAYER                            │
│  PostgreSQL 15.x                                           │
└────────────────────────────────────────────────────────────┘
```

## Modelo Entidad-Relación (ER)

```
                    ┌─────────────────┐
                    │   auth_user     │
                    └─────────────────┘
                           │ 1:1
                           │
                    ┌──────▼──────────┐
                    │ app_paciente    │
                    ├─────────────────┤
                    │ id              │
                    │ usuario_id (FK) │
                    │ fecha_nacimiento│
                    │ telefono        │
                    │ direccion       │
                    │ numero_seguro   │
                    │ alergias        │
                    └─────────────────┘
                           │ 1:N
                           │
        ┌──────────────────┘
        │
        │                  ┌─────────────────┐
        │                  │   app_doctor    │
        │                  ├─────────────────┤
        │                  │ id              │
        │                  │ nombre          │
        │                  │ especialidad    │
        │                  │ numero_cedula   │
        │                  │ telefono        │
        │                  │ email           │
        │                  │ disponible      │
        │                  │ experiencia_anos│
        │                  └─────────────────┘
        │                           │ 1:N
        │                           │
        │              ┌────────────┘
        │              │
        │       ┌──────▼──────────────┐
        └──────►│   app_reserva       │
                ├─────────────────────┤
                │ id                  │
                │ paciente_id (FK)    │
                │ doctor_id (FK)      │
                │ fecha_hora          │
                │ estado              │
                │ razon_consulta      │
                │ notas               │
                │ creada_en           │
                │ actualizada_en      │
                └─────────────────────┘
```

## Flujo de Autenticación

```
VISITANTE ANÓNIMO
    │
    ├─► ¿Ya tiene cuenta?
    │
    ├─ SÍ ─────────────────────┐
    │                           │
    │                    GET /login/
    │                           │
    │                    Ingresa credenciales
    │                           │
    │                    POST /login/
    │                           │
    │                    ✓ Válido
    │                           │
    │                    Crea SessionID
    │                           │
    │                    Redirecciona a /dashboard/
    │
    └─ NO ──────────────────────┐
                                 │
                          GET /registro/
                                 │
                          Completa formulario:
                          - Nombre
                          - Correo
                          - Contraseña
                          - Confirmar contraseña
                                 │
                          POST /registro/
                                 │
                          ✓ Datos válidos
                                 │
                          Crea User (auth_user)
                                 │
                          Signal ────► Auto-crea Paciente
                                 │
                          Login automático
                                 │
                          Redirecciona a /dashboard/
```

## Flujo de Crear Reserva

```
┌─────────────────────────────────────┐
│  USUARIO PACIENTE EN DASHBOARD      │
└─────────────────────────────────────┘
         │
         │ Hace clic en "Nueva Reserva"
         │
         ▼
┌─────────────────────────────────────┐
│  GET /crear-reserva/                │
│  (Muestra formulario)               │
│  ├─ Dropdown de Doctores            │
│  ├─ Selector de Fecha/Hora          │
│  └─ Campo Razón de Consulta         │
└─────────────────────────────────────┘
         │
         │ Usuario completa y envía
         │
         ▼
┌─────────────────────────────────────┐
│  POST /crear-reserva/               │
│  (Validación)                       │
└─────────────────────────────────────┘
         │
         ├─ ¿Doctor existe?
         ├─ ¿Doctor disponible?
         ├─ ¿Fecha es futura?
         └─ ¿No existe reserva en esa hora?
         │
         ✓ TODO VÁLIDO
         │
         ▼
┌─────────────────────────────────────┐
│  Crear Reserva en BD                │
│  estado = 'pendiente'               │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Celery Task: enviar_correo_reserva │
│  (Cola de tareas asincronas)        │
└─────────────────────────────────────┘
         │
         ├─► Redis (Store task)
         │
         └─► Celery Worker (Procesa)
             │
             ├─► SMTP Gmail
             │
             └─► Email enviado ✓
         │
         ▼
┌─────────────────────────────────────┐
│  Redirigir a /dashboard/            │
│  Mostrar mensaje de éxito           │
└─────────────────────────────────────┘
```

## Ciclo de Vida de una Reserva

```
CREACIÓN
    │
    ├─ Paciente crea reserva
    │  └─ Estado: PENDIENTE (⏳ amarillo)
    │     └─ Email: Enviado al paciente
    │
    ▼
CONFIRMACIÓN (Admin)
    │
    ├─ Admin: Confirma cita
    │  └─ Estado: CONFIRMADA (✓ verde)
    │     └─ Email: Enviado al paciente
    │
    ├─ O Paciente cancela
    │  └─ Estado: CANCELADA (✗ rojo)
    │     └─ Email: Notificación de cancelación
    │
    ▼
EJECUCIÓN
    │
    ├─ Paciente asiste a cita
    │  └─ Admin: Completa cita
    │     └─ Estado: COMPLETADA (✓ gris)
    │        └─ Email: Resumen de cita
    │
    └─ Fin del ciclo
```

## Estructura de Componentes UI

```
┌────────────────────────────────────────────────────┐
│              NAVBAR (Sticky)                       │
│  Logo    │  Links    │  Usuario    │  Logout      │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│         HERO SECTION (Gradient Header)             │
│  ┌──────────────────────────────────────────────┐  │
│  │ Título Principal                             │  │
│  │ [Botón Primario] [Botón Secundario]          │  │
│  │ Stats: 50 Doctores | 200 Pacientes          │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│         STATS CARDS (Grid 1-3)                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │ Card 1  │  │ Card 2  │  │ Card 3  │           │
│  │ Total   │  │Próximas │  │Archivo  │           │
│  │ Reservas│  │ Citas   │  │ Activo  │           │
│  └─────────┘  └─────────┘  └─────────┘           │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│         CONTENT AREA                               │
│  ┌─────────────────────────────────────────────┐  │
│  │ [Tab 1: Próximas]  [Tab 2: Historial]       │  │
│  ├─────────────────────────────────────────────┤  │
│  │  Card Item 1                                │  │
│  │  ┌──────────────────────────────────────┐   │  │
│  │  │ Doctor │ Fecha │ Razón │ Estado     │   │  │
│  │  │ [Ver]  │ [Cancelar]                  │   │  │
│  │  └──────────────────────────────────────┘   │  │
│  │                                              │  │
│  │  Card Item 2                                │  │
│  │  ┌──────────────────────────────────────┐   │  │
│  │  │ Doctor │ Fecha │ Razón │ Estado     │   │  │
│  │  │ [Ver]  │ [Cancelar]                  │   │  │
│  │  └──────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│              FOOTER                                │
│  © 2026 Medical Reserva | Contacto | Términos    │
└────────────────────────────────────────────────────┘
```

## Estados de Botones

```
┌─────────────────────────────────────────────┐
│          BUTTON STATES (Visual)             │
└─────────────────────────────────────────────┘

PRIMARY BUTTON (#0f3a7d)
┌────────────────────────────┐
│    Nueva Reserva           │  Default
└────────────────────────────┘
┌────────────────────────────┐
│    Nueva Reserva           │  Hover (darker + shadow)
└────────────────────────────┘
┌────────────────────────────┐
│    Nueva Reserva           │  Active (pressed)
└────────────────────────────┘
┌────────────────────────────┐
│    Nueva Reserva           │  Disabled (opacity 50%)
└────────────────────────────┘

SECONDARY BUTTON (White border)
┌────────────────────────────┐
│    Cancelar                │  Default
└────────────────────────────┘

TEAL BUTTON (#00a896)
┌────────────────────────────┐
│    Confirmar               │  Default
└────────────────────────────┘

DANGER BUTTON (#ef4444)
┌────────────────────────────┐
│    Eliminar                │  Default
└────────────────────────────┘
```

## Grid de Doctores (Lista)

```
┌────────────────────────────────────────────────────────────┐
│         LISTA DE DOCTORES - GRID RESPONSIVO               │
├────────────────────────────────────────────────────────────┤
│
│  Desktop (lg):  3 columnas
│  Tablet (md):   2 columnas
│  Mobile (sm):   1 columna
│
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │
│  │ │ HEADER   │ │  │ │ HEADER   │ │  │ │ HEADER   │ │
│  │ │ (Gradient)  │  │ │ (Gradient)  │  │ │ (Gradient)  │
│  │ │ Dr. Name │ │  │ │ Dr. Name │ │  │ │ Dr. Name │ │
│  │ │Especiald.  │  │ │Especiald.  │  │ │Especiald.  │
│  │ ├──────────┤ │  │ ├──────────┤ │  │ ├──────────┤ │
│  │ │ INFO     │ │  │ │ INFO     │ │  │ │ INFO     │ │
│  │ │ Cédula   │ │  │ │ Cédula   │ │  │ │ Cédula   │ │
│  │ │ Exp: XX  │ │  │ │ Exp: XX  │ │  │ │ Exp: XX  │ │
│  │ │ Email    │ │  │ │ Email    │ │  │ │ Email    │ │
│  │ │ Teléfono │ │  │ │ Teléfono │ │  │ │ Teléfono │ │
│  │ ├──────────┤ │  │ ├──────────┤ │  │ ├──────────┤ │
│  │ │ [AGENDAR]│ │  │ │ [AGENDAR]│ │  │ │ [AGENDAR]│ │
│  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │
│  └──────────────┘  └──────────────┘  └──────────────┘
│
└────────────────────────────────────────────────────────────┘
```

## Paleta de Colores - Uso Específico

```
┌──────────────────────────────────────────────────────────┐
│                 COLOR PALETTE USAGE                      │
└──────────────────────────────────────────────────────────┘

AZUL MÉDICO (#0f3a7d)
████████████
├─ Navbar background
├─ Primary buttons
├─ Links principales
├─ Icons secundarios
└─ Text headings

TEAL MÉDICO (#00a896)
████████████
├─ Gradient header (con azul)
├─ Teal buttons (confirmar)
├─ Accents en cards
├─ Icons de acción
└─ Elementos de éxito

AZUL CLARO (#e3f2fd)
████████████
├─ Background de cards
├─ Hover states
├─ Alert boxes
└─ Resalta contenido

GRIS (#f5f7fa)
████████████
├─ Body background
├─ Alternating row backgrounds
├─ Empty states
└─ Inactive elements

VERDE (#10b981)
████████████
├─ Status: Confirmada
├─ Success messages
├─ Check icons
└─ Positive actions

AMARILLO (#f59e0b)
████████████
├─ Status: Pendiente
├─ Warning alerts
├─ Caution icons
└─ Attention needed

ROJO (#ef4444)
████████████
├─ Status: Cancelada
├─ Danger buttons (eliminar)
├─ Error messages
└─ Delete confirmations

GRIS OSCURO (#1a202c)
████████████
├─ Text principal
├─ Headings
├─ Body text (high contrast)
└─ Dark mode (futuro)
```

## Diagrama de Permisos

```
┌──────────────────────────────────────────────────────┐
│          PERMISSION MATRIX                          │
├──────────────────────────────────────────────────────┤
│
│ ANÓNIMO
│ ├─ Ver index (Home)              ✓
│ ├─ Ver lista de doctores         ✓
│ ├─ Ver detalles de doctor        ✓
│ ├─ Crear reserva                 ✗
│ ├─ Acceder a dashboard           ✗
│ └─ Acceder a admin               ✗
│
│ PACIENTE (Autenticado)
│ ├─ Ver index                     ✓
│ ├─ Ver lista de doctores         ✓
│ ├─ Ver detalles de doctor        ✓
│ ├─ Crear reserva                 ✓
│ ├─ Ver mis reservas              ✓
│ ├─ Editar mi perfil              ✓
│ ├─ Cancelar mi reserva           ✓
│ ├─ Editar reserva                ✗
│ ├─ Acceder a admin               ✗
│ └─ Eliminar otros pacientes      ✗
│
│ ADMIN/STAFF
│ ├─ Acceder a admin-dashboard     ✓
│ ├─ Crear doctor                  ✓
│ ├─ Editar doctor                 ✓
│ ├─ Eliminar doctor               ✓
│ ├─ Ver todos los pacientes       ✓
│ ├─ Ver todas las reservas        ✓
│ ├─ Crear reserva (para otro)     ✓
│ ├─ Confirmar reserva             ✓
│ ├─ Completar reserva             ✓
│ ├─ Cancelar reserva              ✓
│ └─ Acceder a Django Admin        ✗ (superuser solo)
│
│ SUPERUSER
│ ├─ Todas las acciones            ✓
│ ├─ Django Admin (/admin/)        ✓
│ └─ Gestionar usuarios/grupos     ✓
│
└──────────────────────────────────────────────────────┘
```

## Integración API REST

```
┌─────────────────────────────────────────────────────┐
│         API REST ARCHITECTURE                       │
└─────────────────────────────────────────────────────┘

CLIENT (JavaScript/Mobile/3rd-party)
    │
    │ HTTP Request + JWT Token
    │ Authorization: Bearer <token>
    │
    ▼
┌─────────────────────────────────────────────────────┐
│         API ENDPOINTS (/api/)                       │
│                                                     │
│  ├─ /api/token/                                     │
│  │  └─ Obtener JWT token                            │
│  │                                                  │
│  ├─ /api/doctores/                                  │
│  │  ├─ GET: Listar doctores                         │
│  │  ├─ POST: Crear doctor (Admin only)              │
│  │  ├─ /{id}/GET: Detalles                          │
│  │  ├─ /{id}/PATCH: Actualizar (Admin only)         │
│  │  ├─ /{id}/DELETE: Eliminar (Admin only)          │
│  │  └─ /disponibles/: Solo disponibles              │
│  │                                                  │
│  ├─ /api/pacientes/                                 │
│  │  ├─ GET: Listar (Admin only)                     │
│  │  ├─ /mi_perfil/: Mi perfil (Authenticated)       │
│  │  ├─ /{id}/GET: Detalles (Authenticated)          │
│  │  └─ /{id}/PATCH: Actualizar (Authenticated)      │
│  │                                                  │
│  └─ /api/reservas/                                  │
│     ├─ GET: Mis reservas (Authenticated)            │
│     ├─ POST: Crear reserva (Authenticated)          │
│     ├─ /{id}/GET: Detalles (Authenticated)          │
│     ├─ /{id}/PATCH: Actualizar (Admin only)         │
│     ├─ /{id}/cancelar/: Cancelar (Authenticated)    │
│     ├─ /{id}/confirmar/: Confirmar (Admin only)     │
│     ├─ /{id}/completar/: Completar (Admin only)     │
│     └─ /proximas/: Próximas citas (Authenticated)   │
│                                                     │
└─────────────────────────────────────────────────────┘
    │
    │ JSON Response
    │ Status Code (200, 201, 400, 401, 404, etc.)
    │
    ▼
CLIENT
```

## Deploy en Producción

```
┌─────────────────────────────────────────────────────┐
│      PRODUCTION ARCHITECTURE                        │
└─────────────────────────────────────────────────────┘

                    USERS
                      │
                      │ HTTPS
                      ▼
            ┌──────────────────┐
            │   Nginx/Apache   │ (Reverse Proxy)
            └────────┬─────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   ┌─────────┐               ┌─────────┐
   │ Gunicorn│ (multiple)    │ Gunicorn│
   │ Workers │               │ Workers │
   └────┬────┘               └────┬────┘
        │                         │
        └─────────────┬───────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌────────┐
   │PostgreSQL  │  │  Redis  │  │ Celery │
   │ (Cloud)    │  │(Cache)  │  │Workers │
   └───────────┘  └──────────┘  └────────┘

Static Files: AWS S3 / CloudFront
Logs: CloudWatch / ELK Stack
Monitoring: New Relic / Datadog
Backups: Automated snapshots
```

---

**Diagrama generado: Mayo 2026**
