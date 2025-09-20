# Sistema Anti-Keylogger con Machine Learning

## 🛡️ Descripción

Sistema antivirus especializado en la detección de keyloggers en tiempo real utilizando técnicas de Machine Learning y análisis heurístico. Combina múltiples enfoques de detección para identificar y neutralizar amenazas de captura de teclado.

## 🎯 Características Principales

### 🤖 Machine Learning
- **Modelo ONNX optimizado**: Detección rápida con modelos entrenados
- **Análisis de tráfico de red**: Identificación de patrones de exfiltración
- **Clasificación binaria**: Benign vs Keylogger con alta precisión
- **Fallback a scikit-learn**: Robustez y compatibilidad

### 🔍 Monitoreo en Tiempo Real
- **Monitor de Red**: Análisis de conexiones y tráfico sospechoso
- **Monitor de Procesos**: Detección de comportamientos maliciosos
- **Monitor de Archivos**: Vigilancia de cambios en el sistema de archivos
- **Análisis Continuo**: Protección 24/7 con bajo consumo de recursos

### 🧠 Detectores Especializados
- **Detector de Comportamiento**: Heurísticas y patrones conocidos
- **Detector de Patrones de Red**: C&C, exfiltración, beacons
- **Detector ML**: Análisis predictivo avanzado
- **Análisis Multifactor**: Combinación de múltiples indicadores

### ⚡ Características Avanzadas
- **Cuarentena Automática**: Aislamiento de archivos maliciosos
- **Respuesta Adaptiva**: Acciones automáticas según severidad
- **Logging Detallado**: Auditoría completa de eventos
- **Configuración Flexible**: Personalización via TOML

## 📁 Estructura del Proyecto

```
antivirus/
├── __init__.py                 # Módulo principal
├── config.toml                 # Configuración del sistema
├── core/
│   ├── __init__.py
│   └── engine.py              # Motor principal del antivirus
├── monitors/
│   ├── __init__.py
│   ├── network_monitor.py     # Monitor de tráfico de red
│   ├── process_monitor.py     # Monitor de procesos
│   └── file_monitor.py        # Monitor de sistema de archivos
├── detectors/
│   ├── __init__.py
│   ├── ml_detector.py         # Detector ML principal
│   ├── behavior_detector.py   # Detector heurístico
│   └── network_detector.py    # Detector de patrones de red
└── utils/
    ├── __init__.py
    └── file_scanner.py         # Escáner de archivos

antivirus_launcher.py           # Launcher principal
requirements_antivirus.txt      # Dependencias adicionales
```

## 🚀 Instalación

### 1. Instalar Dependencias

```bash
# Instalar dependencias básicas del antivirus
pip install -r requirements_antivirus.txt

# Verificar instalación de dependencias ML (ya instaladas)
pip list | grep -E "(numpy|pandas|scikit-learn|onnxruntime)"
```

### 2. Verificar Modelos ML

Asegúrate de que los modelos entrenados estén disponibles:

```
models/development/
├── modelo_keylogger_from_datos.pkl    # Modelo scikit-learn
├── modelo_keylogger_from_datos.onnx   # Modelo ONNX optimizado
├── metadata.json                      # Metadatos del modelo
└── label_classes.json                 # Clases de clasificación
```

### 3. Configuración

Edita `antivirus/config.toml` para personalizar:
- Intervalos de monitoreo
- Umbrales de detección
- Directorios a vigilar
- Configuración de cuarentena

## 💻 Uso

### Protección en Tiempo Real

```bash
# Iniciar protección completa
python antivirus_launcher.py

# Con configuración personalizada
python antivirus_launcher.py --config mi_config.toml

# Modo verbose para debugging
python antivirus_launcher.py --verbose
```

### Escaneo Manual

```bash
# Escanear directorio específico
python antivirus_launcher.py --scan C:\Users\Usuario\Downloads

# Escanear archivo individual
python antivirus_launcher.py --scan archivo_sospechoso.exe
```

### Diagnóstico del Sistema

```bash
# Probar todos los componentes
python antivirus_launcher.py --test

# Mostrar información del sistema
python antivirus_launcher.py --info
```

## 🔧 Componentes Técnicos

### Motor Principal (engine.py)

Coordina todos los componentes del sistema:
- Inicialización de monitores y detectores
- Gestión de callbacks de amenazas
- Análisis integrado de datos
- Respuesta automática a amenazas

### Monitores

**NetworkTrafficMonitor**:
- Captura conexiones de red en tiempo real
- Análisis de patrones de tráfico
- Detección de comunicaciones sospechosas

**ProcessBehaviorMonitor**:
- Vigilancia de procesos activos
- Detección de comportamientos maliciosos
- Análisis de uso de recursos

**FileSystemMonitor**:
- Monitoreo de cambios en archivos
- Detección de archivos sospechosos
- Cuarentena automática

### Detectores

**MLKeyloggerDetector**:
- Utiliza modelos entrenados para clasificación
- Procesamiento optimizado con ONNX
- Extracción automática de características

**BehaviorDetector**:
- Reglas heurísticas especializadas
- Patrones conocidos de keyloggers
- Análisis de comportamiento multi-factor

**NetworkPatternDetector**:
- Detección de comunicaciones C&C
- Análisis de exfiltración de datos
- Patrones de beacon y DGA

## 📊 Métricas y Monitoreo

### Estadísticas en Tiempo Real

El sistema proporciona métricas continuas:
- Escaneos realizados
- Amenazas detectadas
- Tiempo de actividad
- Estado de componentes

### Logging

**antivirus.log**: Log principal del sistema
**security_events.log**: Eventos de seguridad
**quarantine/**: Archivos en cuarentena con metadatos

### Rendimiento

- **CPU**: < 25% de uso promedio
- **Memoria**: < 512MB de RAM
- **Latencia**: < 100ms para detección ML
- **Precisión**: > 88% según benchmarks

## ⚙️ Configuración Avanzada

### Ajuste de Sensibilidad

```toml
[antivirus]
threat_threshold = 0.7          # 0.5 = más sensible, 0.9 = menos sensible

[ml_model] 
confidence_threshold = 0.8      # Umbral para predicciones ML

[behavior_detector]
min_confidence = 0.6           # Mínimo para detección heurística
```

### Personalización de Monitores

```toml
[network_monitor]
monitor_interval = 1.0         # Frecuencia de captura
suspicious_ports = [1337, 4444, 5555]  # Puertos adicionales

[file_monitor]
monitored_directories = [      # Directorios personalizados
    "C:\\MiDirectorio",
    "D:\\Documentos"
]
```

## 🚨 Respuesta a Amenazas

### Niveles de Severidad

- **High**: Terminación de procesos + cuarentena + log
- **Medium**: Cuarentena + notificación + log  
- **Low**: Solo logging y monitoreo

### Acciones Automáticas

1. **Detección**: ML + Heurísticas + Patrones
2. **Análisis**: Correlación multi-fuente
3. **Clasificación**: Asignación de severidad
4. **Respuesta**: Acción automática según configuración
5. **Logging**: Registro completo del evento

## 🧪 Testing y Validación

### Test de Componentes

```bash
python antivirus_launcher.py --test
```

Verifica:
- ✅ Carga de modelos ML
- ✅ Inicialización de monitores
- ✅ Conectividad de detectores
- ✅ Configuración del sistema

### Test de Detección

El sistema incluye casos de prueba integrados para validar:
- Detección de procesos sospechosos
- Análisis de archivos maliciosos
- Patrones de red anómalos

## 📈 Optimización

### Rendimiento

- **ONNX Runtime**: 10x más rápido que scikit-learn
- **Buffers Circulares**: Gestión eficiente de memoria
- **Threading**: Procesamiento paralelo
- **Caché**: Reducción de cálculos repetitivos

### Escalabilidad

- **Configuración Modular**: Habilitar/deshabilitar componentes
- **Throttling Automático**: Control de recursos
- **Batch Processing**: Procesamiento en lotes para ML

## 🔒 Seguridad

### Protección del Sistema

- **Self-Protection**: Resistencia a terminación
- **Privilege Escalation**: Detección de intentos de elevación
- **Anti-Tampering**: Integridad de archivos críticos

### Privacidad

- **Datos Locales**: Sin envío de información personal
- **Hashing**: Anonimización de datos sensibles
- **Logs Rotativos**: Gestión automática de almacenamiento

## 🐛 Troubleshooting

### Problemas Comunes

**Error: "Import 'onnxruntime' could not be resolved"**
```bash
pip install onnxruntime
```

**Error: "No module named 'psutil'"**
```bash
pip install psutil
```

**Error: "Modelo no encontrado"**
- Verificar que `models/development/` contiene los archivos .pkl y .onnx
- Ejecutar pipeline de entrenamiento si es necesario

**Alto uso de CPU**
- Aumentar `scan_interval` en config.toml
- Deshabilitar componentes no necesarios
- Habilitar `auto_throttle = true`

### Debug Mode

```bash
python antivirus_launcher.py --verbose
```

Proporciona información detallada para diagnóstico.

## 📚 Referencias

### Tecnologías Utilizadas

- **scikit-learn**: Machine Learning
- **ONNX Runtime**: Optimización de modelos
- **psutil**: Monitoreo del sistema
- **pandas/numpy**: Procesamiento de datos
- **threading**: Programación concurrente

### Algoritmos

- **Random Forest**: Clasificación principal
- **Feature Engineering**: Extracción de características de red
- **Heuristic Analysis**: Reglas basadas en conocimiento
- **Pattern Matching**: Detección de signatures

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Revisar `scripts/` para pipeline de entrenamiento
2. Añadir nuevos detectores en `antivirus/detectors/`
3. Mejorar monitores en `antivirus/monitors/`
4. Actualizar configuración en `config.toml`

## 📄 Licencia

Proyecto académico para demostración de técnicas de ML en ciberseguridad.

---

**⚠️ Importante**: Este es un sistema de demostración académica. Para uso en producción, se requiere validación adicional y cumplimiento de regulaciones de seguridad locales.