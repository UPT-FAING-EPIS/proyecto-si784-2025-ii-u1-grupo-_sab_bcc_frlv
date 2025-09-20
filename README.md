<<<<<<< HEAD
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
=======
# Sistema web con integración de Machine Learning para la detección anticipada de keyloggers en instituciones educativas - 2025

## 👥 Integrantes del Proyecto
| Nombre | Código de Estudiante |
|--------|----------------------|
| Sebastián Arce Bracamonte | 2019062986 |
| Brant Antony Chata Choque | 2021072615 |

---

## 📌 Introducción
En el contexto actual, las instituciones educativas están expuestas a diversos riesgos de ciberseguridad. Entre ellos, los **keyloggers** representan una amenaza crítica, ya que capturan las pulsaciones del teclado para robar información sensible como credenciales de acceso, datos personales o evaluaciones en línea.  
Este proyecto propone un **sistema web basado en Machine Learning** que permite la **detección anticipada de keyloggers** en equipos de las instituciones educativas, garantizando la protección de datos y la continuidad de las actividades académicas.

---

## 🎯 Objetivo del Sistema
Desarrollar una plataforma web que:
- Integre algoritmos de Machine Learning para identificar comportamientos sospechosos en tiempo real.
- Brinde a los administradores escolares un panel de control intuitivo para la gestión de amenazas.
- Permita tomar acciones rápidas (cuarentena, eliminación, bloqueo) frente a potenciales keyloggers detectados.
- Escale para dar soporte a múltiples instituciones y usuarios de forma simultánea.

---

## 🛠️ Tecnologías Propuestas
- **Backend:** Python (Django / Flask)
- **Machine Learning:** Scikit-learn / TensorFlow / PyTorch
- **Base de Datos:** PostgreSQL
- **Frontend:** React.js (o framework SPA equivalente)
- **Despliegue:** Docker + Servidor en la nube (AWS / Azure / GCP)
- **Comunicación segura:** HTTPS / TLS

---

## 🧩 Atributos de Calidad del Software

| Atributo       | Descripción aplicada al sistema |
|----------------|---------------------------------|
| **Seguridad**  | Protección de datos mediante comunicación encriptada (HTTPS), autenticación y autorización, cuarentena segura de archivos sospechosos y logging/auditoría para forense. |
| **Escalabilidad** | Arquitectura desplegable en la nube con autoscaling y balanceo de carga, diseñada para múltiples instituciones (multi-tenant) y usuarios concurrentes. |
| **Rendimiento** | Procesamiento optimizado: extracción de features eficiente, modelos livianos en el agente y análisis intensivo en el servidor para minimizar impacto en los equipos cliente. |
| **Mantenibilidad** | Diseño modular (agente, backend, ML, interfaz), pruebas automatizadas y documentación para facilitar actualizaciones y sustitución de modelos ML. |
| **Disponibilidad** | Despliegue redundante en la nube, backups periódicos y plan de recuperación ante desastres para garantizar acceso 24/7. |
| **Usabilidad** | Interfaz web clara e intuitiva para administradores no expertos en ciberseguridad, con reportes y acciones directas (Cuarentena / Eliminar / Re-escanear). |

---

## 📐 Arquitectura General (Diagrama de Despliegue simplificado)

```plantuml
@startuml
node "Nube (AWS/Azure/GCP)" {
  node "Servidor Web" {
    [Frontend React]
    [Backend Django/Flask]
  }
  node "Servidor ML" {
    [Modelo Entrenado ML]
    [Detector de Keyloggers]
  }
  database "BD Instituciones" {
    [Usuarios]
    [Logs de Seguridad]
    [Alertas]
  }
}

node "Cliente (PC Alumno/Admin)" {
  [Navegador Web]
  [Agente de Monitoreo]
}

[Frontend React] --> [Backend Django/Flask]
[Backend Django/Flask] --> [Modelo Entrenado ML]
[Backend Django/Flask] --> [BD Instituciones]
[Agente de Monitoreo] --> [Backend Django/Flask]
@enduml
>>>>>>> 7da7034329fcf64b244fe28ccc1fb1b3d8e339fe
