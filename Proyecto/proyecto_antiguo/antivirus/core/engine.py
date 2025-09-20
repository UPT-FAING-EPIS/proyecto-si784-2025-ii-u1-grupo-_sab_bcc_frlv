"""
Sistema Anti-Keylogger con Machine Learning
==========================================

Módulo principal del sistema antivirus que utiliza ML para detectar keyloggers
en tiempo real mediante análisis de tráfico de red y comportamiento del sistema.
"""

import logging
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('antivirus.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AntiKeyloggerEngine:
    """Motor principal del antivirus anti-keylogger"""
    
    def __init__(self, config_file: str = "config.toml"):
        self.config_file = config_file
        self.is_running = False
        self.monitors = {}
        self.detectors = {}
        self.threat_callbacks = []
        self.stats = {
            'scans_performed': 0,
            'threats_detected': 0,
            'false_positives': 0,
            'start_time': None,
            'last_scan': None
        }
        
        # Cargar configuración
        self.config = self._load_config()
        
        # Inicializar componentes
        self._initialize_ml_model()
        self._initialize_monitors()
        self._initialize_detectors()
        
        logger.info("[SHIELD] Anti-Keylogger Engine inicializado")
    
    def _load_config(self) -> Dict:
        """Carga configuración del sistema"""
        try:
            import toml
            with open(self.config_file, 'r') as f:
                config = toml.load(f)
            logger.info(f"[OK] Configuración cargada desde {self.config_file}")
            return config
        except Exception as e:
            logger.warning(f"[WARNING] No se pudo cargar config: {e}")
            # Configuración por defecto
            return {
                'antivirus': {
                    'scan_interval': 30,
                    'real_time_protection': True,
                    'threat_threshold': 0.7,
                    'quarantine_enabled': True
                },
                'ml_model': {
                    'model_path': 'models/development',
                    'use_onnx': True,
                    'confidence_threshold': 0.8
                },
                'monitoring': {
                    'network_traffic': True,
                    'process_behavior': True,
                    'file_system': True,
                    'registry_changes': True
                }
            }
    
    def _initialize_ml_model(self):
        """Inicializa el modelo de ML para detección"""
        try:
            from .detectors.ml_detector import MLKeyloggerDetector
            
            model_config = self.config.get('ml_model', {})
            self.ml_detector = MLKeyloggerDetector(
                model_path=model_config.get('model_path', 'models/development'),
                use_onnx=model_config.get('use_onnx', True),
                confidence_threshold=model_config.get('confidence_threshold', 0.8)
            )
            
            logger.info("[ML] Detector ML inicializado")
            
        except Exception as e:
            logger.error(f"[ERROR] Error inicializando ML detector: {e}")
            self.ml_detector = None
    
    def _initialize_monitors(self):
        """Inicializa los monitores del sistema"""
        monitor_config = self.config.get('monitoring', {})
        
        try:
            # Monitor de tráfico de red
            if monitor_config.get('network_traffic', True):
                from .monitors.network_monitor import NetworkTrafficMonitor
                self.monitors['network'] = NetworkTrafficMonitor(
                    callback=self._on_network_activity
                )
                logger.info("[NET] Monitor de red inicializado")
            
            # Monitor de procesos
            if monitor_config.get('process_behavior', True):
                from .monitors.process_monitor import ProcessBehaviorMonitor
                self.monitors['process'] = ProcessBehaviorMonitor(
                    callback=self._on_process_activity
                )
                logger.info("[PROC] Monitor de procesos inicializado")
            
            # Monitor de sistema de archivos
            if monitor_config.get('file_system', True):
                from .monitors.file_monitor import FileSystemMonitor
                self.monitors['filesystem'] = FileSystemMonitor(
                    callback=self._on_file_activity
                )
                logger.info("[FILE] Monitor de archivos inicializado")
                
        except Exception as e:
            logger.error(f"[ERROR] Error inicializando monitores: {e}")
    
    def _initialize_detectors(self):
        """Inicializa los detectores especializados"""
        try:
            # Detector de comportamiento de keylogger
            from .detectors.behavior_detector import BehaviorDetector
            self.detectors['behavior'] = BehaviorDetector()
            
            # Detector de patrones de red
            from .detectors.network_detector import NetworkPatternDetector
            self.detectors['network_patterns'] = NetworkPatternDetector()
            
            logger.info("[SEARCH] Detectores especializados inicializados")
            
        except Exception as e:
            logger.error(f"[ERROR] Error inicializando detectores: {e}")
    
    def start_protection(self):
        """Inicia la protección en tiempo real"""
        if self.is_running:
            logger.warning("[WARNING] La protección ya está activa")
            return
        
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        
        logger.info("[SHIELD] Iniciando protección anti-keylogger...")
        
        # Iniciar monitores en hilos separados
        for name, monitor in self.monitors.items():
            thread = threading.Thread(
                target=monitor.start_monitoring,
                name=f"Monitor_{name}",
                daemon=True
            )
            thread.start()
            logger.info(f"[SYNC] Monitor {name} iniciado")
        
        # Hilo principal de análisis
        analysis_thread = threading.Thread(
            target=self._analysis_loop,
            name="AnalysisLoop",
            daemon=True
        )
        analysis_thread.start()
        
        logger.info("[OK] Protección en tiempo real activa")
    
    def stop_protection(self):
        """Detiene la protección"""
        if not self.is_running:
            logger.warning("[WARNING] La protección no está activa")
            return
        
        self.is_running = False
        
        # Detener monitores
        for name, monitor in self.monitors.items():
            monitor.stop_monitoring()
            logger.info(f"🛑 Monitor {name} detenido")
        
        logger.info("[SHIELD] Protección detenida")
    
    def _analysis_loop(self):
        """Bucle principal de análisis"""
        scan_interval = self.config.get('antivirus', {}).get('scan_interval', 30)
        
        while self.is_running:
            try:
                self._perform_scan()
                time.sleep(scan_interval)
            except Exception as e:
                logger.error(f"[ERROR] Error en bucle de análisis: {e}")
                time.sleep(5)  # Pausa breve antes de reintentar
    
    def _perform_scan(self):
        """Realiza un escaneo completo del sistema"""
        logger.info("[SEARCH] Iniciando escaneo del sistema...")
        self.stats['scans_performed'] += 1
        self.stats['last_scan'] = datetime.now()
        
        threats_found = []
        
        # Analizar datos de monitores
        for name, monitor in self.monitors.items():
            try:
                data = monitor.get_recent_data()
                if data:
                    threats = self._analyze_monitor_data(name, data)
                    threats_found.extend(threats)
            except Exception as e:
                logger.error(f"[ERROR] Error analizando {name}: {e}")
        
        # Procesar amenazas encontradas
        if threats_found:
            self._handle_threats(threats_found)
        else:
            logger.info("[OK] Escaneo completado - No se detectaron amenazas")
    
    def _analyze_monitor_data(self, monitor_name: str, data: List[Dict]) -> List[Dict]:
        """Analiza datos de un monitor específico"""
        threats = []
        
        # Usar detector ML si está disponible
        if self.ml_detector and monitor_name == 'network':
            ml_threats = self.ml_detector.analyze_network_data(data)
            threats.extend(ml_threats)
        
        # Usar detectores especializados
        for detector_name, detector in self.detectors.items():
            try:
                detected = detector.analyze(monitor_name, data)
                threats.extend(detected)
            except Exception as e:
                logger.error(f"[ERROR] Error en detector {detector_name}: {e}")
        
        return threats
    
    def _handle_threats(self, threats: List[Dict]):
        """Maneja las amenazas detectadas"""
        for threat in threats:
            self.stats['threats_detected'] += 1
            
            logger.warning(f"🚨 AMENAZA DETECTADA: {threat}")
            
            # Ejecutar callbacks de amenaza
            for callback in self.threat_callbacks:
                try:
                    callback(threat)
                except Exception as e:
                    logger.error(f"[ERROR] Error en callback de amenaza: {e}")
            
            # Acciones automáticas
            self._take_action(threat)
    
    def _take_action(self, threat: Dict):
        """Toma acciones automáticas contra amenazas"""
        threat_level = threat.get('severity', 'medium')
        threat_type = threat.get('type', 'unknown')
        
        if threat_level == 'high':
            if threat_type == 'keylogger':
                self._quarantine_process(threat)
            elif threat_type == 'suspicious_network':
                self._block_network_connection(threat)
        
        # Registrar en log de seguridad
        self._log_security_event(threat)
    
    def _quarantine_process(self, threat: Dict):
        """Pone en cuarentena un proceso malicioso"""
        process_info = threat.get('process', {})
        pid = process_info.get('pid')
        
        if pid:
            try:
                import psutil
                process = psutil.Process(pid)
                process.terminate()
                logger.warning(f"[LOCK] Proceso {pid} terminado (cuarentena)")
            except Exception as e:
                logger.error(f"[ERROR] No se pudo terminar proceso {pid}: {e}")
    
    def _block_network_connection(self, threat: Dict):
        """Bloquea una conexión de red sospechosa"""
        network_info = threat.get('network', {})
        remote_ip = network_info.get('remote_ip')
        
        if remote_ip:
            logger.warning(f"🚫 Bloqueando conexión a {remote_ip}")
            # Aquí implementarías el bloqueo real (firewall, etc.)
    
    def _log_security_event(self, threat: Dict):
        """Registra evento de seguridad"""
        security_log = {
            'timestamp': datetime.now().isoformat(),
            'threat': threat,
            'action_taken': 'logged',
            'engine_version': '1.0.0'
        }
        
        # Guardar en archivo de log de seguridad
        security_log_file = Path("security_events.log")
        with open(security_log_file, 'a') as f:
            f.write(json.dumps(security_log) + '\n')
    
    def _on_network_activity(self, activity_data: Dict):
        """Callback para actividad de red"""
        # Análisis en tiempo real de tráfico
        if self.ml_detector:
            threat_score = self.ml_detector.quick_analyze(activity_data)
            if threat_score > self.config.get('antivirus', {}).get('threat_threshold', 0.7):
                threat = {
                    'type': 'suspicious_network',
                    'severity': 'medium',
                    'confidence': threat_score,
                    'network': activity_data,
                    'timestamp': datetime.now().isoformat()
                }
                self._handle_threats([threat])
    
    def _on_process_activity(self, process_data: Dict):
        """Callback para actividad de procesos"""
        # Análisis de comportamiento de procesos
        suspicious_behaviors = [
            'keylogger_pattern',
            'suspicious_network_access',
            'registry_modification'
        ]
        
        for behavior in suspicious_behaviors:
            if behavior in process_data.get('behaviors', []):
                threat = {
                    'type': 'keylogger',
                    'severity': 'high',
                    'confidence': 0.85,
                    'process': process_data,
                    'timestamp': datetime.now().isoformat()
                }
                self._handle_threats([threat])
                break
    
    def _on_file_activity(self, file_data: Dict):
        """Callback para actividad de archivos"""
        # Análisis de actividad del sistema de archivos
        suspicious_files = [
            '.keylog',
            'passwords.txt',
            'captures.log'
        ]
        
        file_path = file_data.get('path', '')
        if any(suspicious in file_path.lower() for suspicious in suspicious_files):
            threat = {
                'type': 'suspicious_file',
                'severity': 'medium',
                'confidence': 0.6,
                'file': file_data,
                'timestamp': datetime.now().isoformat()
            }
            self._handle_threats([threat])
    
    def add_threat_callback(self, callback: Callable):
        """Añade un callback para ser notificado de amenazas"""
        self.threat_callbacks.append(callback)
    
    def get_status(self) -> Dict:
        """Obtiene el estado actual del sistema"""
        return {
            'is_running': self.is_running,
            'stats': self.stats.copy(),
            'monitors_active': len([m for m in self.monitors.values() if m.is_active()]),
            'ml_detector_loaded': self.ml_detector is not None,
            'config': self.config
        }
    
    def perform_manual_scan(self, target_path: Optional[str] = None):
        """Realiza un escaneo manual"""
        logger.info(f"[SEARCH] Iniciando escaneo manual: {target_path or 'sistema completo'}")
        
        if target_path:
            # Escanear directorio específico
            self._scan_directory(target_path)
        else:
            # Escaneo completo del sistema
            self._perform_scan()
    
    def _scan_directory(self, directory_path: str):
        """Escanea un directorio específico"""
        from .utils.file_scanner import FileScanner
        
        scanner = FileScanner(self.ml_detector)
        results = scanner.scan_directory(directory_path)
        
        threats = [r for r in results if r.get('is_threat', False)]
        if threats:
            self._handle_threats(threats)
        
        logger.info(f"[DATA] Escaneo completado: {len(results)} archivos, {len(threats)} amenazas")


def main():
    """Función principal para ejecutar el antivirus"""
    print("[SHIELD] SISTEMA ANTI-KEYLOGGER CON MACHINE LEARNING")
    print("=" * 50)
    
    # Crear instancia del motor
    engine = AntiKeyloggerEngine()
    
    # Añadir callback para mostrar amenazas
    def on_threat_detected(threat):
        print(f"\n🚨 AMENAZA DETECTADA:")
        print(f"   Tipo: {threat.get('type', 'Desconocido')}")
        print(f"   Severidad: {threat.get('severity', 'Media')}")
        print(f"   Confianza: {threat.get('confidence', 0.0):.2%}")
        print(f"   Timestamp: {threat.get('timestamp', 'N/A')}")
    
    engine.add_threat_callback(on_threat_detected)
    
    try:
        # Iniciar protección
        engine.start_protection()
        
        print("\n[OK] Protección iniciada. Presiona Ctrl+C para detener...")
        
        # Bucle principal
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo protección...")
        engine.stop_protection()
        print("[OK] Sistema detenido")
    
    except Exception as e:
        print(f"[ERROR] Error crítico: {e}")
        engine.stop_protection()


if __name__ == "__main__":
    main()