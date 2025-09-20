# Organización del Workspace - Sistema Anti-Keylogger

## 📁 Estructura Principal

### 🚀 Scripts Principales (Directorio Raíz)
- `simple_launcher.py` - **Launcher principal del sistema antivirus**
- `install_antivirus.py` - **Instalador de dependencias y configuración**  
- `test_antivirus.py` - **Suite de pruebas principal**

### 🛠️ Herramientas (tools/)
- `test_ml_detection.py` - Pruebas específicas del detector ML
- `fix_windows_logging.py` - Corrección de problemas de encoding en Windows
- `audit_workspace.py` - Auditoría y análisis del workspace
- `inspect_onnx_quick.py` - Inspección de modelos ONNX
- `maintenance.py` - Herramientas de mantenimiento
- `deploy.py` - Scripts de deployment
- `antivirus_launcher.py` - Launcher alternativo

### 🤖 Sistema Antivirus (antivirus/)
- `core/` - Motor principal del antivirus
- `detectors/` - Detectores (ML, comportamiento, red)
- `monitors/` - Monitores (red, procesos, archivos)
- `utils/` - Utilidades compartidas

### 🧠 Pipeline ML (ml_pipeline/, scripts/)
- `training/` - Entrenamiento de modelos
- `evaluation/` - Evaluación y métricas
- `deployment/` - Deployment de modelos
- `utils/` - Utilidades ML

### 📊 Modelos (models/)
- `development/` - Modelos entrenados (ONNX, PKL)
- `metadata.json` - Metadatos de modelos
- `label_classes.json` - Clases de predicción

### 💾 Datos (DATOS/)
- `Keylogger_Detection_Dataset.csv` - Dataset principal
- `Keylogger_Detection.csv` - Dataset procesado

### 🗄️ Backup (backup/)
- Versiones anteriores y archivos históricos
- **Nota**: Se eliminaron duplicados durante la limpieza

## 🚀 Uso Rápido

```bash
# Instalación y configuración
python install_antivirus.py

# Prueba básica del sistema
python simple_launcher.py --test

# Pruebas completas
python test_antivirus.py

# Monitoreo en tiempo real
python simple_launcher.py --monitor
```

## 🧹 Limpieza Realizada

### Archivos Duplicados Eliminados:
- `backup/scripts/train_from_datos.py` (duplicado de scripts/)
- `backup/tools/antivirus_control.py` (múltiples duplicados)
- Varios duplicados de `predecir_keylogger.py` en backup/

### Organización Aplicada:
- Scripts utilitarios movidos a `tools/`
- Mantenidos en raíz solo los scripts principales
- Estructura clara por funcionalidad

---
**Generado automáticamente por workspace_cleaner.py**
