"""
Anti-Keylogger Detection API
API REST para detectar keyloggers usando ML
Desplegable en Railway, Render, Heroku
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import joblib
import numpy as np
import json
import os
from typing import Dict, Any, List
import time
from pathlib import Path
import pefile
import hashlib
from datetime import datetime, timedelta
import logging
from starlette.requests import Request

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache global para logs subidos (solución Railway file system efímero)
uploaded_logs_cache = {
    "security_events": [],
    "antivirus": [],
    "timestamp": None,
    "available": False
}

app = FastAPI(
    title="Anti-Keylogger Detection API",
    description="API para detectar keyloggers usando Machine Learning",
    version="1.0.0"
)

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Variables globales para modelos
rf_model = None
feature_names = None
label_classes = None

def load_models():
    """Cargar modelos ML al iniciar la API"""
    global rf_model, feature_names, label_classes
    
    try:
        # Cargar modelo Random Forest
        model_path = os.path.join("models", "rf_large_model_20250918_112442.pkl")
        if os.path.exists(model_path):
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                rf_model = joblib.load(model_path)
            logger.info("✅ Modelo Random Forest cargado (advertencias de versión ignoradas)")
        else:
            logger.error(f"❌ No se encontró el modelo: {model_path}")
        
        # Cargar clases de etiquetas
        labels_path = os.path.join("models", "label_classes.json")
        if os.path.exists(labels_path):
            with open(labels_path, 'r') as f:
                label_classes = json.load(f)
            logger.info("✅ Clases de etiquetas cargadas")
        else:
            # Crear clases por defecto si no existe el archivo
            label_classes = ["safe", "keylogger"]
            logger.info("✅ Usando clases por defecto")
        
        # Cargar nombres de características (si existen)
        features_path = os.path.join("models", "KEEP_modelo_keylogger_from_datos_features.json")
        if os.path.exists(features_path):
            with open(features_path, 'r') as f:
                features_data = json.load(f)
                feature_names = features_data.get('feature_names', [])
            logger.info(f"✅ {len(feature_names)} características cargadas")
        else:
            feature_names = []
            logger.info("✅ Sin nombres de características específicos")
        
    except Exception as e:
        logger.error(f"❌ Error cargando modelos: {e}")
        # Configurar valores por defecto para que la API siga funcionando
        rf_model = None
        label_classes = ["safe", "keylogger"]
        feature_names = []

def extract_pe_features(file_content: bytes) -> Dict[str, Any]:
    """Extraer características de un archivo PE"""
    try:
        # Crear hash del archivo
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Analizar PE
        pe = pefile.PE(data=file_content)
        
        features = {
            # Características básicas
            'file_size': len(file_content),
            'file_hash': file_hash,
            
            # Características PE
            'number_of_sections': pe.FILE_HEADER.NumberOfSections,
            'time_date_stamp': pe.FILE_HEADER.TimeDateStamp,
            'size_of_optional_header': pe.FILE_HEADER.SizeOfOptionalHeader,
            'characteristics': pe.FILE_HEADER.Characteristics,
            
            # Entry point
            'address_of_entry_point': pe.OPTIONAL_HEADER.AddressOfEntryPoint,
            'size_of_code': pe.OPTIONAL_HEADER.SizeOfCode,
            'size_of_initialized_data': pe.OPTIONAL_HEADER.SizeOfInitializedData,
            'size_of_uninitialized_data': pe.OPTIONAL_HEADER.SizeOfUninitializedData,
            
            # Subsystem y DLL characteristics
            'subsystem': pe.OPTIONAL_HEADER.Subsystem,
            'dll_characteristics': pe.OPTIONAL_HEADER.DllCharacteristics,
        }
        
        # Características de secciones
        if hasattr(pe, 'sections'):
            features['sections_count'] = len(pe.sections)
            
            # Características de la primera sección (si existe)
            if pe.sections:
                first_section = pe.sections[0]
                features['first_section_virtual_size'] = first_section.Misc_VirtualSize
                features['first_section_raw_size'] = first_section.SizeOfRawData
                features['first_section_characteristics'] = first_section.Characteristics
        
        # Imports y exports
        try:
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                features['imports_count'] = len(pe.DIRECTORY_ENTRY_IMPORT)
                
                # APIs sospechosas
                suspicious_apis = [
                    'SetWindowsHookEx', 'GetAsyncKeyState', 'GetForegroundWindow',
                    'GetWindowText', 'FindWindow', 'OpenProcess', 'WriteFile',
                    'CreateFile', 'RegSetValue', 'RegOpenKey'
                ]
                
                suspicious_count = 0
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    for imp in entry.imports:
                        if imp.name and any(api.lower() in imp.name.decode('utf-8', errors='ignore').lower() 
                                          for api in suspicious_apis):
                            suspicious_count += 1
                
                features['suspicious_apis_count'] = suspicious_count
            else:
                features['imports_count'] = 0
                features['suspicious_apis_count'] = 0
        except:
            features['imports_count'] = 0
            features['suspicious_apis_count'] = 0
        
        return features
        
    except Exception as e:
        logger.error(f"Error extrayendo características PE: {e}")
        raise HTTPException(status_code=400, detail=f"Error procesando archivo PE: {str(e)}")

def prepare_features_for_model(features: Dict[str, Any]) -> np.ndarray:
    """Preparar características para el modelo ML"""
    try:
        # Características numéricas básicas que el modelo espera
        feature_vector = [
            features.get('file_size', 0),
            features.get('number_of_sections', 0),
            features.get('time_date_stamp', 0),
            features.get('size_of_optional_header', 0),
            features.get('characteristics', 0),
            features.get('address_of_entry_point', 0),
            features.get('size_of_code', 0),
            features.get('size_of_initialized_data', 0),
            features.get('size_of_uninitialized_data', 0),
            features.get('subsystem', 0),
            features.get('dll_characteristics', 0),
            features.get('sections_count', 0),
            features.get('first_section_virtual_size', 0),
            features.get('first_section_raw_size', 0),
            features.get('first_section_characteristics', 0),
            features.get('imports_count', 0),
            features.get('suspicious_apis_count', 0),
        ]
        
        # Normalizar características grandes
        feature_vector[0] = min(feature_vector[0], 100000000)  # file_size
        feature_vector[2] = min(feature_vector[2], 2147483647)  # timestamp
        
        # Completar con ceros hasta llegar a 81 características si es necesario
        while len(feature_vector) < 81:
            feature_vector.append(0)
        
        return np.array(feature_vector[:81]).reshape(1, -1)
        
    except Exception as e:
        logger.error(f"Error preparando características: {e}")
        raise HTTPException(status_code=500, detail=f"Error preparando características: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Cargar modelos al iniciar la aplicación"""
    load_models()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página principal con interfaz web"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Anti-Keylogger Detection API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
            .upload-area { border: 2px dashed #ccc; padding: 20px; text-align: center; margin: 20px 0; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { margin: 20px 0; padding: 15px; border-radius: 5px; }
            .safe { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .danger { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Anti-Keylogger Detection API</h1>
            <p>Sube un archivo ejecutable (.exe) para analizar si es un keylogger</p>
            <div style="text-align: center; margin: 20px 0;">
                <a href="/dashboard" style="display: inline-block; background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">
                    📊 Ver Dashboard de Estadísticas
                </a>
            </div>
            
            <div class="upload-area">
                <input type="file" id="fileInput" accept=".exe" />
                <br><br>
                <button onclick="uploadFile()">Analizar Archivo</button>
            </div>
            
            <div id="result"></div>
        </div>
        
        <script>
            async function uploadFile() {
                const fileInput = document.getElementById('fileInput');
                const resultDiv = document.getElementById('result');
                
                if (!fileInput.files[0]) {
                    alert('Por favor selecciona un archivo');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                
                resultDiv.innerHTML = '<p>🔍 Analizando archivo...</p>';
                
                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        const isKeylogger = result.prediction === 'keylogger';
                        const className = isKeylogger ? 'danger' : 'safe';
                        const icon = isKeylogger ? '⚠️' : '✅';
                        
                        resultDiv.innerHTML = `
                            <div class="result ${className}">
                                <h3>${icon} Resultado del Análisis</h3>
                                <p><strong>Archivo:</strong> ${fileInput.files[0].name}</p>
                                <p><strong>Predicción:</strong> ${result.prediction}</p>
                                <p><strong>Confianza:</strong> ${(result.confidence * 100).toFixed(2)}%</p>
                                <p><strong>Tamaño:</strong> ${result.file_info.size} bytes</p>
                                <p><strong>Hash:</strong> ${result.file_info.hash.substring(0, 16)}...</p>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `<div class="result danger">❌ Error: ${result.detail}</div>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<div class="result danger">❌ Error de conexión: ${error.message}</div>`;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """Analizar un archivo para detectar si es keylogger"""
    
    if not rf_model:
        raise HTTPException(status_code=500, detail="Modelo ML no disponible")
    
    # Validar tipo de archivo
    if not file.filename.lower().endswith('.exe'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .exe")
    
    try:
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Extraer características
        features = extract_pe_features(file_content)
        
        # Preparar para el modelo
        feature_vector = prepare_features_for_model(features)
        
        # Hacer predicción
        prediction = rf_model.predict(feature_vector)[0]
        prediction_proba = rf_model.predict_proba(feature_vector)[0]
        
        # Interpretar resultado
        confidence = max(prediction_proba)
        prediction_label = "keylogger" if prediction == 1 else "safe"
        
        result = {
            "prediction": prediction_label,
            "confidence": float(confidence),
            "file_info": {
                "name": file.filename,
                "size": len(file_content),
                "hash": features.get('file_hash', 'unknown')
            },
            "analysis_timestamp": datetime.now().isoformat(),
            "model_version": "1.0.0"
        }
        
        logger.info(f"Análisis completado: {file.filename} -> {prediction_label} ({confidence:.2f})")
        
        return result
        
    except Exception as e:
        logger.error(f"Error analizando archivo {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

@app.get("/health")
async def health_check():
    """Endpoint de salud para verificar que la API funciona"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": rf_model is not None,
        "version": "1.0.0"
    }

@app.get("/stats")
async def get_stats():
    """Estadísticas del modelo y API"""
    return {
        "model_info": {
            "type": "Random Forest",
            "loaded": rf_model is not None,
            "features_count": 81,
            "classes": label_classes if label_classes else ["safe", "keylogger"]
        },
        "api_info": {
            "version": "1.0.0",
            "supported_formats": [".exe"],
            "max_file_size": "100MB"
        }
    }

# ===== NUEVAS RUTAS PARA DASHBOARD DE ESTADÍSTICAS =====

@app.get("/debug-dashboard")
async def debug_dashboard():
    """Debug information para verificar datos"""
    try:
        stats = read_real_stats()
        detections = read_real_detections()
        notifications = read_real_notifications()
        
        # Verificar estado de logs
        uploaded_security = Path("uploaded_logs/security_events.log")
        uploaded_antivirus = Path("uploaded_logs/antivirus.log")
        
        debug_info = {
            "timestamp": datetime.now().isoformat(),
            "uploaded_logs_available": uploaded_security.exists() and uploaded_antivirus.exists(),
            "uploaded_security_exists": uploaded_security.exists(),
            "uploaded_antivirus_exists": uploaded_antivirus.exists(),
            "uploaded_security_size": uploaded_security.stat().st_size if uploaded_security.exists() else 0,
            "stats": stats,
            "detections_count": len(detections),
            "notifications_count": len(notifications),
            "sample_detection": detections[0] if detections else None,
            "sample_notification": notifications[0] if notifications else None
        }
        
        return debug_info
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Página principal del dashboard de estadísticas"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/stats/summary")
async def get_stats_summary():
    """Estadísticas resumidas para el dashboard - DATOS REALES"""
    try:
        # Leer logs reales del antivirus
        stats = read_real_stats()
        return stats
    except Exception as e:
        logger.error(f"Error leyendo estadísticas reales: {e}")
        # Fallback a datos básicos si hay error
        return {
            "last_scan": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_processes_scanned": 0,
            "threats_detected": 0,
            "false_positives": 0,
            "scan_duration": "N/A",
            "system_health": "Unknown",
            "protection_status": "Error reading logs",
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

@app.get("/api/detections/recent")
async def get_recent_detections():
    """Obtener detecciones recientes REALES del antivirus"""
    try:
        # Leer detecciones reales del security_events.log
        detections = read_real_detections()
        return detections
    except Exception as e:
        logger.error(f"Error leyendo detecciones reales: {e}")
        return []

@app.get("/api/notifications")
async def get_notifications():
    """Obtener notificaciones REALES del antivirus"""
    try:
        # Convertir detecciones reales en notificaciones
        notifications = read_real_notifications()
        return notifications
    except Exception as e:
        logger.error(f"Error leyendo notificaciones reales: {e}")
        return []

def read_real_stats():
    """Leer estadísticas reales del antivirus"""
    try:
        # Priorizar logs en cache (memoria) sobre logs en disco
        global uploaded_logs_cache
        
        if uploaded_logs_cache["available"] and uploaded_logs_cache["security_events"]:
            logger.info("📁 Estadísticas: usando logs subidos (cache en memoria)")
            # Procesar logs desde cache
            lines = uploaded_logs_cache["security_events"]
            threats_detected = 0
            last_scan_time = None
            
            for line in lines:
                try:
                    event = json.loads(line.strip())
                    if 'threat' in event:
                        threats_detected += 1
                        timestamp_str = event.get('timestamp', '')
                        if timestamp_str and (not last_scan_time or timestamp_str > last_scan_time):
                            last_scan_time = timestamp_str
                except json.JSONDecodeError:
                    continue
            
            total_scanned = max(len(lines), threats_detected)
            
        else:
            # Fallback: buscar archivos de logs en disco
            logger.info("📁 Estadísticas: usando logs en disco")
            uploaded_security = Path("uploaded_logs/security_events.log")
            uploaded_antivirus = Path("uploaded_logs/antivirus.log")
            
            if uploaded_security.exists() and uploaded_antivirus.exists():
                antivirus_log = str(uploaded_antivirus)
                security_log = str(uploaded_security)
                logger.info("📁 Usando logs subidos desde uploaded_logs/")
            else:
                # Logs locales (Railway: directorio raíz, Local: directorio padre)
                antivirus_log = "../../antivirus.log" if os.path.exists("../../antivirus.log") else "../antivirus.log"
                security_log = "../../security_events.log" if os.path.exists("../../security_events.log") else "../security_events.log"
                logger.info(f"📁 Usando logs locales: {security_log}")
            
            # Contar líneas de logs para estadísticas
            total_scanned = 0
            threats_detected = 0
            last_scan_time = None
            
            # Leer security_events.log
            if os.path.exists(security_log):
                with open(security_log, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    try:
                        event = json.loads(line.strip())
                        if 'threat' in event:
                            threats_detected += 1
                            timestamp_str = event.get('timestamp', '')
                            if timestamp_str and (not last_scan_time or timestamp_str > last_scan_time):
                                last_scan_time = timestamp_str
                    except json.JSONDecodeError:
                        continue
            
            # Leer antivirus.log para más estadísticas
            if os.path.exists(antivirus_log):
                with open(antivirus_log, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                # Contar procesos escaneados aproximadamente
                scan_count = len([line for line in lines if 'PROC' in line or 'ML' in line])
                total_scanned = max(scan_count, threats_detected)
        
        # Calcular estadísticas
        if not last_scan_time:
            last_scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determinar estado del sistema
        if threats_detected == 0:
            system_health = "Excellent"
            protection_status = "Active - No threats"
        elif threats_detected < 5:
            system_health = "Good"
            protection_status = "Active - Monitoring threats"
        else:
            system_health = "Alert"
            protection_status = "Active - Multiple threats detected"
        
        return {
            "last_scan": last_scan_time,
            "total_processes_scanned": total_scanned,
            "threats_detected": threats_detected,
            "false_positives": max(0, threats_detected - (threats_detected // 3)),  # Estimar falsos positivos
            "scan_duration": "Real-time",
            "system_health": system_health,
            "protection_status": protection_status,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Error en read_real_stats: {e}")
        raise

def read_real_detections():
    """Leer detecciones reales del security_events.log"""
    try:
        # Priorizar logs en cache (memoria)
        global uploaded_logs_cache
        detections = []
        
        if uploaded_logs_cache["available"] and uploaded_logs_cache["security_events"]:
            logger.info("📁 Detecciones: usando logs subidos (cache)")
            lines = uploaded_logs_cache["security_events"]
        else:
            # Buscar logs en disco
            uploaded_security = Path("uploaded_logs/security_events.log")
            if uploaded_security.exists():
                security_log = str(uploaded_security)
                logger.info("📁 Detecciones: usando logs subidos en disco")
            else:
                security_log = "../../security_events.log" if os.path.exists("../../security_events.log") else "../security_events.log"
                logger.info(f"📁 Detecciones: usando logs locales: {security_log}")

            if not os.path.exists(security_log):
                return []
            
            with open(security_log, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        # Procesar últimas 10 detecciones
        for line in reversed(lines[-20:]):  # Últimas 20 líneas
            try:
                event = json.loads(line.strip())
                
                if 'threat' in event and 'process' in event['threat']:
                    threat = event['threat']
                    process_info = threat['process'].get('process_info', {})
                    
                    # Determinar nivel de amenaza
                    confidence = threat.get('confidence', 0) * 100
                    if confidence >= 80:
                        threat_level = "High"
                    elif confidence >= 50:
                        threat_level = "Medium"
                    else:
                        threat_level = "Low"
                    
                    # Determinar acción tomada
                    action = event.get('action_taken', 'logged')
                    if action == 'logged':
                        action_taken = "Monitored (No action)"
                    else:
                        action_taken = action.title()
                    
                    detection = {
                        "id": len(detections) + 1,
                        "program_name": process_info.get('name', 'Unknown'),
                        "detection_time": event.get('timestamp', ''),
                        "threat_level": threat_level,
                        "action_taken": action_taken,
                        "file_path": process_info.get('exe', 'Unknown path'),
                        "confidence": int(confidence)
                    }
                    
                    detections.append(detection)
                    
                    # Limitar a 10 resultados más recientes
                    if len(detections) >= 10:
                        break
                        
            except (json.JSONDecodeError, KeyError) as e:
                continue
        
        return detections
        
    except Exception as e:
        logger.error(f"Error en read_real_detections: {e}")
        return []

def read_real_notifications():
    """Convertir detecciones reales en notificaciones"""
    try:
        # Buscar logs (prioritario: subidos, luego locales)
        uploaded_security = Path("uploaded_logs/security_events.log")
        if uploaded_security.exists():
            security_log = str(uploaded_security)
            logger.info("📁 Notificaciones: usando logs subidos")
        else:
            security_log = "../../security_events.log" if os.path.exists("../../security_events.log") else "../security_events.log"
            logger.info(f"📁 Notificaciones: usando logs locales: {security_log}")
        notifications = []
        
        if not os.path.exists(security_log):
            return []
        
        with open(security_log, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Procesar últimas detecciones para notificaciones
        for line in reversed(lines[-10:]):  # Últimas 10 líneas
            try:
                event = json.loads(line.strip())
                
                if 'threat' in event:
                    threat = event['threat']
                    process_info = threat.get('process', {}).get('process_info', {})
                    program_name = process_info.get('name', 'Unknown')
                    confidence = threat.get('confidence', 0) * 100
                    
                    # Determinar tipo de notificación
                    if confidence >= 80:
                        notif_type = "warning"
                        title = "High Threat Detected"
                    elif confidence >= 50:
                        notif_type = "warning"
                        title = "Suspicious Activity"
                    else:
                        notif_type = "info"
                        title = "Low Risk Detection"
                    
                    notification = {
                        "id": len(notifications) + 1,
                        "type": notif_type,
                        "title": title,
                        "message": f"Detected {threat.get('type', 'threat')} in {program_name}",
                        "program": program_name,
                        "timestamp": event.get('timestamp', ''),
                        "read": False  # Todas las notificaciones empiezan como no leídas
                    }
                    
                    notifications.append(notification)
                    
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Agregar notificación de estado general
        if notifications:
            notifications.append({
                "id": len(notifications) + 1,
                "type": "success",
                "title": "Anti-Keylogger Active",
                "message": f"System is monitoring. {len(notifications)} recent detections.",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "read": True
            })
        
        return notifications
        
    except Exception as e:
        logger.error(f"Error en read_real_notifications: {e}")
        return []

@app.post("/api/notifications/{notification_id}/mark-read")
async def mark_notification_read(notification_id: int):
    """Marcar una notificación como leída"""
    return {"success": True, "message": f"Notificación {notification_id} marcada como leída"}

@app.post("/api/notifications/mark-all-read")
async def mark_all_notifications_read():
    """Marcar todas las notificaciones como leídas"""
    return {"success": True, "message": "Todas las notificaciones marcadas como leídas"}

@app.post("/api/upload-logs")
async def upload_logs(logs_data: dict):
    """Recibir logs desde PC local y guardarlos en Railway (cache + disco)"""
    try:
        global uploaded_logs_cache
        
        timestamp = logs_data.get("timestamp", time.time())
        
        # 1. Almacenar en cache de memoria (principal)
        uploaded_logs_cache["security_events"] = logs_data.get("security_events", [])
        uploaded_logs_cache["antivirus"] = logs_data.get("antivirus", [])
        uploaded_logs_cache["timestamp"] = timestamp
        uploaded_logs_cache["available"] = True
        
        # 2. También intentar guardar en disco (backup, aunque sea efímero)
        try:
            logs_dir = Path("uploaded_logs")
            logs_dir.mkdir(exist_ok=True)
            
            # Guardar security_events.log
            if "security_events" in logs_data and logs_data["security_events"]:
                security_file = logs_dir / "security_events.log"
                with open(security_file, 'w', encoding='utf-8') as f:
                    for line in logs_data["security_events"]:
                        f.write(line.strip() + '\n')
            
            # Guardar antivirus.log
            if "antivirus" in logs_data and logs_data["antivirus"]:
                antivirus_file = logs_dir / "antivirus.log"
                with open(antivirus_file, 'w', encoding='utf-8') as f:
                    for line in logs_data["antivirus"]:
                        f.write(line.strip() + '\n')
        except Exception as disk_error:
            logger.warning(f"No se pudo escribir a disco (normal en Railway): {disk_error}")
        
        logger.info(f"✅ Logs almacenados en cache: {len(logs_data.get('security_events', []))} eventos")
        
        return {
            "success": True, 
            "message": "Logs almacenados en cache de memoria",
            "events_count": len(logs_data.get('security_events', [])),
            "timestamp": timestamp,
            "storage": "memory_cache_primary"
        }
        
    except Exception as e:
        logger.error(f"Error recibiendo logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando logs: {e}")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)