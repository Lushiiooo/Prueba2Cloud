#!/bin/sh
# Script para esperar a que PostgreSQL esté listo

set -e

host="${DB_HOST:-localhost}"
port="${DB_PORT:-5432}"
user="${DB_USER:-medical_user}"

echo "⏳ Esperando a que PostgreSQL esté listo en $host:$port..."

while ! nc -z "$host" "$port" 2>/dev/null; do
  echo "🔄 PostgreSQL no está listo aún. Esperando..."
  sleep 1
done

echo "✓ PostgreSQL está listo!"

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py migrate --noinput

# Ejecutar seed_data
echo "🌱 Sembrando datos de prueba..."
python manage.py seed_data

# Recolectar estáticos
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Iniciar servidor Django
echo "🚀 Iniciando servidor Django..."
python manage.py runserver 0.0.0.0:8000
