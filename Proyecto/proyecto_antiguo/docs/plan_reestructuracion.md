# PLAN DE REESTRUCTURACIÓN DEL PROYECTO ANTI-KEYLOGGER

## PROBLEMAS IDENTIFICADOS

### 1. ARCHIVOS/CARPETAS A ELIMINAR
- .vscode/ - Configuración del editor (debería ir en .gitignore)
- .pytest_cache/ - Cache de testing (debería ir en .gitignore)
- AntiKeyloggerApp/onnxruntime-1.22.2/ - Librería completa (130MB+), usar pip install
- backup/ - Versiones antiguas obsoletas
- assignments/ - Parece trabajo académico no relacionado
- __pycache__/ - Cache de Python (debería ir en .gitignore)

### 2. SCRIPTS DUPLICADOS
- scripts/convertidorONNX.py vs scripts/convert_pkl_to_onnx.py (MISMO PROPÓSITO)
- scripts/train_colab.py vs scripts/train_from_datos.py (LÓGICA SIMILAR)
- Múltiples versiones en workbench/ (antivirus/, antivirus_cli_interactivo/, antivirus_monitor_py/)

### 3. ESTRUCTURA CONFUSA
- Lógica principal dispersa entre /scripts y /workbench/antivirus_monitor_py
- AntiKeyloggerApp (C#) desconectado del flujo Python principal
- Archivos huérfanos en raíz (articulo_keylogger.tex, generar_alerta_keylogger.py)

## ESTRUCTURA PROPUESTA (LIMPIA)

```
Python_ML/
├── src/                          # Código fuente principal
│   ├── core/                     # Lógica central
│   │   ├── scanner.py
│   │   ├── file_monitor.py
│   │   ├── feature_extractor.py
│   │   ├── predictor.py
│   │   └── threat_detector.py
│   ├── interfaces/               # Interfaces de usuario
│   │   └── console_interface.py
│   ├── utils/                    # Utilidades
│   │   ├── config_manager.py
│   │   ├── log_manager.py
│   │   └── alert_manager.py
│   └── models/                   # Gestión de modelos ML
│       ├── model_trainer.py
│       └── model_converter.py
├── scripts/                      # Scripts de entrenamiento y utilidades
│   ├── train_model.py           # Unificado de train_from_datos.py
│   ├── convert_to_onnx.py       # Unificado de convert_pkl_to_onnx.py
│   ├── verify_model.py          # Verificación ONNX vs PKL
│   └── generate_test_alert.py   # Para pruebas
├── data/                        # Datasets
│   └── keylogger_dataset.csv
├── models/                      # Modelos entrenados
│   ├── *.pkl
│   ├── *.onnx
│   └── metadata.json
├── config/                      # Configuraciones
│   └── settings.json
├── logs/                        # Archivos de log
├── tests/                       # Tests unitarios
├── docs/                        # Documentación
│   ├── README.md
│   ├── requerimientos.md
│   ├── diagramas.md
│   └── modelo_logico.md
├── requirements.txt             # Dependencias Python
├── .gitignore                   # Archivos a ignorar
└── main.py                      # Punto de entrada principal
```

## ACCIONES RECOMENDADAS

### FASE 1: LIMPIEZA INMEDIATA
1. Eliminar carpetas problemáticas:
   ```bash
   rm -rf .vscode .pytest_cache AntiKeyloggerApp/onnxruntime-1.22.2 backup assignments
   ```

2. Crear .gitignore:
   ```
   __pycache__/
   *.pyc
   .pytest_cache/
   .vscode/
   *.log
   .env
   ```

3. Consolidar scripts duplicados:
   - Mantener convert_pkl_to_onnx.py (es más específico)
   - Mantener train_from_datos.py (es más robusto)
   - Eliminar convertidorONNX.py y train_colab.py

### FASE 2: REESTRUCTURACIÓN
1. Mover código de workbench/antivirus_monitor_py/ a src/
2. Crear main.py como punto de entrada único
3. Unificar configuración en config/
4. Centralizar documentación en docs/

### FASE 3: INTEGRACIÓN
1. El AntiKeyloggerApp (C#) debería ser un proyecto separado
2. Usar pip install onnxruntime en lugar de incluir la librería
3. Crear API REST para integración entre C# y Python

## BENEFICIOS ESPERADOS

✅ Reducción de tamaño del repo (>100MB menos)
✅ Estructura clara y profesional
✅ Eliminación de duplicación de código
✅ Mejor mantenibilidad y escalabilidad
✅ Separación clara de responsabilidades
✅ Facilita colaboración y CI/CD

## ARCHIVOS CLAVE A MANTENER

- workbench/antivirus_monitor_py/monitor.py (CORE del sistema)
- scripts/train_from_datos.py (entrenamiento robusto)
- scripts/convert_pkl_to_onnx.py (conversión específica)
- modelos/ (artefactos entrenados)
- requerimientos_anti_keylogger.md (especificaciones)
- diagramas.md (arquitectura)

## NOTA SOBRE AntiKeyloggerApp

El proyecto C# parece ser una implementación paralela/alternativa:
- Usa Microsoft.ML.OnnxRuntime
- Intenta cargar "../modelo_keylogger.onnx"
- Podría ser útil como cliente de la API Python
- Debería ser proyecto separado con su propia solución

RECOMENDACIÓN: Mantener solo el núcleo Python, crear API REST, 
y que el C# sea un cliente opcional.