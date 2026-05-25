## 🚀 API Medical Reserva - Verificación

### 1. Verifica que los Datos Existen en la BD

```bash
# Doctores
docker exec medical_web python manage.py shell -c "from app.models import Doctor; print(f'✓ Doctores: {Doctor.objects.count()}')"

# Pacientes
docker exec medical_web python manage.py shell -c "from app.models import Paciente; print(f'✓ Pacientes: {Paciente.objects.count()}')"

# Reservas
docker exec medical_web python manage.py shell -c "from app.models import Reserva; print(f'✓ Reservas: {Reserva.objects.count()}')"
```

---

### 2. Endpoints de la API REST

**Base URL**: `http://localhost:8000/api/`

#### 🔐 Autenticación (Token JWT)

**POST** `/api/token/`
```json
{
  "username": "admin",
  "password": "admin123"
}
```
Respuesta:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**POST** `/api/token/refresh/`
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

#### 👨‍⚕️ Doctores

**GET** `/api/doctores/` - Listar todos
**GET** `/api/doctores/{id}/` - Obtener uno
**GET** `/api/doctores/disponibles/` - Solo disponibles
**GET** `/api/doctores/disponibles/?especialidad=cardiologia` - Filtrar por especialidad
**GET** `/api/doctores/{id}/reservas/` - Reservas de un doctor

Opciones de búsqueda:
```
GET /api/doctores/?search=Carlos
GET /api/doctores/?ordering=experiencia_anos
GET /api/doctores/?ordering=-nombre
```

---

#### 🏥 Pacientes

**GET** `/api/pacientes/` (Auth requerida) - Listar
**GET** `/api/pacientes/{id}/` (Auth requerida) - Obtener uno
**GET** `/api/pacientes/mi_perfil/` (Auth requerida) - Tu perfil
**POST** `/api/pacientes/` (Auth requerida) - Crear
**PUT** `/api/pacientes/{id}/` (Auth requerida) - Actualizar

Búsqueda:
```
GET /api/pacientes/?search=Juan
```

---

#### 📅 Reservas

**GET** `/api/reservas/` (Auth) - Listar mis reservas
**GET** `/api/reservas/{id}/` (Auth) - Obtener una
**GET** `/api/reservas/proximas/` (Auth) - Próximas
**POST** `/api/reservas/` (Auth) - Crear

```json
{
  "doctor": 1,
  "fecha_hora": "2026-05-26T14:00:00Z",
  "razon_consulta": "Revisión general",
  "notas": "Sin alergias"
}
```

**POST** `/api/reservas/{id}/cancelar/` (Auth) - Cancelar
**POST** `/api/reservas/{id}/confirmar/` (Staff) - Confirmar
**POST** `/api/reservas/{id}/completar/` (Staff) - Completar

---

### 3. Ejemplos en Bash (cURL)

#### Obtener Token
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"paciente_test","password":"paciente123"}'
```

#### Listar Doctores
```bash
curl http://localhost:8000/api/doctores/
```

#### Listar Mis Reservas (Requiere Token)
```bash
curl -H "Authorization: Bearer AQUI_TU_ACCESS_TOKEN" \
  http://localhost:8000/api/reservas/
```

#### Crear Reserva
```bash
curl -X POST http://localhost:8000/api/reservas/ \
  -H "Authorization: Bearer AQUI_TU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor": 1,
    "fecha_hora": "2026-05-26T14:00:00Z",
    "razon_consulta": "Revisión"
  }'
```

#### Cancelar Reserva
```bash
curl -X POST http://localhost:8000/api/reservas/1/cancelar/ \
  -H "Authorization: Bearer AQUI_TU_ACCESS_TOKEN"
```

---

### 4. Credenciales de Prueba

**Admin:**
- Usuario: `admin`
- Contraseña: `admin123`

**Paciente:**
- Usuario: `paciente_test`
- Contraseña: `paciente123`

---

### 5. Códigos de Estado HTTP Esperados

| Código | Significado |
|--------|-------------|
| 200 | OK - Éxito |
| 201 | Created - Recurso creado |
| 204 | No Content - Eliminado |
| 400 | Bad Request - Error en datos |
| 401 | Unauthorized - Token inválido o faltante |
| 403 | Forbidden - Permisos insuficientes |
| 404 | Not Found - Recurso no existe |

---

### 6. Paginación

Por defecto retorna 20 resultados por página:
```
GET /api/doctores/?page=1
GET /api/doctores/?page=2
```

Respuesta:
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/doctores/?page=2",
  "previous": null,
  "results": [...]
}
```

---

### 7. Permiso y Restricciones

| Endpoint | Permiso |
|----------|---------|
| GET /doctores | AllowAny |
| POST /doctores | IsAdminUser |
| GET /pacientes | IsAuthenticated |
| GET /reservas | IsAuthenticated (propio del usuario) |
| POST /reservas/confirmar | IsAdminUser |

---

### 8. Configuración de Tokens JWT

- **Access Token Lifetime**: 60 minutos
- **Refresh Token Lifetime**: 7 días
- **Algoritmo**: HS256
- **Clave**: SECRET_KEY de Django

---

### 9. Usa esta API desde Flutter

Archivo: `flutter_app/lib/services/api_service.dart`

```dart
final String baseUrl = 'http://10.0.2.2:8000/api';

// Login
final response = await http.post(
  Uri.parse('$baseUrl/token/'),
  body: {'username': 'user', 'password': 'pass'},
);

// Get Doctores
final response = await http.get(Uri.parse('$baseUrl/doctores/'));

// Get Mis Reservas
final response = await http.get(
  Uri.parse('$baseUrl/reservas/'),
  headers: {'Authorization': 'Bearer $accessToken'},
);
```

---

### 10. Test Rápido en Navegador

1. Abre: `http://localhost:8000/admin/`
2. Login: `admin` / `admin123`
3. Verifica que existan:
   - ✓ 3 Doctores
   - ✓ 1 Paciente
   - ✓ 1 Reserva

4. Luego accede a: `http://localhost:8000/api/doctores/`
   - Verás JSON de doctores disponibles (sin token)

5. Accede a: `http://localhost:8000/api/reservas/`
   - Django Rest Framework mostrará formulario de login
   - Haz login y verás tus reservas en JSON
