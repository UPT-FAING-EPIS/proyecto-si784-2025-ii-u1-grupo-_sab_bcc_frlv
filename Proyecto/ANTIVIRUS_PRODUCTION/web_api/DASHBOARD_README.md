# 📊 Dashboard Anti-Keylogger

Dashboard en tiempo real para monitorear las estadísticas y detecciones del sistema Anti-Keylogger.

## 🎯 Nuevas Funcionalidades

### ✨ **Dashboard de Estadísticas**
- **URL**: `/dashboard` (en Railway será `tu-app.railway.app/dashboard`)
- **Métricas en tiempo real**: Procesos escaneados, amenazas detectadas, rendimiento
- **Visualización elegante**: Cards animadas con efectos visuales modernos
- **Responsive**: Funciona perfectamente en móviles y tablets

### 🔔 **Sistema de Notificaciones**
- **Notificaciones toast**: Aparecen elegantemente en la esquina superior derecha
- **Alertas por nivel**: Verde (seguro), Amarillo (sospechoso), Rojo (peligroso)
- **Sin cerrar programas**: Solo monitorea y notifica, no interrumpe el trabajo
- **Gestión de notificaciones**: Marcar como leídas individual o masivamente

### 📈 **Datos en Tiempo Real**
- **Actualización automática**: Cada 30 segundos
- **API endpoints**:
  - `/api/stats/summary` - Resumen de estadísticas
  - `/api/detections/recent` - Detecciones recientes
  - `/api/notifications` - Notificaciones del sistema

## 🎨 **Diseño y UX**

### **Características Visuales:**
- **Gradientes modernos**: Fondos con efectos de vidrio esmerilado
- **Animaciones suaves**: Transiciones y efectos hover elegantes
- **Iconos FontAwesome**: Interface profesional y clara
- **Colores intuitivos**: 
  - 🟢 Verde = Seguro/Completado
  - 🟡 Amarillo = Sospechoso/Advertencia  
  - 🔴 Rojo = Peligroso/Error
  - 🔵 Azul = Información/Neutral

### **Navegación:**
- **Navbar fijo**: Navegación entre Inicio y Dashboard
- **Breadcrumbs visuales**: Indicadores de estado claros
- **Botones de acción**: Actualizar, marcar leídas, etc.

## 🚀 **Deployment en Railway**

### **Archivos Agregados:**
```
web_api/
├── templates/
│   └── dashboard.html          # Página del dashboard
├── static/
│   └── dashboard.css          # Estilos personalizados
├── main.py                    # API actualizada con nuevas rutas
└── requirements.txt           # Dependencias actualizadas
```

### **Nuevas Rutas API:**
```python
GET  /dashboard                 # Página del dashboard
GET  /api/stats/summary        # Estadísticas generales  
GET  /api/detections/recent    # Detecciones recientes
GET  /api/notifications        # Notificaciones del sistema
POST /api/notifications/{id}/mark-read    # Marcar notificación como leída
POST /api/notifications/mark-all-read     # Marcar todas como leídas
```

## 🔧 **Configuración del Sistema Antivirus**

### **Modo No Invasivo:**
El antivirus ahora funciona en **modo de monitoreo** en lugar de cerrar programas:

```python
# Antes (invasivo):
def handle_detection(self, process_info, detection_result):
    process.terminate()  # ❌ Cerraba el programa
    
# Ahora (no invasivo):  
def handle_detection(self, process_info, detection_result):
    self.show_elegant_notification(notification)  # ✅ Solo notifica
    self.save_notification(notification)          # ✅ Guarda registro
```

### **Notificaciones Elegantes:**
```
🛡️  ANTI-KEYLOGGER PROTECTION ALERT
============================================================
⏰ Tiempo: 2024-12-20 15:28:45
📋 Programa: suspicious_app.exe  
🔍 PID: 1234
⚠️  Nivel de Amenaza: MEDIUM
📊 Confianza: 75%
🔧 Acción: MONITORED
============================================================
ℹ️  El programa continúa ejecutándose bajo monitoreo.
📱 Revisa el dashboard web para más detalles.
============================================================
```

## 📱 **Uso del Dashboard**

### **Acceso:**
1. **Desde Railway**: `https://tu-app.railway.app/dashboard`
2. **Local**: `http://localhost:8000/dashboard`
3. **Enlace directo**: Botón en la página principal

### **Funcionalidades:**
- **Vista general**: Estado del sistema y métricas clave
- **Detecciones**: Lista de programas analizados con niveles de amenaza
- **Notificaciones**: Alertas recientes con opciones de gestión
- **Tiempo real**: Actualizaciones automáticas sin refrescar página

### **Interacciones:**
- **Hover effects**: Cards se elevan al pasar el mouse
- **Click actions**: Botones para actualizar y gestionar notificaciones
- **Responsive**: Se adapta automáticamente al tamaño de pantalla
- **Toasts**: Notificaciones emergentes para nuevas detecciones

## 🔄 **Deploy Automático**

Una vez que hagas commit y push:

```bash
git add .
git commit -m "Add dashboard and elegant notifications"
git push origin Calidad
```

**Railway detectará los cambios automáticamente** y desplegará:
- ✅ Nuevas dependencias (Jinja2)
- ✅ Templates y archivos estáticos  
- ✅ Nuevas rutas API
- ✅ Dashboard funcional

## 🎉 **Resultado Final**

Tu aplicación tendrá:
- **Página principal mejorada** con enlace al dashboard
- **Dashboard completo** con estadísticas en tiempo real
- **Sistema de notificaciones** elegante y no invasivo
- **API robusta** con múltiples endpoints
- **Diseño profesional** con UX/UI moderna

**¡Tu Railway app será una solución completa de monitoreo anti-keylogger!** 🛡️✨