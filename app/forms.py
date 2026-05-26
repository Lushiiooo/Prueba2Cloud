"""
Forms for medicalreserva app.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Doctor, Paciente, Reserva


class DoctorForm(forms.ModelForm):
    """Form for creating and updating doctors."""
    
    class Meta:
        model = Doctor
        fields = ['nombre', 'especialidad', 'numero_cedula', 'telefono', 'email', 'disponible', 'experiencia_anos']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nombre completo del doctor'
            }),
            'especialidad': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'numero_cedula': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Número de cédula único'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '+34 XXX XXX XXX',
                'type': 'tel'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'correo@ejemplo.com'
            }),
            'disponible': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-500 rounded focus:ring-2 focus:ring-blue-500'
            }),
            'experiencia_anos': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': 0,
                'max': 70,
                'placeholder': 'Años de experiencia'
            }),
        }


class PacienteEditForm(forms.ModelForm):
    """Form for editing patient profile."""
    
    first_name = forms.CharField(max_length=150, required=False, label='Nombre', widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
        'placeholder': 'Nombre'
    }))
    last_name = forms.CharField(max_length=150, required=False, label='Apellido', widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
        'placeholder': 'Apellido'
    }))
    email = forms.EmailField(required=False, label='Email', widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
        'placeholder': 'correo@ejemplo.com'
    }))
    
    class Meta:
        model = Paciente
        fields = ['fecha_nacimiento', 'telefono', 'direccion', 'numero_seguro', 'alergias']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '+34 XXX XXX XXX',
                'type': 'tel'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Dirección completa',
                'rows': 3
            }),
            'numero_seguro': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Número de seguro médico'
            }),
            'alergias': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Describe tus alergias conocidas',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.usuario:
            self.fields['first_name'].initial = self.instance.usuario.first_name
            self.fields['last_name'].initial = self.instance.usuario.last_name
            self.fields['email'].initial = self.instance.usuario.email
    
    def save(self, commit=True):
        paciente = super().save(commit=False)
        if paciente.usuario:
            paciente.usuario.first_name = self.cleaned_data['first_name']
            paciente.usuario.last_name = self.cleaned_data['last_name']
            paciente.usuario.email = self.cleaned_data['email']
            paciente.usuario.save()
        if commit:
            paciente.save()
        return paciente

class ReservaPacienteForm(forms.ModelForm):
    """Formulario simplificado para que el paciente cree su propia reserva."""
    class Meta:
        model = Reserva
        fields = ['doctor', 'fecha_hora', 'razon_consulta']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'fecha_hora': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'type': 'datetime-local'}),
            'razon_consulta': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
        }


class ReservaForm(forms.ModelForm):
    """Form for creating and updating reservations (Admin only)."""
    
    class Meta:
        model = Reserva
        fields = ['paciente', 'doctor', 'fecha_hora', 'razon_consulta', 'estado', 'notas']
        widgets = {
            'paciente': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'doctor': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'fecha_hora': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
            'razon_consulta': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Razón de la consulta'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Notas adicionales',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que el datetime se formatea correctamente para datetime-local input
        if self.instance and self.instance.fecha_hora:
            # Convertir datetime a string en formato datetime-local (YYYY-MM-DDTHH:mm)
            self.fields['fecha_hora'].initial = self.instance.fecha_hora.strftime('%Y-%m-%dT%H:%M')


class RegistroForm(UserCreationForm):
    """Custom registration form with additional user fields and patient profile creation."""
    
    first_name = forms.CharField(max_length=150, required=True, label='Nombre', widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
        'placeholder': 'Tu nombre'
    }))
    last_name = forms.CharField(max_length=150, required=True, label='Apellido', widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
        'placeholder': 'Tu apellido'
    }))
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
        'placeholder': 'tu@correo.com'
    }))
    username = forms.CharField(max_length=150, required=True, label='Usuario', widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
        'placeholder': 'Nombre de usuario único'
    }))
    fecha_nacimiento = forms.DateField(required=True, label='Fecha de Nacimiento', widget=forms.DateInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
        'type': 'date'
    }))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
            'placeholder': 'Contraseña'
        })
        self.fields['password1'].label = 'Contraseña'
        
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
            'placeholder': 'Confirma tu contraseña'
        })
        self.fields['password2'].label = 'Confirmar Contraseña'
    
    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            Paciente.objects.create(
                usuario=user,
                fecha_nacimiento=self.cleaned_data['fecha_nacimiento']
            )
        return user
