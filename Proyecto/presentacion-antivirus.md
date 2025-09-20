---
marp: true
theme: default
paginate: true
backgroundColor: #1a1a2e
color: #ffffff
style: |
  section {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f1419 100%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }
  h1 {
- **Detección proactiva** sin firmas

    # ❓ ¿Qué es un Keylogger?

    <div class="warning">
    Malware que registra pulsaciones de teclas.
    </div>

    ---

    # ¿Por qué son peligrosos?

    <div class="warning">
    Roban contraseñas, datos bancarios y privados.<br>
    Difíciles de detectar por antivirus tradicionales.
    </div>

    ---

    # 💡 Solución Propuesta

    <div class="success">
    Machine Learning para detectar patrones.
    </div>

    ---

    # Más allá de las firmas

    <div class="success">
    Monitoreo de archivos, red y procesos.<br>
    Detección proactiva, no solo por firmas.
    </div>

    ---

    # 🏗️ Arquitectura

    <div class="highlight">
    <b>Estructura modular y escalable:</b>
    </div>

    ---

    # Componentes principales

    ```
    ANTIVIRUS_PRODUCTION/
    ├── ML Engine
    ├── Detectores
    ├── Monitores
    ├── Utils
    └── Configuración
    ```

    ---

    # 🧠 Machine Learning

    <div class="success">
    Modelo: <b>Random Forest + ONNX</b>
    </div>

    ---

    # Métricas ML

    <div class="success">
    Accuracy: <b>73.78%</b><br>
    81 características de red<br>
    Optimizado para velocidad
    </div>

    ---

    # 🔍 Detectores

    <div class="highlight">
    ML Detector: tráfico de red
    </div>

    ---

    # Más capas de protección

    <div class="highlight">
    Behavior Detector: procesos sospechosos<br>
    Network Detector: conexiones anómalas
    </div>

    ---

    # �️ Monitores

    <div class="highlight">
    Archivos: cambios y escritura
    </div>

    ---

    # Vigilancia de red y procesos

    <div class="highlight">
    Red: tráfico y conexiones<br>
    Procesos: uso de CPU/RAM
    </div>

    ---

    # � Resultados

    <div class="success">
    CPU: <b>14%</b> | RAM: <b>58%</b>
    </div>

    ---

    # Más resultados

    <div class="success">
    108 conexiones monitoreadas<br>
    Sistema funcionando al 100%
    </div>

    ---

    # 🚀 Demo Rápida

    <div class="highlight">
    1. Arranque del sistema
    </div>

    ---

    # Demo: Monitoreo y alertas

    <div class="highlight">
    2. Monitoreo en tiempo real<br>
    3. Detección y alertas
    </div>

    ---


    # Tecnologías

    <div class="success" style="font-size:0.95em;">
    <b>Python 3.11+</b> - Lenguaje principal<br>
    <b>scikit-learn</b> - Machine Learning<br>
    <b>ONNX</b> - Optimización de modelos
    </div>

    ---

    # Más tecnologías

    <div class="success" style="font-size:0.95em;">
    <b>pandas</b> - Manipulación de datos<br>
    <b>numpy</b> - Cálculos numéricos<br>
    <b>psutil</b> - Monitoreo del sistema<br>
    <b>logging</b> - Debug y monitoreo
    </div>

    ---


    # Logros

    <div class="success" style="font-size:0.95em;">
    Sistema ML funcional<br>
    Arquitectura modular
    </div>

    ---

    # Más logros

    <div class="success" style="font-size:0.95em;">
    Dashboard web<br>
    Documentación completa
    </div>

    ---

    # 🛣️ Próximos Pasos

    <div class="highlight">
    Mejorar precisión ML
    </div>

    ---

    # Roadmap

    <div class="highlight">
    Interfaz gráfica<br>
    Testing automatizado
    </div>

    ---




    # 🙏 ¡Gracias!

    <div class="success" style="font-size:1.2em; text-align:center; margin:20px;">
    ¿Preguntas?
    </div>

    ---

    # 💻 GitHub

    <div class="highlight" style="font-size:1em; text-align:center; margin:20px;">
    Repositorio: <a href="https://github.com/KrCrimson/proyecto-Anti-keylogger" style="color:#00d4ff">proyecto-Anti-keylogger</a>
    </div>

    ---


    # Documentación

    <div class="highlight" style="font-size:0.95em; text-align:center; margin:20px;">
    Manual: carpeta <code>MD's Explicativos/</code>
    </div>

**📊 Métricas Finales:**
- **Precision:** 74.22%
- **Recall:** 73.78%
- **F1-Score:** 72.70%

</div>

### **⚡ Optimizaciones:**
- **ONNX Runtime** - 10x más rápido
- **81 características** de tráfico de red

---

# 🔍 Detectores Especializados

## **Triple Capa de Protección**

### **1. 🤖 ML Detector**
- Análisis de patrones de tráfico de red
- Modelo entrenado con datos reales

### **2. 🕵️ Behavior Detector**
- Monitoreo de comportamientos sospechosos
- Análisis de actividad de procesos
- Detección de patrones anómalos

### **3. 🌐 Network Detector**
- Análisis de conexiones de red
- Detección de transmisión de datos sospechosa

---

# 📊 Monitores del Sistema

## **Vigilancia Continua 24/7**

### **📁 File Monitor**
```python
- Archivos creados/modificados
- Actividad de escritura sospechosa
```

### **🌐 Network Monitor**
```python
- Conexiones entrantes/salientes
- Tráfico de datos en tiempo real
- Análisis de patrones de comunicación
```
### **⚙️ Process Monitor**
```python
- Procesos en ejecución
- Uso de CPU/memoria
- Comportamiento de aplicaciones
```

---

# 📈 Resultados y Métricas

## **Rendimiento del Sistema**

<div class="success">

### **✅ Sistema Operativo:**
- **CPU Usage:** 14.0%
- **RAM Usage:** 58.3%
- **Conexiones activas:** 108 monitoreadas
- **Estado:** ✅ FUNCIONANDO AL 100%

</div>

### **🎯 Capacidades de Detección:**
- **Tiempo real** - Detección instantánea
- **Bajo consumo** - Recursos optimizados
- **Alta precisión** - 73.78% de aciertos
- **Falsos positivos** - Minimizados

---

# 🚀 Versión de Producción

## **Sistema Listo para Despliegue**

### **📦 Executables Disponibles:**

<div class="highlight">

```powershell
# Instalación simple
cd ANTIVIRUS_PRODUCTION
pip install -r requirements.txt

# Ejecución
python simple_launcher.py
```

</div>

### **📁 Estructura Optimizada:**
- **350MB** total - Solo archivos esenciales
- **Modelos ML** incluidos y optimizados
- **Configuración** lista para usar
- **Logs** integrados para monitoreo

---

# 🛠️ Tecnologías Utilizadas

## **Stack Tecnológico Robusto**

### **🐍 Backend:**
- **Python 3.11+** - Lenguaje principal
- **scikit-learn** - Machine Learning
- **ONNX Runtime** - Optimización de modelos
- **psutil** - Monitoreo del sistema

### **📊 Data Science:**
- **pandas** - Manipulación de datos
- **numpy** - Cálculos numéricos
- **joblib** - Serialización de modelos

### **🔧 Tools:**
- **TOML** - Configuración
- **JSON** - Intercambio de datos
- **Logging** - Monitoreo y debugging

---

# 🌐 Web Dashboard (Bonus)

## **Interfaz de Monitoreo**

### **📊 Características del Dashboard:**
- **Visualización** de logs en tiempo real
- **Métricas** del sistema y detecciones
- **Historial** de amenazas detectadas
- **Configuración** remota del antivirus

### **🚀 Despliegue:**
```bash
# API REST disponible
cd web_api
python main.py
# Dashboard en http://localhost:8000
```

<div class="success">

**Bonus:** Sistema desplegable en Railway para monitoreo remoto

</div>

---

# 🎯 Demo en Vivo

## **¡Veamos el Sistema en Acción!**

### **🔄 Proceso de Demostración:**

1. **Arranque** del sistema anti-keylogger
2. **Monitoreo** en tiempo real
3. **Simulación** de actividad sospechosa
4. **Detección** y alertas
5. **Logs** y reportes generados

<div class="warning">

**Nota:** Demo realizada en entorno controlado para fines educativos

</div>

---

# 📊 Casos de Uso Reales

## **Aplicaciones Prácticas**

### **🏢 Empresas:**
- Protección de datos corporativos
- Monitoreo de estaciones de trabajo
- Compliance y auditoría

### **🏠 Usuarios Domésticos:**
- Protección de información personal
- Seguridad en banca online
- Privacidad familiar

### **🎓 Instituciones Educativas:**
- Laboratorios de computación
- Protección de investigación
- Seguridad estudiantil

---

# ✅ Logros Alcanzados

## **¿Qué hemos conseguido?**

<div class="success">

### **✅ Tecnológicos:**
- Sistema ML funcional al 73.78% de precisión
- Arquitectura modular y escalable
- Optimización ONNX para producción
- Monitoreo multicapa integrado

</div>

<div class="highlight">

### **✅ Prácticos:**
- Executable listo para despliegue
- Configuración plug-and-play
- Dashboard web operativo
- Documentación completa

</div>

---

# 🚧 Limitaciones Actuales

## **Áreas de Mejora Identificadas**

### **⚠️ Técnicas:**
- **Precisión** - Objetivo 85%+ para producción
- **Falsos positivos** - Refinamiento necesario
- **Datasets** - Más datos de entrenamiento
- **Features** - Análisis de comportamiento expandido

### **⚠️ Operacionales:**
- **Instalación** - Simplificar proceso
- **Interfaz** - GUI más intuitiva
- **Documentación** - Manual de usuario
- **Testing** - Pruebas automatizadas

---

# 🛣️ Próximos Pasos

## **Roadmap de Desarrollo**

### **🎯 Corto Plazo (1-3 meses):**
- **Mejorar precisión** del modelo ML
- **Interfaz gráfica** para usuarios finales
- **Sistema de actualizaciones** automáticas
- **Testing automatizado** completo

### **🚀 Largo Plazo (6+ meses):**
- **Deep Learning** con redes neuronales
- **Detección de malware** general
- **Integración cloud** y sincronización
- **Versión comercial** con soporte

---

# 💰 Valor y Aplicabilidad

## **¿Por qué es importante este proyecto?**

### **🎓 Académico:**
- Aplicación práctica de **Machine Learning**
- Integración de **múltiples tecnologías**
- Experiencia en **ciberseguridad**
- **Metodología de desarrollo** completa

### **💼 Profesional:**
- **Portfolio** de proyecto completo
- **Experiencia** en ML aplicado
- **Conocimiento** en seguridad informática
- **Capacidades** de desarrollo full-stack

### **🌍 Social:**
- **Contribución** a la ciberseguridad
- **Protección** de datos personales
- **Educación** en amenazas digitales

---

# 🔬 Aspectos Técnicos Avanzados

## **Detalles de Implementación**

### **🧠 Pipeline de ML:**
```python
Raw Network Data → Feature Extraction → 
Model Prediction → Risk Assessment → 
Action Trigger → Logging & Alerts
```

### **⚙️ Arquitectura de Software:**
- **Patrón Facade** - Interfaz simplificada
- **Observer Pattern** - Monitores en tiempo real
- **Strategy Pattern** - Detectores intercambiables
- **Factory Pattern** - Creación de componentes

### **📊 Métricas de Calidad:**
- **Cobertura de código** - Testing comprehensive
- **Documentación** - README y comentarios
- **Estándares** - PEP 8 y buenas prácticas

---

# 🎖️ Reconocimientos

## **Agradecimientos y Créditos**

### **📚 Fuentes de Inspiración:**
- **Papers académicos** sobre detección de malware
- **Datasets públicos** de ciberseguridad
- **Comunidad open source** de Python
- **Documentación técnica** de ONNX y scikit-learn

### **🛠️ Herramientas Utilizadas:**
- **VS Code** - Desarrollo
- **Git** - Control de versiones
- **Railway** - Despliegue cloud
- **Marp** - Esta presentación

<div class="success">

**Este proyecto representa la aplicación práctica de conocimientos en ML, ciberseguridad y desarrollo de software**

</div>

---

# ❓ Preguntas y Respuestas

## **¡Momento de Interacción!**

<div class="highlight">

### **💬 Temas de Discusión:**
- **Aspectos técnicos** del machine learning
- **Implementación** y arquitectura
- **Aplicaciones** y casos de uso
- **Mejoras** y evolución futura
- **Experiencias** durante el desarrollo

</div>

### **📧 Contacto:**
- **GitHub:** [proyecto-Anti-keylogger](https://github.com/KrCrimson/proyecto-Anti-keylogger)
- **Documentación:** Ver carpeta `MD's Explicativos/`

---

# 🙏 ¡Gracias!

## **Sistema Anti-Keylogger con ML**

<div class="success">

### **✅ Lo que hemos visto:**
- **Problema real** de ciberseguridad
- **Solución innovadora** con ML
- **Implementación completa** y funcional
- **Resultados medibles** y prometedores
- **Futuro prometedor** del proyecto

</div>

### **🎯 Mensaje Final:**
> *"La ciberseguridad no es solo sobre proteger datos, es sobre proteger vidas digitales y preservar la confianza en la tecnología"*

**¡El futuro de la detección de malware es inteligente!** 🤖🛡️

---