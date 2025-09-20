# Requerimientos del Proyecto Anti-Keylogger

## Requerimientos Funcionales

| Código | Nombre                  | Descripción breve                        | Imp. | Prio. |
|--------|-------------------------|------------------------------------------|------|-------|
| RF01   | Monitoreo archivos      | Analiza carpetas y procesos activos      | Alta | 1     |
| RF02   | Extracción de features  | Extrae características para ML           | Alta | 2     |
| RF03   | Detección keyloggers    | Identifica archivos/procesos maliciosos  | Alta | 3     |
| RF04   | Predicción ML           | Usa modelos `.pkl` y `.onnx`             | Alta | 4     |
| RF05   | Alertas automáticas     | Muestra alerta y detiene análisis        | Alta | 5     |
| RF06   | Opciones de escaneo     | Escaneo total, carpeta o archivo; acciones ante detección | Alta | 6     |
| RF07   | Registro de eventos     | Guarda logs de análisis y detecciones    | Media| 7     |
| RF08   | Tolerancia a errores    | Continúa ante archivos corruptos         | Alta | 8     |
| RF09   | Configuración flexible  | Permite ajustar rutas y parámetros       | Media| 9     |
| RF10   | Predicción manual       | Permite análisis desde consola           | Media| 10    |

## Requerimientos No Funcionales

| Código | Nombre         | Descripción breve                        | Imp. | Prio. |
|--------|----------------|------------------------------------------|------|-------|
| RNF01  | Portabilidad   | Funciona en Windows 7/8/10/11 (x86/x64)  | Alta | 1     |
| RNF02  | Robustez       | Maneja errores sin detener el sistema     | Alta | 2     |
| RNF03  | Rendimiento    | Análisis rápido y escalable               | Alta | 3     |
| RNF04  | Seguridad      | No envía datos fuera; logs cifrados       | Alta | 4     |
--
Este documento sirve como base para validar el avance y cumplimiento de los objetivos del proyecto.
