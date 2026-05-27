#!/usr/bin/env python
"""
Script de prueba para Resend
Uso: python test_resend.py
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicalreserva.settings')
django.setup()

from django.conf import settings

print("=" * 70)
print("PRUEBA DE CONFIGURACIÓN RESEND")
print("=" * 70)

# 1. Verificar variables de entorno
print("\n1. VARIABLES DE ENTORNO:")
print(f"   API Key: {settings.RESEND_API_KEY}")
print(f"   FROM Email: {settings.RESEND_FROM_EMAIL}")

if not settings.RESEND_API_KEY:
    print("   ❌ ERROR: RESEND_API_KEY no está configurada")
    sys.exit(1)

if not settings.RESEND_FROM_EMAIL:
    print("   ❌ ERROR: RESEND_FROM_EMAIL no está configurada")
    sys.exit(1)

print("   ✅ Variables configuradas")

# 2. Probar importación de resend
print("\n2. IMPORTACIÓN DE LIBRERÍA RESEND:")
try:
    import resend
    print(f"   ✅ Resend importado exitosamente")
    print(f"   Versión: {resend.__version__ if hasattr(resend, '__version__') else 'desconocida'}")
except ImportError as e:
    print(f"   ❌ ERROR: No se puede importar resend: {e}")
    print("   Ejecuta: pip install resend==2.3.0")
    sys.exit(1)

# 3. Prueba de envío simple
print("\n3. PRUEBA DE ENVÍO:")
print("   Enviando correo de prueba...")

try:
    resend.api_key = settings.RESEND_API_KEY
    
    response = resend.Emails.send({
        "from": settings.RESEND_FROM_EMAIL,
        "to": ["servidor12minecraft21@gmail.com"],
        "subject": "Prueba Resend - Medical Reserva",
        "html": """
        <h1>¡Prueba Exitosa!</h1>
        <p>Si recibes este correo, Resend está configurado correctamente.</p>
        <p><strong>Detalles:</strong></p>
        <ul>
            <li>API Key: válida</li>
            <li>FROM Email: """ + settings.RESEND_FROM_EMAIL + """</li>
            <li>TO Email: servidor12minecraft21@gmail.com</li>
        </ul>
        """,
    })
    
    print(f"\n   Respuesta de Resend:")
    print(f"   {response}")
    
    if response.get("id"):
        print(f"\n   ✅ CORREO ENVIADO EXITOSAMENTE")
        print(f"   ID de Resend: {response.get('id')}")
        print(f"\n   Revisa tu bandeja de entrada en servidor12minecraft21@gmail.com")
    else:
        print(f"\n   ❌ ERROR EN RESEND:")
        error_msg = response.get("message", response.get("error", "Error desconocido"))
        print(f"   {error_msg}")
        
        # Mensajes de ayuda comunes
        if "Invalid from email" in str(error_msg):
            print(f"\n   💡 SOLUCIÓN: El email {settings.RESEND_FROM_EMAIL} no está verificado en Resend")
            print(f"   Ve a: https://resend.com/domains")
            print(f"   Verifica que medicalreserva.com esté en tu lista de dominios")
        
        sys.exit(1)

except Exception as e:
    print(f"\n   ❌ ERROR AL ENVIAR:")
    print(f"   {type(e).__name__}: {str(e)}")
    print(f"\n   Posibles causas:")
    print(f"   1. API Key inválida")
    print(f"   2. Dominio no verificado en Resend")
    print(f"   3. Problema de conexión a internet")
    sys.exit(1)

print("\n" + "=" * 70)
print("PRUEBA COMPLETADA")
print("=" * 70)
