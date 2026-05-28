import sys
from django.test import SimpleTestCase
from django.conf import settings

class ArchitectureSmokeTest(SimpleTestCase):
    """
    SimpleTestCase le indica a Django que este bloque NO requiere
    crear ni conectarse a ninguna base de datos relacional.
    """
    
    def test_django_settings_load_successfully(self):
        """
        Valida que el archivo settings.py esté correctamente estructurado
        y que no tenga errores de sintaxis ni variables de entorno faltantes.
        """
        # Verificamos que la clave secreta se haya cargado en el runtime de CI
        self.assertTrue(hasattr(settings, 'SECRET_KEY'))
        self.assertNotEqual(settings.SECRET_KEY, "")

    def test_critical_modules_compilation(self):
        """
        Prueba de humo para asegurar que los controladores y rutas base
        del sistema compilen y se importen sin errores de código.
        """
        try:
            # Forzamos la importación de los módulos clave del proyecto
            import medicalreserva.urls
            import medicalreserva.celery
            
            modulo_cargado = True
        except Exception as e:
            modulo_cargado = False
            print(f"Error de compilación en despliegue: {e}")
            
        self.assertTrue(modulo_cargado, "El código tiene errores de sintaxis o importación.")


error fatal