# 🔒 Anti-Keylogger ML Pipeline

Un pipeline completo de Machine Learning para la detección de keyloggers usando técnicas avanzadas de ciencia de datos.

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Uso Rápido](#uso-rápido)
- [Pipeline Detallado](#pipeline-detallado)
- [Configuración](#configuración)
- [API REST](#api-rest)
- [Contribución](#contribución)

## 🎯 Descripción

Este proyecto implementa un pipeline completo de Machine Learning para detectar keyloggers usando:

- **Preprocesamiento avanzado**: Limpieza de datos, manejo de valores faltantes, detección de outliers
- **Múltiples algoritmos**: Random Forest, XGBoost, LightGBM con hyperparameter tuning
- **Evaluación comprehensiva**: Métricas detalladas, análisis de robustez, detección de drift
- **Deployment automático**: API REST, procesamiento batch, inferencia en tiempo real
- **Monitoreo**: Tracking de rendimiento, análisis de confianza de predicciones

## 📁 Estructura del Proyecto

```
Python_ML/
├── 📊 data/
│   ├── raw/              # Datos originales (CSV)
│   ├── processed/        # Datos procesados (Parquet, Pickle)
│   ├── external/         # Datos externos
│   └── features/         # Features engineered
├── 📓 notebooks/
│   └── 01_exploratory_data_analysis.ipynb
├── 🧪 data_science/
│   └── data_preprocessing.py
├── 🤖 ml_pipeline/
│   ├── training/
│   │   └── train_model.py
│   ├── evaluation/
│   │   └── evaluate_model.py
│   └── deployment/
│       └── predict_model.py
├── 💾 models/
│   ├── development/      # Modelos en desarrollo
│   ├── production/       # Modelos en producción
│   ├── evaluation/       # Reportes de evaluación
│   └── predictions/      # Resultados de predicciones
├── 📝 logs/              # Logs del pipeline
├── 🔧 config.toml        # Configuración
├── 🚀 run_pipeline.py    # Orquestador principal
└── 📄 requirements.txt   # Dependencias
```

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/Python_ML.git
cd Python_ML
```

### 2. Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar datos
Coloca tus archivos CSV en la carpeta `data/raw/`:
```bash
data/raw/
├── keylogger_dataset_small.csv
└── keylogger_dataset_large.csv
```

## 🚀 Uso Rápido

### Pipeline Completo (Recomendado)
```bash
python run_pipeline.py --stage all
```

### Etapas Individuales
```bash
# Solo preprocesamiento
python run_pipeline.py --stage preprocess

# Solo entrenamiento
python run_pipeline.py --stage train

# Solo evaluación
python run_pipeline.py --stage evaluate

# Solo predicciones
python run_pipeline.py --stage predict
```

## 🔬 Pipeline Detallado

### 1. 📊 Preprocesamiento de Datos

**Archivo**: `data_science/data_preprocessing.py`

**Características**:
- ✅ Análisis de calidad de datos automático
- ✅ Limpieza de valores faltantes y outliers
- ✅ Encoding de variables categóricas
- ✅ Normalización y escalado
- ✅ Export a múltiples formatos (Parquet, Pickle, HDF5)

**Uso**:
```python
from data_science.data_preprocessing import DataPreprocessor

preprocessor = DataPreprocessor()
df = preprocessor.load_data("data/raw/dataset.csv")
df_clean = preprocessor.clean_data(df)
preprocessor.export_processed_data(df_clean, "clean_dataset")
```

### 2. 🤖 Entrenamiento de Modelos

**Archivo**: `ml_pipeline/training/train_model.py`

**Características**:
- ✅ Múltiples algoritmos (Random Forest, XGBoost, LightGBM)
- ✅ Hyperparameter tuning con Grid Search
- ✅ Cross-validation estratificada
- ✅ Export a PKL y ONNX
- ✅ Feature importance analysis

**Uso**:
```python
from ml_pipeline.training.train_model import AdvancedModelTrainer

trainer = AdvancedModelTrainer()
summary = trainer.full_training_pipeline(
    data_path="data/processed/clean_dataset.parquet",
    target_column="class"
)
```

### 3. 📈 Evaluación de Modelos

**Archivo**: `ml_pipeline/evaluation/evaluate_model.py`

**Características**:
- ✅ Métricas comprehensivas (Accuracy, F1, ROC-AUC, etc.)
- ✅ Análisis de matriz de confusión
- ✅ Detección de data drift
- ✅ Análisis de confianza de predicciones
- ✅ Comparación automática de modelos

**Uso**:
```python
from ml_pipeline.evaluation.evaluate_model import ModelEvaluator

evaluator = ModelEvaluator()
result = evaluator.evaluate_model_comprehensive(
    model_path="models/development/best_model.pkl",
    test_data_path="data/processed/test_data.parquet",
    target_column="class"
)
```

### 4. 🎯 Deployment y Predicciones

**Archivo**: `ml_pipeline/deployment/predict_model.py`

**Características**:
- ✅ Predicción individual y batch
- ✅ API REST con FastAPI
- ✅ Procesamiento de archivos grandes por chunks
- ✅ Validación de entrada automática
- ✅ Monitoreo de rendimiento

**Uso**:
```python
from ml_pipeline.deployment.predict_model import ModelPredictor

predictor = ModelPredictor("models/production/best_model.pkl")
result = predictor.predict_single(features_array)
```

## ⚙️ Configuración

El archivo `config.toml` contiene toda la configuración del pipeline:

```toml
[pipeline]
project_name = "Anti-Keylogger ML Pipeline"
version = "1.0.0"

[data]
missing_threshold = 0.95
outlier_method = "iqr"
preferred_format = "parquet"

[models]
algorithms = ["random_forest", "xgboost", "lightgbm"]
test_size = 0.2
cv_folds = 5

[evaluation]
min_accuracy = 0.85
min_f1_score = 0.80
```

## 🌐 API REST

### Iniciar el servidor
```python
from ml_pipeline.deployment.predict_model import ModelPredictor, ModelAPI

predictor = ModelPredictor("models/production/best_model.pkl")
api = ModelAPI(predictor)
api.run(host="0.0.0.0", port=8000)
```

### Endpoints disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Estado de la API |
| `/health` | GET | Health check |
| `/predict` | POST | Predicción individual |
| `/predict/batch` | POST | Predicción batch |
| `/model/info` | GET | Información del modelo |
| `/stats` | GET | Estadísticas de uso |

### Ejemplo de uso
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"features": [1.0, 2.0, 3.0, ...]}'
```

## 📊 Jupyter Notebooks

### Análisis Exploratorio de Datos
El notebook `notebooks/01_exploratory_data_analysis.ipynb` incluye:

- 📈 Estadísticas descriptivas
- 📊 Visualizaciones de distribuciones
- 🔍 Análisis de correlaciones
- 🧹 Identificación de problemas de calidad
- 🎯 Insights para feature engineering

## 📋 Ejemplos de Uso

### Ejemplo 1: Pipeline básico
```python
# Ejecutar todo el pipeline
python run_pipeline.py --stage all

# Ver resultados
ls models/development/  # Modelos entrenados
ls models/evaluation/   # Reportes de evaluación
ls models/predictions/  # Predicciones
```

### Ejemplo 2: Entrenamiento personalizado
```python
from ml_pipeline.training.train_model import AdvancedModelTrainer

trainer = AdvancedModelTrainer()
trainer.create_model_configurations()  # Ver configuraciones
summary = trainer.full_training_pipeline(
    data_path="mi_dataset.parquet",
    target_column="mi_target"
)
print(f"Mejor modelo: {summary['best_model']}")
```

### Ejemplo 3: Predicciones en producción
```python
from ml_pipeline.deployment.predict_model import ModelPredictor, BatchProcessor

# Cargar modelo
predictor = ModelPredictor("models/production/modelo_final.pkl")

# Predicción individual
features = np.array([...])  # Tus features
result = predictor.predict_single(features)
print(f"Predicción: {result['prediction_label']}")
print(f"Confianza: {result['confidence']:.2%}")

# Procesamiento batch
batch_processor = BatchProcessor(predictor)
batch_processor.process_csv_file("nuevos_datos.csv")
```

## 🔧 Troubleshooting

### Problema: Error de importación
```bash
# Solución: Agregar al PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

### Problema: Memoria insuficiente
```python
# Usar chunks más pequeños en el config.toml
[deployment]
batch_chunk_size = 5000
```

### Problema: Modelos no encontrados
```bash
# Verificar estructura
python run_pipeline.py --stage train
ls models/development/
```

## 📈 Métricas y Monitoreo

El pipeline genera automáticamente:

- 📊 **Reportes de rendimiento**: Accuracy, F1, ROC-AUC
- 🎯 **Análisis de confianza**: Distribución de probabilidades
- 📉 **Detección de drift**: Cambios en distribución de datos
- ⏱️ **Métricas de latencia**: Tiempo de predicción
- 💾 **Uso de recursos**: CPU y memoria

## 🤝 Contribución

1. Fork del proyecto
2. Crear branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📜 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Autores

- **Data Science Team** - *Trabajo inicial* - [TuPerfil](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- Comunidad de Machine Learning
- Contribuidores de scikit-learn, XGBoost, LightGBM
- Equipo de FastAPI y Jupyter

---

⭐ **¡Si este proyecto te ayuda, dale una estrella!** ⭐