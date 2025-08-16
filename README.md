
| Integrante                         | Código     |
| ---------------------------------- | ---------- |
| Sebastián Arce Bracamonte          | 2019062986 |
| Brant Antony Chata Choque          | 2021072615 |
| Renzo Fernando Loyola Vilca Choque | 2020067577 |
# 🛡️ Sistema Híbrido en C++ y Python para Detección y Supresión Automática de Keyloggers en Windows

## 📌 Descripción del Proyecto
Este proyecto tiene como finalidad el desarrollo de un **sistema híbrido** en **C++ y Python**, apoyado en algoritmos de **Machine Learning**, para la **detección y supresión automática de keyloggers** en entornos **Windows**.  

Los **keyloggers** representan una amenaza crítica de ciberseguridad, pues capturan información sensible (contraseñas, datos bancarios, credenciales corporativas) de manera oculta y difícil de detectar, incluso para antivirus tradicionales.  

El sistema propuesto se enfoca en el **análisis de procesos, tráfico de red, registros de teclado y comportamiento de archivos**, diferenciando entre procesos legítimos y sospechosos. Además, integra un mecanismo de **respuesta automática** para finalizar procesos maliciosos y poner en cuarentena los archivos infectados.

---

## 🚨 Problema
- Los keyloggers operan ocultos, disfrazándose como procesos legítimos.  
- Antivirus tradicionales se basan en firmas conocidas, lo que limita la detección de variantes nuevas o polimórficas.  
- Existe la necesidad de un sistema **inteligente** capaz de detectar comportamientos anómalos en tiempo real y actuar automáticamente.  

---

## 🎯 Objetivos

### Objetivo Principal
Desarrollar un sistema híbrido en C++ y Python que permita la **detección en tiempo real** y **supresión automática de keyloggers** en entornos Windows, mediante técnicas de Machine Learning.

### Objetivos Específicos
1. Analizar las técnicas utilizadas por los keyloggers para capturar datos y mantenerse ocultos en Windows.  
2. Diseñar un módulo en **C++** para captura de:  
   - Procesos activos  
   - Hooks de teclado  
   - Tráfico de red  
   - Modificaciones de archivos  
3. Implementar en **Python** un modelo de Machine Learning (Random Forest, XGBoost o Isolation Forest) para clasificar procesos sospechosos.  
4. Integrar la comunicación entre **C++ y Python** mediante **Named Pipes** o **Pybind11**.  
5. Desarrollar un mecanismo de **supresión automática** que finalice procesos maliciosos y mueva archivos a cuarentena.  
6. Validar el sistema en **entornos virtuales** (VirtualBox + Cuckoo Sandbox), midiendo:  
   - Precisión  
   - Recall  
   - Tasa de falsos positivos  

---

## 🏗️ Arquitectura del Sistema

```text
+---------------------+       +----------------------+
|  Módulo en C++      | <---> |  Modelo ML en Python |
|  -----------------  |       |  ------------------  |
| - Procesos activos  |       | - Random Forest      |
| - Hooks de teclado  |       | - XGBoost / IForest  |
| - Red y archivos    |       |                      |
+---------------------+       +----------------------+
        |                                 |
        v                                 v
Supresión automática          Decisión inteligente
 (kill / quarantine)          (detección en tiempo real)
```

## 🛠️ Tecnologías Utilizadas

- Lenguajes: C++17, Python 3.10

- Machine Learning: scikit-learn, XGBoost

- Integración C++/Python: Pybind11, Named Pipes

- Entorno de pruebas: VirtualBox, Cuckoo Sandbox

- Sistema operativo objetivo: Windows 10/11

## ⚙️ Requisitos

- Sistema Operativo: Windows 10/11

- Compilador C++: MSVC o MinGW

- Python: 3.10+

**Dependencias de Python:**
```
pip install scikit-learn xgboost pandas numpy
```

**Entorno de pruebas: VirtualBox + Cuckoo Sandbox**

## 🚀 Instalación y Ejecución
**1️⃣ Clonar el repositorio**
```
git clone https://github.com/usuario/proyecto-keylogger-detection.git
cd proyecto-keylogger-detection
```
**2️⃣ Compilar el módulo en C++**
```
g++ -std=c++17 -o detector detector.cpp
```
**3️⃣ Ejecutar el sistema**
```
./detector
```

- El sistema se comunicará con el modelo en Python para clasificar procesos en tiempo real.

## 📊 Métricas de Evaluación

- Precisión (Accuracy)

- Recall (Detección efectiva de amenazas)

- Tasa de falsos positivos

## 🔒 Consideraciones de Seguridad

- El sistema debe ejecutarse con privilegios de administrador en Windows.

- El mecanismo de supresión está diseñado para usarse en entornos de prueba controlados.

- No se recomienda su ejecución en producción sin validación exhaustiva.
