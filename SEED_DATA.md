# 🌱 Script de Inicialización de Datos - Medical Reserva

## Descripción

El comando `seed_data` siembra automáticamente datos de prueba en la base de datos. Es **idempotente**, lo que significa que puede ejecutarse múltiples veces sin crear duplicados.

---

## 📋 Qué Crea

### 1. **Superusuario (Admin)**
- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **Email**: `admin@medicalreserva.com`

### 2. **3 Doctores de Prueba**
| Nombre | Especialidad | Cédula | Experiencia |
|--------|--------------|--------|-------------|
| Dr. Carlos Martínez López | Cardiología | CD-001-2024 | 15 años |
| Dra. María González Ruiz | Pediatría | CD-002-2024 | 12 años |
| Dr. Juan Rodríguez Torres | Medicina General | CD-003-2024 | 20 años |

### 3. **Paciente de Prueba**
- **Usuario**: `paciente_test`
- **Contraseña**: `paciente123`
- **Nombre**: Juan Pérez García
- **Fecha de Nacimiento**: 15/03/1985
- **Alergias**: Penicilina, Mariscos

### 4. **Reserva de Prueba**
- Cita confirmada para mañana a las 14:00
- Entre el paciente de prueba y el primer doctor
- Razón: Revisión médica general

---

## 🚀 Ejecución Automática (Recomendado)

El comando se ejecuta **automáticamente** cada vez que reinicia el contenedor Docker:

```bash
docker-compose up --build
```

El Dockerfile incluye:
```dockerfile
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_data && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
```

---

## 🔧 Ejecución Manual

Si necesitas ejecutar el comando manualmente después de que el contenedor ya está corriendo:

### **Opción 1: Dentro del Contenedor**
```bash
docker exec prueba2_cloud-web-1 python manage.py seed_data
```

Reemplaza `prueba2_cloud-web-1` con el nombre real del contenedor. Puedes verlo con:
```bash
docker ps
```

### **Opción 2: En Local (Desarrollo)** 
Si estás ejecutando Django localmente:
```bash
python manage.py seed_data
```

---

## ✅ Verificación

### 1. **Ver Superusuario Creado**
```bash
docker exec prueba2_cloud-web-1 python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username='admin').exists()
True
```

### 2. **Ver Doctores Creados**
```bash
docker exec prueba2_cloud-web-1 python manage.py shell
>>> from app.models import Doctor
>>> Doctor.objects.count()
3
>>> for d in Doctor.objects.all():
...     print(f"{d.nombre} - {d.get_especialidad_display()}")
```

### 3. **Ver en Admin Panel**
1. Accede a: `http://localhost:8000/admin/`
2. Login con `admin` / `admin123`
3. Verifica:
   - ✓ Doctors (Doctores)
   - ✓ Pacientes
   - ✓ Reservas

---

## 🔄 Idempotencia (No Crea Duplicados)

El script **verifica si los datos ya existen** antes de crearlos:

```python
if Doctor.objects.exists():
    print('Base de datos ya contiene doctores. No se crearán duplicados.')
    return
```

### Ejemplo de Ejecución Múltiple:
```bash
# Primera ejecución
docker exec prueba2_cloud-web-1 python manage.py seed_data
# Output: ✅ Sembrado de datos completado exitosamente.

# Segunda ejecución (la misma)
docker exec prueba2_cloud-web-1 python manage.py seed_data
# Output: ✓ La base de datos ya contiene doctores. No se crearán duplicados.
```

---

## 🗑️ Limpiar Datos de Prueba

Si necesitas eliminar los datos generados y empezar de nuevo:

### **Opción 1: Eliminar Volúmenes Docker**
```bash
docker-compose down -v
docker-compose up --build
```

### **Opción 2: Desde el Admin Panel**
1. Accede a: `http://localhost:8000/admin/`
2. Login: `admin` / `admin123`
3. Elimina manualmente:
   - Doctors
   - Pacientes
   - Reservas

Luego ejecuta nuevamente:
```bash
docker exec prueba2_cloud-web-1 python manage.py seed_data
```

---

## 📝 Notas Importantes

- ✅ El script es **idempotente**: puede ejecutarse múltiples veces sin efectos secundarios
- ✅ No sobrescribe datos existentes
- ✅ Verifica mediante cédula y username para evitar duplicados
- ✅ Incluye manejo de errores (ej: citas duplicadas por unique_together)
- ✅ Muestra feedback en consola con emojis para fácil lectura

---

## 🔐 Seguridad en Producción

**IMPORTANTE**: Las contraseñas de prueba (`admin123`, `paciente123`) deben cambiar en producción:

1. **Cambiar contraseña de admin**:
   ```bash
   docker exec prueba2_cloud-web-1 python manage.py changepassword admin
   ```

2. **Eliminar usuario paciente_test** en producción:
   ```bash
   docker exec prueba2_cloud-web-1 python manage.py shell
   >>> from django.contrib.auth.models import User
   >>> User.objects.get(username='paciente_test').delete()
   ```

---

## 📂 Estructura de Archivos

```
app/
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── seed_data.py     ← Comando personalizado
├── models.py
├── views.py
└── ...
```

---

## 🐛 Troubleshooting

### Problema: "No module named 'app.management.commands.seed_data'"
**Solución**: Asegúrate de que existen los archivos `__init__.py`:
```bash
touch app/management/__init__.py
touch app/management/commands/__init__.py
```

### Problema: "The directory '/app/static' does not exist"
**Solución**: Esto ya está corregido en `settings.py` (STATICFILES_DIRS = [])

### Problema: "IntegrityError: Duplicate entry for..."
**Solución**: El script es idempotente. Si ves este error, ejecuta:
```bash
docker-compose down -v
docker-compose up --build
```

---

## 📞 Contacto / Soporte

Para cualquier duda sobre el sistema Medical Reserva, revisa:
- [README.md](./README.md)
- [DEPLOYMENT.md](./DEPLOYMENT.md)
- [QUICK_START_WINDOWS.md](./QUICK_START_WINDOWS.md)
