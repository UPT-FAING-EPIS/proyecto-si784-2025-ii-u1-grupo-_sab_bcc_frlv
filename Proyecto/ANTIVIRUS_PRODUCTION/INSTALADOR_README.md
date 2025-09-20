# 🛡️ Instalador Anti-Keylogger

Instalador simple y rápido para el sistema Anti-Keylogger Protection.

## 🚀 Instalación Rápida

### Paso 1: Descargar
```bash
git clone https://github.com/KrCrimson/proyecto-Anti-keylogger.git
cd proyecto-Anti-keylogger/ANTIVIRUS_PRODUCTION
```

### Paso 2: Ejecutar Instalador
```bash
python install_antivirus.py
```

**¡Eso es todo!** El instalador se encarga de todo automáticamente.

## 📋 ¿Qué hace el instalador?

✅ **Verifica requisitos** (Python 3.8+)  
✅ **Instala dependencias** automáticamente  
✅ **Crea directorios** necesarios  
✅ **Copia archivos** del antivirus  
✅ **Configura el sistema** correctamente  
✅ **Crea acceso directo** en escritorio  
✅ **Verifica instalación** completa  

## 🎯 Después de Instalar

### Ejecutar el Antivirus
1. **Desde escritorio**: Doble click en `Anti-Keylogger.bat`
2. **Desde consola**: `python C:\Users\{USUARIO}\AntiKeylogger\start_antivirus.py`
3. **Navegando**: Ir a `C:\Users\{USUARIO}\AntiKeylogger` → `python antivirus_launcher.py`

### ⚠️ Importante
- **Ejecutar como Administrador** para máxima protección
- Los **logs** se guardan en `~/AntiKeylogger/logs/`
- La **configuración** está en `~/AntiKeylogger/config/`

## 🗑️ Desinstalar

Para desinstalar completamente:
```bash
python uninstall_antivirus.py
```

El desinstalador:
- Detiene procesos activos
- Ofrece backup de configuración
- Elimina todos los archivos
- Limpia accesos directos

## 📁 Estructura de Instalación

```
~/AntiKeylogger/
├── antivirus/              # Módulos del antivirus
├── models/                 # Modelos ML de detección
├── config/                 # Configuración
├── logs/                   # Registros del sistema
├── temp/                   # Archivos temporales
├── antivirus_launcher.py   # Launcher principal
├── start_antivirus.py      # Script de inicio optimizado
└── ...
```

## 🔧 Requisitos

- **Python 3.8+**
- **Windows 10/11** (recomendado)
- **Permisos de administrador** (opcional, pero recomendado)
- **Conexión a internet** (para instalar dependencias)

## 📦 Dependencias Instaladas

El instalador instala automáticamente:
- `psutil` - Monitoreo del sistema
- `watchdog` - Vigilancia de archivos
- `scikit-learn` - Machine Learning
- `joblib` - Serialización de modelos
- `numpy` - Computación numérica
- `pefile` - Análisis de ejecutables
- `onnxruntime` - Ejecución de modelos ONNX
- `fastapi` - API web
- `uvicorn` - Servidor ASGI

## 🛠️ Solución de Problemas

### Error de permisos
```bash
# Ejecutar como administrador
# Click derecho → "Ejecutar como administrador"
```

### Error de Python
```bash
# Verificar versión de Python
python --version

# Debe ser 3.8 o superior
```

### Error de dependencias
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Reinstalar manualmente
pip install psutil watchdog scikit-learn
```

### Error de importación
```bash
# Verificar instalación
cd ~/AntiKeylogger
python -c "import antivirus; print('OK')"
```

## 🚨 Funcionalidades del Antivirus

Una vez instalado, el antivirus proporciona:

- **🔍 Detección en tiempo real** de keyloggers
- **🛡️ Protección proactiva** del sistema
- **📊 Análisis con Machine Learning** de procesos sospechosos
- **📝 Registro detallado** de eventos de seguridad
- **⚡ Bajo impacto** en rendimiento del sistema
- **🔧 Configuración flexible** según necesidades

## 💡 Consejos de Uso

1. **Ejecutar siempre como administrador** para máxima efectividad
2. **Revisar logs regularmente** para detectar amenazas
3. **Mantener actualizado** el sistema y dependencias
4. **Configurar exclusiones** si hay falsos positivos
5. **Hacer backup** de configuración personalizada

## 📞 Soporte

Si tienes problemas:
1. Revisa este README
2. Consulta los logs en `~/AntiKeylogger/logs/`
3. Ejecuta el desinstalador y vuelve a instalar
4. Verifica que tengas Python 3.8+ y permisos adecuados

---

**🛡️ ¡Tu sistema estará protegido contra keyloggers una vez completada la instalación!**