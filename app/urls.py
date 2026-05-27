"""
URL configuration for app.
"""
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from . import api_views

router = DefaultRouter()
router.register(r'pacientes', api_views.PacienteViewSet, basename='paciente')
router.register(r'doctores', api_views.DoctorViewSet, basename='doctor')
router.register(r'reservas', api_views.ReservaViewSet, basename='reserva')

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Home and Auth
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
    
    # Paciente Dashboard
    path('dashboard/', views.dashboard_paciente, name='dashboard_paciente'),
    path('reserva/<int:reserva_id>/', views.detalle_reserva, name='detalle_reserva'),
    path('crear-reserva/', views.crear_reserva, name='crear_reserva'),
    path('cancelar-reserva/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    
    # Doctores
    path('doctores/', views.lista_doctores, name='lista_doctores'),
    path('doctor/<int:doctor_id>/', views.detalle_doctor, name='detalle_doctor'),
    
    # Admin Personalizado
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-doctores/', views.admin_doctores, name='admin_doctores'),
    path('admin-doctores/crear/', views.DoctorCreateView.as_view(), name='doctor_create'),
    path('admin-doctores/<int:doctor_id>/editar/', views.DoctorUpdateView.as_view(), name='doctor_update'),
    path('admin-doctores/<int:doctor_id>/eliminar/', views.DoctorDeleteView.as_view(), name='doctor_delete'),
    path('admin-doctor/<int:doctor_id>/toggle/', views.admin_doctor_toggle, name='admin_doctor_toggle'),
    
    path('admin-pacientes/', views.admin_pacientes, name='admin_pacientes'),
    path('paciente/editar/', views.PacienteUpdateView.as_view(), name='paciente_update'),
    path('paciente/eliminar/', views.PacienteDeleteView.as_view(), name='paciente_delete'),
    path('admin-pacientes/<int:paciente_id>/editar/', views.AdminPacienteUpdateView.as_view(), name='admin_paciente_update'),
    path('admin-pacientes/<int:paciente_id>/eliminar/', views.AdminPacienteDeleteView.as_view(), name='admin_paciente_delete'),
    
    path('admin-reservas/', views.admin_reservas, name='admin_reservas'),
    path('admin-reservas/crear/', views.ReservaCreateView.as_view(), name='reserva_create'),
    path('admin-reservas/<int:reserva_id>/editar/', views.ReservaUpdateView.as_view(), name='reserva_update'),
    path('admin-reservas/<int:reserva_id>/eliminar/', views.ReservaDeleteView.as_view(), name='reserva_delete'),
    path('admin-reserva/<int:reserva_id>/confirmar/', views.admin_reserva_confirmar, name='admin_reserva_confirmar'),
    path('admin-reserva/<int:reserva_id>/completar/', views.admin_reserva_completar, name='admin_reserva_completar'),
    path('admin-reserva/<int:reserva_id>/cancelar/', views.admin_reserva_cancelar, name='admin_reserva_cancelar'),
    
    # Reporte mensuales
    path('reportes/generar-reporte/', views.generar_reporte, name='generar_reporte'),
    path('reportes/verificar-reporte/<str:task_id>/', views.verificar_reporte, name='verificar_reporte'),
    path('reportes/descargar-reporte/<str:filename>/', views.descargar_reporte, name='descargar_reporte'),
]

