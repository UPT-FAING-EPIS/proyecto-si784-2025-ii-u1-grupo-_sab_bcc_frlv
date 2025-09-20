# Sistema Anti-Keylogger con Machine Learning

## 🛡️ Descripción General

Este proyecto implementa un sistema antivirus completo especializado en la detección de keyloggers utilizando técnicas de Machine Learning. El sistema combina análisis de comportamiento en tiempo real con modelos predictivos avanzados para proporcionar protección proactiva contra amenazas de keylogging.

## 🏗️ Arquitectura del Sistema

### Componentes Principales

1. **Motor Principal** (`antivirus/core/engine.py`)
   - Orquestación de todos los componentes
   - Gestión de amenazas en tiempo real
   - Coordinación de respuestas automáticas

2. **Monitores de Sistema**
   - **Monitor de Red** (`antivirus/monitors/network_monitor.py`)
   - **Monitor de Procesos** (`antivirus/monitors/process_monitor.py`)
   - **Monitor de Archivos** (`antivirus/monitors/file_monitor.py`)

3. **Detectores Especializados**
   - **Detector ML** (`antivirus/detectors/ml_detector.py`)
   - **Detector de Comportamiento** (`antivirus/detectors/behavior_detector.py`)
   - **Detector de Patrones de Red** (`antivirus/detectors/network_detector.py`)

4. **Utilidades**
   - **Escáner de Archivos** (`antivirus/utils/file_scanner.py`)
   - **Sistema de Cuarentena**
   - **Logging Avanzado**

## 🤖 Machine Learning

### Modelos Implementados

- **Random Forest Classifier**
  - Modelo base: 73.89% de precisión
  - Modelo avanzado con features: 88.25% de precisión
  - Optimización ONNX: 9.95x speedup

### Pipeline de Datos

1. **Extracción de Features**
   - Análisis de tráfico de red
   - Patrones de comportamiento de procesos
   - Métricas de sistema

2. **Preprocessamiento**
   - Normalización de datos
   - Selección de características
   - Balanceo de clases

3. **Entrenamiento**
   - Validación cruzada
   - Optimización de hiperparámetros
   - Evaluación de rendimiento

## 🚀 Instalación Rápida

### Opción 1: Despliegue Automático (Recomendado)

```bash
# Despliegue completo con entrenamiento
python deploy.py complete

# Despliegue rápido sin entrenamiento
python deploy.py quick
```

### Opción 2: Instalación Manual

```bash
# 1. Instalar dependencias
python install_antivirus.py

# 2. Entrenar modelos (opcional)
python scripts/train_from_datos.py

# 3. Ejecutar pruebas
python test_antivirus.py

# 4. Iniciar sistema
python antivirus_launcher.py
```

## 📋 Requisitos del Sistema

### Software Requerido
- Python 3.8+
- pip (gestor de paquetes)
- 2GB RAM mínimo
- 1GB espacio libre

### Dependencias Principales
```
psutil>=5.9.0
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
onnxruntime>=1.10.0
joblib>=1.1.0
toml>=0.10.0
```

### Dependencias Opcionales
```
python-magic      # Detección de tipos de archivo
watchdog         # Monitoreo avanzado de archivos
cryptography     # Análisis de archivos cifrados
pefile           # Análisis de ejecutables PE
```

## 🎯 Uso del Sistema

### Comandos Principales

```bash
# Información del sistema
python antivirus_launcher.py --info

# Modo de prueba
python antivirus_launcher.py --test

# Protección en tiempo real
python antivirus_launcher.py

# Protección en background
python antivirus_launcher.py --daemon
```

### Configuración

El archivo `antivirus/config.toml` contiene todas las configuraciones:

```toml
[monitoring]
network_interval = 5.0
process_interval = 3.0
file_monitoring = true

[detection]
ml_threshold = 0.7
behavior_sensitivity = "medium"
quarantine_enabled = true

[logging]
level = "INFO"
file_rotation = true
max_size_mb = 100
```

## 🧪 Sistema de Pruebas

### Ejecutar Pruebas

```bash
# Suite completa de pruebas
python test_antivirus.py

# Solo pruebas de ML
python test_antivirus.py --ml-only

# Pruebas de rendimiento
python test_antivirus.py --performance
```

### Tipos de Pruebas
- ✅ Importación de módulos
- ✅ Carga de modelos ML
- ✅ Funcionamiento de monitores
- ✅ Detectores especializados
- ✅ Integración de componentes
- ✅ Rendimiento del sistema

## 🧹 Mantenimiento

### Comandos de Mantenimiento

```bash
# Mantenimiento estándar
python maintenance.py

# Mantenimiento completo
python maintenance.py full

# Solo limpiar logs
python maintenance.py logs

# Solo backup
python maintenance.py backup
```

### Tareas Automatizadas
- 🗂️ Limpieza de logs antiguos
- 🗃️ Limpieza de archivos temporales
- 🔒 Gestión de cuarentena
- 💾 Backups automáticos
- 📁 Verificación de estructura

## 📊 Monitoreo y Logs

### Ubicación de Logs
```
logs/
├── antivirus_main.log          # Log principal
├── network_monitor.log         # Actividad de red
├── process_monitor.log         # Actividad de procesos
├── file_monitor.log           # Actividad de archivos
├── ml_detector.log            # Detecciones ML
└── test_results_*.json        # Resultados de pruebas
```

### Métricas Disponibles
- 📈 Tasa de detección
- ⚡ Tiempo de respuesta
- 🔍 Falsos positivos/negativos
- 💻 Uso de recursos del sistema
- 🌐 Patrones de tráfico de red

## 🔧 Desarrollo y Extensión

### Estructura del Proyecto
```
Python_ML/
├── antivirus/                 # Sistema antivirus principal
│   ├── core/                 # Motor principal
│   ├── monitors/             # Monitores especializados
│   ├── detectors/            # Detectores de amenazas
│   ├── utils/                # Utilidades
│   └── config.toml           # Configuración
├── models/                   # Modelos ML
│   └── development/          # Modelos entrenados
├── scripts/                  # Scripts de utilidad
├── DATOS/                    # Datasets
├── demos/                    # Demostraciones
├── logs/                     # Archivos de log
├── quarantine/               # Archivos en cuarentena
└── temp/                     # Archivos temporales
```

### Añadir Nuevos Detectores

1. Crear nueva clase en `antivirus/detectors/`
2. Heredar de `BaseDetector`
3. Implementar métodos `detect()` y `configure()`
4. Registrar en el motor principal

```python
from antivirus.detectors.base import BaseDetector

class CustomDetector(BaseDetector):
    def detect(self, data):
        # Lógica de detección personalizada
        return threat_analysis
    
    def configure(self, config):
        # Configuración específica
        pass
```

## 🛡️ Seguridad

### Características de Seguridad
- 🔐 Cuarentena segura de archivos maliciosos
- 📝 Logging detallado de todas las actividades
- 🚫 Protección contra bypass de detección
- 🔄 Actualizaciones automáticas de modelos
- 👥 Control de acceso basado en permisos

### Mejores Prácticas
- Ejecutar con permisos mínimos necesarios
- Revisar logs regularmente
- Actualizar modelos periódicamente
- Configurar backups automáticos
- Monitorear rendimiento del sistema

## 📈 Rendimiento

### Benchmarks Típicos
- **Detección ML**: >100 predicciones/segundo
- **Monitoreo de Red**: ~5 segundos de intervalo
- **Análisis de Procesos**: ~3 segundos de intervalo
- **Uso de RAM**: <200MB en condiciones normales
- **Uso de CPU**: <5% en operación continua

### Optimizaciones Implementadas
- ⚡ Modelos ONNX optimizados
- 🔄 Caché de predicciones
- 📊 Análisis asíncrono
- 🎯 Filtrado inteligente de eventos
- 💾 Gestión eficiente de memoria

## 🐛 Solución de Problemas

### Problemas Comunes

**Error: Modelos ML no encontrados**
```bash
# Ejecutar entrenamiento
python scripts/train_from_datos.py
```

**Error: Dependencias faltantes**
```bash
# Re-instalar dependencias
python install_antivirus.py
```

**Alto uso de CPU**
```bash
# Ajustar intervalos en config.toml
[monitoring]
network_interval = 10.0
process_interval = 5.0
```

**Muchos falsos positivos**
```bash
# Ajustar sensibilidad
[detection]
ml_threshold = 0.8
behavior_sensitivity = "low"
```

### Logs de Debug
```bash
# Habilitar logging debug en config.toml
[logging]
level = "DEBUG"
```

## 🤝 Contribución

### Cómo Contribuir
1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

### Estándares de Código
- Seguir PEP 8
- Documentar funciones públicas
- Incluir pruebas unitarias
- Actualizar documentación

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📞 Soporte

### Recursos de Ayuda
- 📖 Documentación: `ANTIVIRUS_README.md`
- 🧪 Pruebas: `python test_antivirus.py`
- 🔧 Mantenimiento: `python maintenance.py`
- 📊 Estado: `python antivirus_launcher.py --info`

### Contacto
- 🐛 Issues: GitHub Issues
- 💬 Discusiones: GitHub Discussions
- 📧 Email: [configurar según necesidad]

---

## 🎯 Casos de Uso

### Protección Personal
- Detección de keyloggers en computadoras personales
- Monitoreo de actividad sospechosa
- Protección de datos sensibles

### Entornos Corporativos
- Seguridad de estaciones de trabajo
- Monitoreo de amenazas internas
- Compliance de seguridad

### Investigación y Análisis
- Análisis forense de malware
- Investigación de patrones de amenazas
- Desarrollo de contramedidas

---

*Este README proporciona una visión completa del sistema. Para información técnica detallada, consulte la documentación específica de cada componente.*