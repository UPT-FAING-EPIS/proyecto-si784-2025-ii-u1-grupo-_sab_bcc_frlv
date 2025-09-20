# Anti-Keylogger Detection API

API REST para detectar keyloggers usando Machine Learning.

## 🚀 Despliegue en Railway (Gratis)

### ⚠️ Configuración para rama 'Calidad'

**Este proyecto está en la rama `Calidad`, no en `main`**

1. **Conectar repositorio en Railway:**
   - Ve a [railway.app](https://railway.app)
   - New Project → Deploy from GitHub repo
   - Selecciona: `KrCrimson/proyecto-Anti-keylogger`

2. **Configurar rama y directorio:**
   - Settings → Source → Branch: `Calidad`
   - Settings → Build → Root Directory: `ANTIVIRUS_PRODUCTION/web_api`
   - Settings → Build → Builder: `DOCKERFILE`

3. **Variables automáticas:**
   - Railway detectará el `Dockerfile` automáticamente
   - El puerto se configurará via `$PORT` environment variable

4. **Deploy:**
   - Haz click en "Deploy"
   - Railway construirá y desplegará automáticamente
   - Tu API estará disponible en: `https://tu-proyecto.railway.app`

### Opción 2: Deploy con Railway CLI
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Hacer login
railway login

# Inicializar proyecto
railway init

# Deploy
railway up
```

## 📋 Archivos incluidos

- `main.py` - Código principal de la API
- `requirements.txt` - Dependencias Python
- `Dockerfile` - Configuración para contenedor
- `Procfile` - Configuración para Heroku
- `package.json` - Metadatos del proyecto
- `models/` - Modelos ML entrenados

## 🔧 Uso de la API

### Endpoint principal
```
GET /
```
Interfaz web para subir archivos

### Análisis de archivos
```
POST /analyze
Content-Type: multipart/form-data

file: archivo.exe
```

Respuesta:
```json
{
  "prediction": "keylogger|safe",
  "confidence": 0.95,
  "file_info": {
    "name": "archivo.exe",
    "size": 12345,
    "hash": "abc123..."
  }
}
```

### Salud del servicio
```
GET /health
```

### Estadísticas
```
GET /stats
```

## 🌐 Plataformas de Despliegue Gratuitas

1. **Railway** - Recomendado
   - 500 horas gratis/mes
   - Deploy automático desde Git
   - Soporte Docker nativo

2. **Render**
   - 750 horas gratis/mes
   - SSL automático
   - Deploy desde GitHub

3. **Heroku**
   - 550 horas gratis/mes
   - Fácil configuración
   - Gran ecosistema

## 📝 Variables de Entorno

No se requieren variables de entorno especiales. Los modelos se cargan automáticamente desde la carpeta `models/`.

## ⚡ Prueba Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar API
python main.py

# Visitar http://localhost:8000
```

## 🔒 Características de Seguridad

- Validación de tipos de archivo (.exe únicamente)
- Límites de tamaño de archivo
- Análisis de PE headers
- Detección de APIs sospechosas
- Logging de todas las solicitudes