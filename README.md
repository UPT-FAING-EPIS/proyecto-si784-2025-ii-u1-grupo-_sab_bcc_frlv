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
