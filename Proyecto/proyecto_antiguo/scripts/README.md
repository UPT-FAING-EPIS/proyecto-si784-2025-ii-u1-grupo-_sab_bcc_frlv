# Scripts Directory

Este directorio contiene todos los scripts organizados del proyecto ML Pipeline.

## Estructura

```
scripts/
├── simple_pipeline.py              # Pipeline completo simplificado
├── run_pipeline.py                 # Orquestador principal del pipeline
├── main.py                        # Punto de entrada principal
├── training/
│   └── train_large_model.py       # Entrenamiento de modelos avanzados
├── evaluation/
│   └── advanced_evaluation.py     # Evaluación exhaustiva de modelos
├── deployment/
│   ├── api_server.py              # Servidor API REST
│   └── convert_to_onnx.py         # Conversión de modelos a ONNX
└── utils/
    ├── process_large_dataset.py   # Procesamiento de datasets grandes
    └── use_trained_model.py       # Utilidades para usar modelos entrenados
```

## Uso

### Scripts Principales
```bash
# Pipeline completo simplificado
python scripts/simple_pipeline.py

# Pipeline completo avanzado
python scripts/run_pipeline.py --stage all

# Aplicación principal
python scripts/main.py
```

### Scripts de Entrenamiento
```bash
# Entrenamiento avanzado
python scripts/training/train_large_model.py
```

### Scripts de Evaluación
```bash
# Evaluación exhaustiva
python scripts/evaluation/advanced_evaluation.py
```

### Scripts de Deployment
```bash
# Servidor API
python scripts/deployment/api_server.py

# Conversión ONNX
python scripts/deployment/convert_to_onnx.py
```

### Scripts de Utilidades
```bash
# Procesamiento de datasets
python scripts/utils/process_large_dataset.py

# Usar modelo entrenado
python scripts/utils/use_trained_model.py
```