#!/bin/bash
# Quick Verification Script for Medical Reserva CRUDs

echo "=================================================="
echo "🔍 VERIFICACIÓN DE CRUDs - Medical Reserva"
echo "=================================================="

echo -e "\n✅ VERIFICANDO ARCHIVOS PRINCIPALES...\n"

# Check app/forms.py
if grep -q "class RegistroForm" app/forms.py; then
    echo "✓ app/forms.py - RegistroForm presente"
else
    echo "✗ app/forms.py - RegistroForm FALTA"
fi

if grep -q "class DoctorForm" app/forms.py; then
    echo "✓ app/forms.py - DoctorForm presente"
else
    echo "✗ app/forms.py - DoctorForm FALTA"
fi

if grep -q "class ReservaForm" app/forms.py; then
    echo "✓ app/forms.py - ReservaForm presente"
else
    echo "✗ app/forms.py - ReservaForm FALTA"
fi

if grep -q "class PacienteEditForm" app/forms.py; then
    echo "✓ app/forms.py - PacienteEditForm presente"
else
    echo "✗ app/forms.py - PacienteEditForm FALTA"
fi

# Check app/views.py
echo ""

if grep -q "class RegistroView" app/views.py; then
    echo "✓ app/views.py - RegistroView presente"
else
    echo "✗ app/views.py - RegistroView FALTA"
fi

if grep -q "class DoctorCreateView" app/views.py; then
    echo "✓ app/views.py - DoctorCreateView presente"
else
    echo "✗ app/views.py - DoctorCreateView FALTA"
fi

if grep -q "class DoctorUpdateView" app/views.py; then
    echo "✓ app/views.py - DoctorUpdateView presente"
else
    echo "✗ app/views.py - DoctorUpdateView FALTA"
fi

if grep -q "class DoctorDeleteView" app/views.py; then
    echo "✓ app/views.py - DoctorDeleteView presente"
else
    echo "✗ app/views.py - DoctorDeleteView FALTA"
fi

if grep -q "class PacienteUpdateView" app/views.py; then
    echo "✓ app/views.py - PacienteUpdateView presente"
else
    echo "✗ app/views.py - PacienteUpdateView FALTA"
fi

if grep -q "class PacienteDeleteView" app/views.py; then
    echo "✓ app/views.py - PacienteDeleteView presente"
else
    echo "✗ app/views.py - PacienteDeleteView FALTA"
fi

if grep -q "class ReservaCreateView" app/views.py; then
    echo "✓ app/views.py - ReservaCreateView presente"
else
    echo "✗ app/views.py - ReservaCreateView FALTA"
fi

if grep -q "class ReservaUpdateView" app/views.py; then
    echo "✓ app/views.py - ReservaUpdateView presente"
else
    echo "✗ app/views.py - ReservaUpdateView FALTA"
fi

if grep -q "class ReservaDeleteView" app/views.py; then
    echo "✓ app/views.py - ReservaDeleteView presente"
else
    echo "✗ app/views.py - ReservaDeleteView FALTA"
fi

# Check app/urls.py
echo ""

if grep -q "name='registro'" app/urls.py; then
    echo "✓ app/urls.py - Ruta registro presente"
else
    echo "✗ app/urls.py - Ruta registro FALTA"
fi

if grep -q "name='doctor_create'" app/urls.py; then
    echo "✓ app/urls.py - Ruta doctor_create presente"
else
    echo "✗ app/urls.py - Ruta doctor_create FALTA"
fi

if grep -q "name='paciente_update'" app/urls.py; then
    echo "✓ app/urls.py - Ruta paciente_update presente"
else
    echo "✗ app/urls.py - Ruta paciente_update FALTA"
fi

if grep -q "name='reserva_create'" app/urls.py; then
    echo "✓ app/urls.py - Ruta reserva_create presente"
else
    echo "✗ app/urls.py - Ruta reserva_create FALTA"
fi

# Check templates
echo ""

if [ -f "templates/registro.html" ]; then
    echo "✓ templates/registro.html presente"
else
    echo "✗ templates/registro.html FALTA"
fi

if [ -f "templates/doctor_form.html" ]; then
    echo "✓ templates/doctor_form.html presente"
else
    echo "✗ templates/doctor_form.html FALTA"
fi

if [ -f "templates/paciente_form.html" ]; then
    echo "✓ templates/paciente_form.html presente"
else
    echo "✗ templates/paciente_form.html FALTA"
fi

if [ -f "templates/reserva_form.html" ]; then
    echo "✓ templates/reserva_form.html presente"
else
    echo "✗ templates/reserva_form.html FALTA"
fi

if [ -f "templates/paciente_confirm_delete.html" ]; then
    echo "✓ templates/paciente_confirm_delete.html presente"
else
    echo "✗ templates/paciente_confirm_delete.html FALTA"
fi

echo -e "\n=================================================="
echo "🧪 VERIFICACIÓN EN PYTHON"
echo "=================================================="

python manage.py shell -c "
from app.forms import RegistroForm, DoctorForm, ReservaForm, PacienteEditForm
from app.views import RegistroView, DoctorCreateView, PacienteUpdateView, ReservaDeleteView
from django.urls import reverse_lazy, reverse

print('✓ Todos los imports exitosos')

# Verificar que reverse_lazy funciona
try:
    url = reverse_lazy('registro')
    print(f'✓ reverse_lazy(\"registro\") = {url}')
except Exception as e:
    print(f'✗ Error en reverse_lazy: {e}')

# Verificar que reverse funciona
try:
    url = reverse('index')
    print(f'✓ reverse(\"index\") = {url}')
except Exception as e:
    print(f'✗ Error en reverse: {e}')

# Verificar formularios
print('✓ RegistroForm fields:', list(RegistroForm().fields.keys()))
print('✓ DoctorForm fields:', list(DoctorForm().fields.keys()))
print('✓ ReservaForm fields:', list(ReservaForm().fields.keys()))
print('✓ PacienteEditForm fields:', list(PacienteEditForm().fields.keys()))
"

echo -e "\n=================================================="
echo "✨ VERIFICACIÓN COMPLETADA"
echo "=================================================="
echo ""
echo "📝 Próximos pasos:"
echo "1. Abre http://localhost:8000/registro/"
echo "2. Crea una cuenta de prueba"
echo "3. Accede a http://localhost:8000/admin/"
echo "4. Vuelve a /admin-doctores/crear/ para crear un doctor"
echo "5. Verifica que todo funciona correctamente"
echo ""
