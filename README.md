# 🛡️ Anti-Keylogger con Machine Learning

## Descripción

Anti-Keylogger es un sistema avanzado de ciberseguridad diseñado para detectar y bloquear keyloggers en tiempo real. Utiliza modelos de Machine Learning, análisis de comportamiento y monitoreo de red, archivos y procesos para proteger la información sensible de usuarios y empresas.

## Características principales

- **Detección inteligente:** Modelos ML entrenados para identificar patrones de keyloggers, incluso variantes desconocidas.
- **Monitoreo multidimensional:** Vigilancia continua de archivos, procesos y conexiones de red.
- **Arquitectura modular:** Componentes independientes y escalables.
- **Dashboard web:** Visualización de métricas, logs y amenazas detectadas.
- **Bajo consumo de recursos:** Optimizado para funcionar en equipos de producción.

## Estructura del proyecto

```
ANTIVIRUS_PRODUCTION/
├── antivirus/           # Código principal
├── models/              # Modelos ML (ONNX, PKL, JSON)
├── config/              # Configuración TOML y JSON
├── simple_launcher.py   # Ejecución básica
├── antivirus_launcher.py# Ejecución completa
├── requirements.txt     # Dependencias
├── web_api/             # API y dashboard web
└── logs/                # Registros de actividad
```

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/KrCrimson/proyecto-Anti-keylogger.git
   ```
2. Instala las dependencias mínimas:
   ```bash
   pip install -r ANTIVIRUS_PRODUCTION/requirements_minimal.txt
   ```
3. Ejecuta el antivirus:
   ```bash
   cd ANTIVIRUS_PRODUCTION
   python simple_launcher.py
   ```

## Uso del dashboard web

1. Instala las dependencias del API:
   ```bash
   pip install -r ANTIVIRUS_PRODUCTION/web_api/requirements.txt
   ```
2. Ejecuta el dashboard:
   ```bash
   cd ANTIVIRUS_PRODUCTION/web_api
   python main.py
   ```
3. Accede a: [http://localhost:8000](http://localhost:8000)

## Tecnologías utilizadas

- Python 3.11+
- scikit-learn, ONNX Runtime
- pandas, numpy, joblib
- psutil, logging
- Railway (despliegue cloud)
- Marp (presentaciones)

## Métricas y resultados

- **Accuracy ML:** 73.78%
- **CPU:** 14% | **RAM:** 58%
- **Conexiones monitoreadas:** 108
- **Sistema:** 100% funcional en producción

## Roadmap

- Mejorar precisión ML (objetivo 85%+)
- Interfaz gráfica para usuarios finales
- Testing automatizado
- Integración cloud y versión comercial

## Contacto

- **GitHub:** [proyecto-Anti-keylogger](https://github.com/KrCrimson/proyecto-Anti-keylogger)
- **Documentación:** Ver carpeta `MD's Explicativos/`
