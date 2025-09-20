# Dockerfile para Railway en la raíz del proyecto
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos desde la subcarpeta
COPY ANTIVIRUS_PRODUCTION/web_api/requirements.txt .

# Actualizar pip y instalar dependencias
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código
COPY ANTIVIRUS_PRODUCTION/web_api/ .

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE $PORT

# Comando para ejecutar la aplicación
RUN chmod +x start.sh
CMD ["./start.sh"]