# 🚀 Guía de Comandos del Pipeline ML - Ejecución por Grupos

Este archivo contiene todos los comandos organizados por carpetas para ejecutar cada parte del código del pipeline ML.

## 📋 Pre-requisitos

```bash
# 1. Verificar Python instalado
python --version

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Verificar estructura de datos
ls data/raw/
```

---

## 🏁 Scripts Principales (Carpeta: `scripts/`)

### 🚀 Pipeline Básico - Inicio Rápido
```bash
# Ejecutar pipeline completo en 3-5 segundos
python scripts/simple_pipeline.py

# Resultado: Modelo entrenado + predicciones + datos procesados
# Ideal para: Desarrollo rápido y testing
```

### ⚙️ Pipeline Avanzado - Orquestador Completo
```bash
# Pipeline completo con todas las etapas
python scripts/run_pipeline.py --stage all

# O ejecutar etapas individuales:
python scripts/run_pipeline.py --stage preprocess
python scripts/run_pipeline.py --stage train
python scripts/run_pipeline.py --stage evaluate
python scripts/run_pipeline.py --stage predict
```

### 🎯 Aplicación Principal
```bash
# Ejecutar aplicación principal del sistema
python scripts/main.py

# Otras opciones disponibles (si aplican):
python scripts/main.py --help
```

---

## 🚀 Entrenamiento (Carpeta: `scripts/training/`)

### 📊 Entrenamiento de Modelos Avanzados
```bash
# Entrenar modelo con dataset grande (alta precisión)
python scripts/training/train_large_model.py

# Resultado: Modelo RF con 88.25% accuracy
# Tiempo: ~2-5 minutos dependiendo del dataset
# Output: models/development/rf_large_model_*.pkl
```

**Ejemplo de flujo completo de entrenamiento:**
```bash
# 1. Procesar datos grandes (si es necesario)
python scripts/utils/process_large_dataset.py

# 2. Entrenar modelo avanzado
python scripts/training/train_large_model.py

# 3. Verificar modelo entrenado
ls models/development/rf_large_model_*.pkl
```

---

## 📊 Evaluación (Carpeta: `scripts/evaluation/`)

### 🔍 Evaluación Exhaustiva de Modelos
```bash
# Evaluar modelo con métricas detalladas
python scripts/evaluation/advanced_evaluation.py

# Resultado: Reporte completo con ROC AUC, matriz de confusión, etc.
# Output: models/evaluation/evaluation_report_*.json
```

**Ejemplo de flujo de evaluación:**
```bash
# 1. Asegurar que hay modelos entrenados
ls models/development/

# 2. Ejecutar evaluación avanzada
python scripts/evaluation/advanced_evaluation.py

# 3. Ver reportes generados
ls models/evaluation/
cat models/evaluation/evaluation_report_*.json
```

---

## 🌐 Deployment (Carpeta: `scripts/deployment/`)

### 🔄 Conversión a ONNX (Optimización)
```bash
# Convertir modelo sklearn a ONNX (10x más rápido)
python scripts/deployment/convert_to_onnx.py

# Resultado: Modelo optimizado para producción
# Output: models/development/keylogger_model_*.onnx
# Speedup: ~10x mejora en velocidad
```

### 🌐 Servidor API REST
```bash
# Iniciar servidor API para predicciones en tiempo real
python scripts/deployment/api_server.py

# Servidor disponible en: http://localhost:8000
# Endpoints:
#   POST /predict - Predicción individual
#   POST /predict/batch - Predicción por lotes
#   GET /health - Estado del servidor
#   GET /model/info - Información del modelo
```

**Ejemplo de flujo de deployment:**
```bash
# 1. Convertir modelo a ONNX
python scripts/deployment/convert_to_onnx.py

# 2. Iniciar servidor API (en background)
python scripts/deployment/api_server.py &

# 3. Probar API (en otra terminal)
curl -X POST "http://localhost:8000/health"
```

---

## 🛠️ Utilidades (Carpeta: `scripts/utils/`)

### 📦 Procesamiento de Datasets Grandes
```bash
# Procesar dataset grande por chunks
python scripts/utils/process_large_dataset.py

# Resultado: Muestra optimizada de 50k registros
# Input: data/raw/keylogger_dataset_large.csv (297MB)
# Output: data/processed/dataset_large_sample.parquet
```

### 🤖 Uso de Modelos Entrenados
```bash
# Cargar y probar modelo más reciente
python scripts/utils/use_trained_model.py

# Resultado: Predicciones de muestra + estadísticas del modelo
# Muestra: 10 predicciones con confianza
# Estadísticas: Accuracy, F1-Score, features usadas
```

**Ejemplo de flujo de utilidades:**
```bash
# 1. Procesar datos grandes
python scripts/utils/process_large_dataset.py

# 2. Verificar resultado
ls data/processed/dataset_large_sample.parquet

# 3. Probar modelo entrenado
python scripts/utils/use_trained_model.py
```

---

## 📊 Análisis Exploratorio (Carpeta: `notebooks/`)

### 🔍 Análisis de Datos Interactivo
```bash
# Iniciar Jupyter Notebook
jupyter notebook

# Abrir notebook específico
jupyter notebook notebooks/01_exploratory_data_analysis.ipynb

# O ejecutar todas las celdas automáticamente
jupyter nbconvert --execute notebooks/01_exploratory_data_analysis.ipynb
```

---

## 🎯 Flujos de Trabajo Completos

### 🚀 Flujo 1: Desarrollo Rápido (3-5 minutos)
```bash
# Pipeline completo básico
python scripts/simple_pipeline.py

# Verificar resultados
python scripts/utils/use_trained_model.py

# Ver archivos generados
ls models/development/
ls models/predictions/
```

### 🔬 Flujo 2: Investigación Avanzada (10-15 minutos)
```bash
# 1. Análisis exploratorio
jupyter notebook notebooks/01_exploratory_data_analysis.ipynb

# 2. Procesar datos grandes
python scripts/utils/process_large_dataset.py

# 3. Entrenar modelo avanzado
python scripts/training/train_large_model.py

# 4. Evaluar exhaustivamente
python scripts/evaluation/advanced_evaluation.py

# 5. Verificar resultados
ls models/development/rf_large_model_*.pkl
ls models/evaluation/evaluation_report_*.json
```

### 🌐 Flujo 3: Producción (5-10 minutos)
```bash
# 1. Asegurar modelo entrenado
python scripts/training/train_large_model.py

# 2. Optimizar para producción
python scripts/deployment/convert_to_onnx.py

# 3. Iniciar servidor API
python scripts/deployment/api_server.py

# 4. Probar API (en otra terminal)
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/model/info"
```

### 🔄 Flujo 4: Pipeline Completo Avanzado (15-20 minutos)
```bash
# 1. Preprocesamiento
python scripts/run_pipeline.py --stage preprocess

# 2. Entrenamiento
python scripts/run_pipeline.py --stage train

# 3. Evaluación
python scripts/run_pipeline.py --stage evaluate

# 4. Predicción
python scripts/run_pipeline.py --stage predict

# O todo junto:
python scripts/run_pipeline.py --stage all
```

---

## 🔧 Comandos de Verificación

### 📋 Verificar Estado del Sistema
```bash
# Ver estructura de archivos
tree scripts/ models/ data/

# Verificar modelos disponibles
ls -la models/development/

# Verificar datos procesados
ls -la data/processed/

# Verificar predicciones
ls -la models/predictions/
```

### 🧪 Comandos de Testing
```bash
# Test rápido: Pipeline básico
python scripts/simple_pipeline.py

# Test intermedio: Usar modelo
python scripts/utils/use_trained_model.py

# Test avanzado: API (verificar imports)
python -c "from scripts.deployment.api_server import load_model; print('✅ API OK')"

# Test completo: Evaluación
python scripts/evaluation/advanced_evaluation.py
```

---

## 📊 Resumen de Outputs por Comando

| Comando | Output Principal | Ubicación | Tiempo Aprox. |
|---------|------------------|-----------|---------------|
| `simple_pipeline.py` | Modelo RF básico | `models/development/rf_model_*.pkl` | 3-5 seg |
| `train_large_model.py` | Modelo RF avanzado | `models/development/rf_large_model_*.pkl` | 2-5 min |
| `advanced_evaluation.py` | Reporte de evaluación | `models/evaluation/evaluation_report_*.json` | 1-3 min |
| `convert_to_onnx.py` | Modelo ONNX optimizado | `models/development/keylogger_model_*.onnx` | 30 seg |
| `api_server.py` | Servidor REST | `http://localhost:8000` | Inmediato |
| `process_large_dataset.py` | Dataset muestreado | `data/processed/dataset_large_sample.parquet` | 1-2 min |
| `use_trained_model.py` | Predicciones demo | Consola + stats | 5-10 seg |

---

## 🎯 Comandos por Objetivo

### 🎯 Para Desarrollo/Testing
```bash
python scripts/simple_pipeline.py
python scripts/utils/use_trained_model.py
```

### 🎯 Para Investigación/Análisis
```bash
jupyter notebook notebooks/01_exploratory_data_analysis.ipynb
python scripts/evaluation/advanced_evaluation.py
```

### 🎯 Para Producción
```bash
python scripts/deployment/convert_to_onnx.py
python scripts/deployment/api_server.py
```

### 🎯 Para Datasets Grandes
```bash
python scripts/utils/process_large_dataset.py
python scripts/training/train_large_model.py
```

---

## 🚀 Quick Start - Comandos Mínimos

```bash
# 1. Pipeline básico (OBLIGATORIO - empezar aquí)
python scripts/simple_pipeline.py

# 2. Ver resultados (RECOMENDADO)
python scripts/utils/use_trained_model.py

# 3. API para producción (OPCIONAL)
python scripts/deployment/api_server.py
```

**¡Con estos 3 comandos tienes un sistema ML completo funcionando!** 🎉