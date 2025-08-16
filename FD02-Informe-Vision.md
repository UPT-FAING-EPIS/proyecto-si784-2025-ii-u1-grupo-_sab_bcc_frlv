# 📌 Universidad Privada de Tacna  

## Facultad de Ingeniería  
**Escuela Profesional de Ingeniería de Sistemas**  
**Curso:** Calidad y Pruebas de Software  
**Docente:** Mag. Patrick Cuadros Quiroga  

### 👥 Integrantes:
- Sebastian Arce Bracamonte (2019062886)  
- Chata Choque, Brant Antony (2020067577)  
- Renzo Fernando Loyola Vilca Choque (2021072615)  

📍 Tacna – Perú  
📅 2025  

---

# 🛡️ Desarrollo de un sistema híbrido en C++ y Python basado en Machine Learning para la detección y supresión automática de keyloggers en entornos Windows  

**Documento de Visión – Versión 1.0**

---

## 📑 Control de Versiones

| Versión | Hecha por | Revisada por | Aprobada por | Fecha     | Motivo          |
|---------|-----------|--------------|--------------|-----------|-----------------|
| 1.0     | SAB       | BCC          | FRLV         | 16/08/25  | Primera Versión |

---

## 📚 Índice General
1. [Introducción](#1-introducción)  
2. [Visión General](#2-visión-general)  
3. [Descripción de los Interesados y Usuarios](#3-descripción-de-los-interesados-y-usuarios)  
4. [Vista General del Proyecto](#4-vista-general-del-proyecto)  
5. [Características del Proyecto](#5-características-del-proyecto)  
6. [Restricciones](#6-restricciones)  
7. [Satisfacción al Cliente](#7-satisfacción-al-cliente)  
8. [Rangos de Calidad](#8-rangos-de-calidad)  
9. [Precedencia y Prioridad](#9-precedencia-y-prioridad)  
10. [Otros Requerimientos del Producto](#10-otros-requerimientos-del-producto)  
11. [Conclusiones](#11-conclusiones)  
12. [Recomendaciones](#12-recomendaciones)  

---

## 1. Introducción  

### 1.1 Propósito  
Este documento articula la visión integral del sistema híbrido en **C++ y Python con Machine Learning** para la detección y supresión automática de **keyloggers en entornos Windows**.  

### 1.2 Alcance  
El sistema se enfocará en:  
- 🔍 Monitoreo de procesos, tráfico de red y registros de teclado.  
- ⚡ Identificación de comportamientos sospechosos en tiempo real.  
- 🤖 Clasificación automática de procesos mediante modelos de ML.  
- 🛑 Supresión inmediata de keyloggers detectados y cuarentena de sus archivos.  
- 🧪 Validación experimental en entornos virtualizados seguros (VirtualBox + Cuckoo Sandbox).  

### 1.3 Definiciones, Siglas y Abreviaturas  
- **ML:** Machine Learning  
- **C++:** Lenguaje de programación de bajo nivel usado para módulos de monitoreo  
- **Python:** Lenguaje de alto nivel para la implementación de modelos de ML  
- **Keylogger:** Software malicioso diseñado para registrar pulsaciones de teclado  
- **API Hook:** Técnica para interceptar funciones del sistema  

### 1.4 Referencias  
- Bishop, M. *Computer Security: Art and Science*  
- Papers IEEE y Scopus sobre detección de malware con ML  
- Documentación de Pybind11 y Named Pipes en Windows  

---

## 2. Visión General  

### 2.1 Posicionamiento  
El sistema es una **herramienta avanzada de ciberseguridad**, orientada a detectar keyloggers incluso en sus versiones polimórficas, superando las limitaciones de antivirus tradicionales.  

### 2.2 Oportunidad de Negocio  
El incremento de ataques de robo de credenciales y espionaje corporativo hace que el sistema sea de **alto valor estratégico** para usuarios finales y empresas.  

### 2.3 Definición del Problema  
Los keyloggers en Windows se ocultan como procesos legítimos, evadiendo la protección tradicional. La **falta de detección en tiempo real** expone credenciales y datos sensibles.  

---

## 3. Descripción de los Interesados y Usuarios  

### 3.1 Interesados  
- **Docente y asesores académicos:** Supervisión del proyecto.  
- **Empresas y usuarios:** Obtendrán mayor seguridad digital.  

### 3.2 Usuarios  
- **Administrador de Seguridad:** Configuración y validación de resultados.  
- **Usuarios Finales:** Protección automática sin conocimientos técnicos.  

### 3.3 Entorno del Usuario  
- **Plataforma:** Windows 10/11  
- **Requisitos mínimos:** Intel i5, 8 GB RAM, 200 MB de espacio.  

---

## 4. Vista General del Proyecto  

### 4.1 Perspectiva del Producto  
- **C++** → captura de procesos, hooks, tráfico.  
- **Python** → análisis y ML.  
- Comunicación en tiempo real con **Named Pipes o Pybind11**.  

### 4.2 Resumen de Capacidades  

| Capacidad              | Beneficio |
|-------------------------|-----------|
| Detección en tiempo real | Previene robo de datos sensibles |
| Clasificación ML        | Diferencia procesos legítimos de maliciosos |
| Supresión automática    | Finaliza procesos y pone en cuarentena archivos |
| Informes y alertas      | Facilita gestión a administradores |
| Integración híbrida     | Combina velocidad (C++) y flexibilidad (Python) |

### 4.3 Suposiciones y Dependencias  
- Permisos de administrador en Windows  
- Conexión a internet para entrenar modelos  
- Librerías externas: **scikit-learn, XGBoost, Pybind11**  

---

## 5. Características del Proyecto  
- 🎛️ Usabilidad: interfaz sencilla  
- 📊 Consistencia en reportes  
- ⚙️ Disponibilidad: ejecución en segundo plano  
- 🔐 Seguridad: cifrado de logs  
- 🛠️ Mantenibilidad: código modular  
- ⚡ Inmediatez: respuesta en < 2 segundos  

---

## 6. Restricciones  
- ⏳ Tiempo de desarrollo: **6 meses**  
- 👥 Equipo: **3 integrantes**  
- 💰 Presupuesto: limitado a software libre y hardware existente  

---

## 7. Satisfacción al Cliente  
- Precisión del modelo > **95%**  
- Falsos positivos < **5%**  
- Supresión exitosa de keyloggers  

---

## 8. Rangos de Calidad  
- ✅ Confiabilidad: 99% disponibilidad  
- ⚡ Eficiencia: tiempo real sin sobrecargar CPU  
- 🔐 Seguridad: logs cifrados  

---

## 9. Precedencia y Prioridad  

| Código | Requerimiento                     | Prioridad  |
|--------|------------------------------------|------------|
| RF01   | Captura de procesos activos        | Alta       |
| RF02   | Monitoreo de hooks de teclado      | 🚨 Muy Alta |
| RF03   | Análisis de tráfico de red         | Alta       |
| RF04   | Clasificación ML de procesos       | 🚨 Muy Alta |
| RF05   | Supresión automática de keyloggers | 🚨 Muy Alta |
| RF06   | Reportes y métricas de detección   | Alta       |

---

## 10. Otros Requerimientos del Producto  
- 📜 Cumplimiento con normativas de protección de datos  
- 🔗 Logs en **JSON**  
- 💻 Plataforma: Windows 10/11 (64 bits)  
- 🔐 Cifrado AES en reportes  

---

## 11. Conclusiones  
El sistema híbrido en **C++ y Python con ML** es una solución **preventiva, innovadora y adaptable** frente a amenazas keylogger en entornos Windows.  

---

## 12. Recomendaciones  
- 🔄 Mantener el entrenamiento del modelo con nuevas muestras  
- 🧠 Integrar IA explicable (XAI)  
- 🌐 Escalar a Linux y macOS en futuras versiones  

---
