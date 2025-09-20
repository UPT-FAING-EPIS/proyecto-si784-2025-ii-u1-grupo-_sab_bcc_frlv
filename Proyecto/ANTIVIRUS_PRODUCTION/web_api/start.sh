#!/bin/bash

# Script de inicio para Railway
echo "🚀 Iniciando Anti-Keylogger API..."

# Verificar variables de entorno
echo "📍 Puerto configurado: ${PORT:-8000}"
echo "📂 Directorio actual: $(pwd)"
echo "📁 Archivos disponibles:"
ls -la

# Verificar modelos
echo "🧠 Verificando modelos ML..."
if [ -d "models" ]; then
    echo "✅ Carpeta models encontrada"
    ls -la models/
else
    echo "❌ Carpeta models no encontrada"
fi

# Verificar dependencias principales
echo "🐍 Verificando dependencias Python..."
python -c "import fastapi; print('✅ FastAPI OK')" || echo "❌ FastAPI error"
python -c "import uvicorn; print('✅ Uvicorn OK')" || echo "❌ Uvicorn error"
python -c "import sklearn; print('✅ Scikit-learn OK')" || echo "❌ Scikit-learn error"
python -c "import numpy; print('✅ Numpy OK')" || echo "❌ Numpy error"

# Iniciar aplicación
echo "🌟 Iniciando servidor..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info