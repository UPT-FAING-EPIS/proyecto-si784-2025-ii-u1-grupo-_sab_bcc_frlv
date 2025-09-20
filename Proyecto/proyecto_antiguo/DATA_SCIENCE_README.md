# Estructura de Data Science y ML Pipeline

Este directorio contiene toda la infraestructura de Data Science y Machine Learning del proyecto.

## 📊 Estructura de Datos

```
data/
├── raw/                    # Datos originales (sin modificar)
│   ├── keylogger_dataset_small.csv   # ~38k registros (15MB)
│   └── keylogger_dataset_large.csv   # ~500k registros (298MB)
├── processed/              # Datos limpios y procesados
├── external/               # Datos externos o de terceros
└── features/               # Features engineering results
```

## 🧪 Notebooks de Exploración

```
notebooks/
├── 01_exploratory_data_analysis.ipynb    # EDA inicial
├── 02_data_cleaning.ipynb                # Limpieza de datos
├── 03_feature_engineering.ipynb          # Ingeniería de características
├── 04_model_training.ipynb               # Entrenamiento de modelos
└── 05_model_evaluation.ipynb             # Evaluación y métricas
```

## 🤖 Pipeline de ML

```
ml_pipeline/
├── training/
│   ├── train_model.py              # Script de entrenamiento
│   ├── feature_engineering.py      # Pipeline de features
│   └── data_preprocessing.py       # Preprocesamiento
├── evaluation/
│   ├── evaluate_model.py           # Evaluación de modelos
│   ├── cross_validation.py         # Validación cruzada
│   └── metrics_calculation.py      # Cálculo de métricas
└── deployment/
    ├── model_converter.py          # Conversión PKL → ONNX
    └── model_validator.py          # Validación de modelos
```

## 🎯 Modelos Entrenados

```
models/
├── development/            # Modelos en desarrollo
├── production/             # Modelos en producción
├── experiments/            # Experimentos y A/B testing
└── metadata/              # Metadatos y configuraciones
```

## 🚀 Flujo de Trabajo

### 1. Exploración de Datos
```bash
jupyter notebook notebooks/01_exploratory_data_analysis.ipynb
```

### 2. Limpieza de Datos
```bash
python ml_pipeline/training/data_preprocessing.py
```

### 3. Entrenamiento
```bash
python ml_pipeline/training/train_model.py --dataset processed/clean_dataset.parquet
```

### 4. Evaluación
```bash
python ml_pipeline/evaluation/evaluate_model.py --model models/latest/model.pkl
```

### 5. Conversión y Deployment
```bash
python ml_pipeline/deployment/model_converter.py --input models/latest/model.pkl
```

## 📈 Mejoras Propuestas

### Formato de Datos
- **De CSV a Parquet**: Mejor compresión y velocidad
- **De CSV a DuckDB**: Consultas SQL rápidas
- **Particionamiento**: Para datasets grandes

### Algoritmos ML
- **XGBoost**: Para mejor rendimiento
- **LightGBM**: Para datasets grandes
- **AutoML**: Optimización automática
- **Deep Learning**: Redes neuronales para detección avanzada

### MLOps
- **MLflow**: Tracking de experimentos
- **DVC**: Versionado de datos
- **Docker**: Containerización de modelos
- **CI/CD**: Pipeline automatizado