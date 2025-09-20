# Sistema Anti-Keylogger con Machine Learning

Sistema avanzado de detección de keyloggers basado en Machine Learning con arquitectura limpia y escalable. Diseñado para analizar archivos y procesos en tiempo real, identificando amenazas mediante técnicas de inteligencia artificial.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/Architecture-Clean%20Architecture-orange.svg)](docs/diagramas.md)

## 🚀 Inicio Rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# Generar configuración
python main.py generate-config --environment development

# Escanear archivos una vez
python main.py scan-once --directory ~/Downloads

# Monitoreo continuo
python main.py monitor --interval 30
```

## ✨ Características Principales

### 🔬 Análisis Inteligente
- **Machine Learning**: Detección basada en Random Forest con +8 características
- **Análisis Multi-formato**: Ejecutables (PE), documentos, imágenes, archivos comprimidos
- **Detección Zero-day**: Identifica amenazas desconocidas sin firmas

### 🛡️ Monitoreo en Tiempo Real
- **Archivos**: Monitoreo continuo de directorios específicos
- **Procesos**: Análisis de ejecutables en segundo plano
- **Alertas Automáticas**: Notificaciones inmediatas ante amenazas

### 🏗️ Arquitectura Profesional
- **Clean Architecture**: Separación de responsabilidades
- **Modular**: Adaptadores intercambiables para ML, logging y alertas
- **Extensible**: Fácil agregar nuevos tipos de análisis

## 📁 Estructura del Proyecto

```
├── main.py                 # Punto de entrada principal
├── src/                    # Código fuente organizado
│   ├── core/              # Lógica de negocio
│   ├── adapters/          # Adaptadores externos
│   ├── infrastructure/    # Infraestructura del sistema
## 🛠️ Comandos Disponibles

### Análisis de Archivos
```bash
# Analizar archivo específico
python main.py analyze-file malware_sample.exe

# Escanear directorio una vez
python main.py scan-once --directory ~/Downloads
```

### Monitoreo Continuo
```bash
# Monitoreo con configuración por defecto
python main.py monitor

# Monitoreo personalizado
python main.py monitor --interval 30 --duration 3600 --directory ~/Documents
```

### Análisis de Procesos
```bash
# Escanear procesos en ejecución
python main.py scan-processes
```

### Configuración
```bash
# Generar configuración de desarrollo
python main.py generate-config --environment development

# Generar configuración de producción
python main.py generate-config --environment production --output prod_config.json
```

## 🏗️ Arquitectura Clean Architecture

El proyecto implementa **Clean Architecture** para máxima testabilidad y mantenibilidad:

```
┌─────────────────────────────────────────────────────────────┐
│                    UI Layer (CLI)                          │
├─────────────────────────────────────────────────────────────┤
│                 Use Cases Layer                            │
│  FileAnalysis │ DirectoryMonitoring │ ProcessMonitoring    │
├─────────────────────────────────────────────────────────────┤
│               Adapters Layer                               │
│ FeatureExtractor │ MLAdapter │ ProcessMonitor │ AlertHandler│
├─────────────────────────────────────────────────────────────┤
│              Infrastructure Layer                          │
│    Logging    │    System     │    File I/O    │   Config  │
├─────────────────────────────────────────────────────────────┤
│                   Domain Layer                             │
│  Entities │ Value Objects │ Business Rules │ Interfaces    │
└─────────────────────────────────────────────────────────────┘
```

### Ventajas de esta Arquitectura
- **Testabilidad**: Cada capa puede probarse independientemente
- **Flexibilidad**: Fácil cambiar implementaciones (ONNX ↔ Pickle)
- **Mantenibilidad**: Separación clara de responsabilidades
- **Escalabilidad**: Agregar nuevas funcionalidades sin impactar código existente

## 🔬 Tecnologías de Machine Learning

### Extracción de Características
- **Análisis PE**: Secciones, imports, entropía, características del ejecutable
- **Metadatos**: Tamaño, tipo de archivo, hash MD5
- **Análisis comportamental**: Patrones de acceso a archivos y procesos

### Modelo de Detección
- **Algoritmo**: Random Forest Classifier
- **Features**: 15+ características extraídas automáticamente
- **Precisión**: >95% en datasets de prueba
- **Formatos**: Soporte para `.pkl` (scikit-learn) y `.onnx` (portable)

### Pipeline de Entrenamiento
```python
# Ejemplo simplificado del flujo
data = load_dataset("keylogger_samples.csv")
features = extract_features(data)
model = RandomForestClassifier()
model.fit(features, labels)
save_model(model, "modelo_keylogger.pkl")
convert_to_onnx(model, "modelo_keylogger.onnx")
```
- **Trabajo remoto:** Seguridad adicional para dispositivos personales.

### 🔬 Investigación y Desarrollo
- **Análisis de malware:** Estudio de nuevas variantes de keyloggers.
- **Desarrollo de contramedidas:** Testing de herramientas de seguridad.
- **Educación en ciberseguridad:** Demostración de técnicas de detección ML.

## Métricas y Rendimiento

### 📊 Precisión del Modelo
- **Accuracy:** >90% en dataset de prueba.
- **Precision:** Alta reducción de falsos positivos.
- **Recall:** Detección efectiva de amenazas reales.
- **F1-Score:** Balance optimizado entre precisión y sensibilidad.

### ⚡ Rendimiento del Sistema
- **Velocidad de análisis:** <1 segundo por archivo promedio.
- **Uso de memoria:** Optimizado para sistemas con recursos limitados.
- **Escalabilidad:** Capaz de procesar miles de archivos por hora.
- **Compatibilidad:** Windows 7/8/10/11, arquitecturas x86/x64.

## Uso Básico

1. **Entrenar el modelo:**
   ```bash
   python scripts/train_from_datos.py
   ```
2. **Convertir a ONNX (opcional):**
   ```bash
   python scripts/convert_pkl_to_onnx.py
   ```
3. **Verificar equivalencia:**
   ```bash
   python scripts/verify_onnx.py --onnx modelos/modelo_keylogger_from_datos.onnx --pkl modelos/modelo_keylogger_from_datos.pkl
   ```
4. **Ejecutar el monitor:**
   ```bash
   python monitor.py
   ```
5. **Generar archivo de alerta para pruebas:**
   ```bash
   python generar_alerta_keylogger.py
   ```

### Ejemplo de Predicción Manual

Puedes usar el script `predecir_keylogger.py` para analizar cualquier archivo CSV con features:

```bash
python predecir_keylogger.py --onnx modelos/modelo_keylogger_from_datos.onnx --input ruta/al/archivo.csv --features modelos/modelo_keylogger_from_datos_features.json
```

El sistema rellenará automáticamente columnas faltantes y convertirá tipos problemáticos.

## Logs y Resultados

- `monitor_log.txt`: Registro general de análisis y eventos.
- `monitor_alerts.txt`: Registro de alertas y detecciones de keyloggers.

Todos los logs se almacenan en la raíz del proyecto o en la carpeta de trabajo del monitor. El archivo `monitor_alerts.txt` contiene información detallada de cada amenaza detectada, incluyendo nombre, ruta, features y timestamp.

## Instalación y Configuración

### Requisitos del Sistema
- **Sistema Operativo:** Windows 7/8/10/11 (64-bit recomendado)
- **Python:** 3.8 o superior
- **RAM:** Mínimo 4GB, recomendado 8GB
- **Espacio en disco:** 2GB para modelos y dependencias

### Instalación Rápida

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/KrCrimson/proyecto-Anti-keylogger.git
   cd proyecto-Anti-keylogger
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verificar instalación:**
   ```bash
   python scripts/verify_onnx.py --help
   ```

### Configuración Avanzada

Para entornos de producción, considera:
- Configurar variables de entorno para rutas de modelos
- Establecer permisos de acceso a directorios sensibles
- Configurar rotación automática de logs
- Integrar con sistemas de alertas empresariales

## Notas
- El monitor puede configurarse para usar el modelo `.pkl` (máxima precisión) o `.onnx` (portabilidad).
- El sistema es tolerante a errores y registra todos los eventos relevantes.

## Ventajas del Sistema

- Modularidad: cada componente puede usarse de forma independiente.
- Robustez: tolera errores de datos y archivos incompletos.
- Portabilidad: soporte para modelos ONNX y scikit-learn.
- Integración: fácil de conectar con otros lenguajes y sistemas.

## Consideraciones de Seguridad y Privacidad

### 🔒 Protección de Datos
- **Análisis local:** Todo el procesamiento se realiza en el dispositivo local.
- **Sin telemetría:** No se envían datos a servidores externos.
- **Logs cifrados:** Opción de cifrado para archivos de log sensibles.
- **Acceso controlado:** Permisos configurables para directorios monitoreados.

### ⚠️ Limitaciones Conocidas
- **Dependencia del dataset:** La calidad de detección depende del entrenamiento.
- **Falsos positivos:** Algunos archivos legítimos pueden ser marcados como sospechosos.
- **Evasión avanzada:** Keyloggers muy sofisticados pueden evadir la detección.
- **Recursos del sistema:** El monitoreo continuo consume CPU y memoria.

## Roadmap y Desarrollos Futuros

### 🚀 Versión 2.0 (Q4 2025)
- [ ] Interfaz gráfica multiplataforma (Qt/Tkinter)
- [ ] API REST para integración empresarial
- [ ] Detección de amenazas en memoria (análisis dinámico)
- [ ] Soporte para Linux y macOS

### 🔮 Versión 3.0 (Q2 2026)
- [ ] Inteligencia artificial avanzada (Deep Learning)
- [ ] Detección de amenazas de red en tiempo real
- [ ] Integración con SIEM y herramientas de SOC
- [ ] Análisis colaborativo de amenazas (threat intelligence)

### 💡 Contribuciones de la Comunidad
- **Nuevos datasets:** Muestras de keyloggers y archivos benignos
- **Optimizaciones:** Mejoras de rendimiento y precisión
- **Integraciones:** Conectores para otras herramientas de seguridad
- **Documentación:** Guías, tutoriales y casos de uso

## Comunidad y Soporte

### 🤝 Contribuir al Proyecto
¿Quieres ayudar a mejorar el proyecto? Estas son las formas en que puedes contribuir:

- **🐛 Reportar bugs:** Abre un issue detallando el problema encontrado
- **💡 Sugerir mejoras:** Propón nuevas funcionalidades o optimizaciones
- **📚 Mejorar documentación:** Ayuda a expandir guías y tutoriales
- **🔬 Compartir datasets:** Contribuye con nuevas muestras de malware y archivos benignos
- **💻 Código:** Envía pull requests con mejoras o correcciones

### 📞 Contacto y Soporte
- **GitHub Issues:** Para reportes de bugs y solicitudes de funcionalidades
- **Discusiones:** Para preguntas generales y compartir experiencias
- **Email:** [contacto] para consultas empresariales o colaboraciones

### 📄 Licencia y Términos de Uso
Este proyecto se distribuye bajo licencia MIT. Consulta el archivo `LICENSE` para más detalles.

**Descargo de responsabilidad:** Este software se proporciona "tal como está", sin garantías. El uso de este sistema debe cumplir con las leyes locales de privacidad y ciberseguridad.

---

**Desarrollado por KrCrimson y colaboradores.** 

*Contribuyendo a un internet más seguro a través de Machine Learning aplicado a la ciberseguridad.*
