# Usa imagen oficial de Python 3.11
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema para PostgreSQL y Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    netcat-openbsd \
    azure-cli \
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de requisitos
COPY requirements.txt .

# Instala las dependencias Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia el código de la aplicación
COPY . .

# Copia y prepara el script de entrada
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expone el puerto 8000
EXPOSE 8000

# Ejecuta el script de entrada
ENTRYPOINT ["/app/entrypoint.sh"]