import importlib.metadata
from django.test import TestCase

class DependencyVersionValidationTest(TestCase):
    def setUp(self):
        # Definimos el diccionario con las versiones estrictas del informe técnico
        self.versiones_requeridas = {
            "django": "5.0.6",
            "gunicorn": "21.2.0",
            "djangorestframework": "3.14.0",  # En Python, el tag 3.14 se registra como 3.14.0
            "celery": "5.3.4",
        }

    def test_framework_versions_match_requirements(self):
        """
        Garantiza que el entorno aislado de CI tenga instaladas las versiones exactas
        del stack tecnológico declaradas para producción.
        """
        for paquete, version_esperada in self.versiones_requeridas.items():
            try:
                # Extrae la versión real instalada en el runtime de GitHub Actions
                version_instalada = importlib.metadata.version(paquete)

                # Compara que coincida con el contrato técnico
                self.assertEqual(
                    version_instalada,
                    version_esperada,
                    f"Fallo de CI: El paquete {paquete} tiene la versión {version_instalada} pero se requiere la {version_esperada}."
                )
            except importlib.metadata.PackageNotFoundError:
                self.fail(f"Fallo de CI: El paquete crítico '{paquete}' no está instalado en el entorno.")