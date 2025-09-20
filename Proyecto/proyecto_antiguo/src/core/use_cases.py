"""
Casos de uso del sistema Anti-Keylogger.
Implementa la lógica de aplicación siguiendo Clean Architecture.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
import uuid

from .domain import (
    FileFeatures, DetectionResult, ProcessInfo, AlertEvent,
    KeyloggerDetectionEngine, MonitoringSession, ThreatLevel
)


class IFeatureExtractor(ABC):
    """Interfaz para extractores de características de archivos."""
    
    @abstractmethod
    def extract_features(self, file_path: Path) -> FileFeatures:
        """Extrae características de un archivo."""
        pass
    
    @abstractmethod
    def can_process(self, file_path: Path) -> bool:
        """Determina si puede procesar un tipo de archivo."""
        pass


class IMLModelAdapter(ABC):
    """Interfaz para adaptadores de modelos de Machine Learning."""
    
    @abstractmethod
    def predict(self, features: FileFeatures) -> DetectionResult:
        """Realiza predicción sobre las características."""
        pass
    
    @abstractmethod
    def load_model(self, model_path: Path) -> bool:
        """Carga el modelo ML."""
        pass


class IProcessMonitor(ABC):
    """Interfaz para monitores de procesos del sistema."""
    
    @abstractmethod
    def get_running_processes(self) -> List[ProcessInfo]:
        """Obtiene lista de procesos en ejecución."""
        pass


class IAlertHandler(ABC):
    """Interfaz para manejadores de alertas."""
    
    @abstractmethod
    def handle_alert(self, alert: AlertEvent) -> bool:
        """Maneja un evento de alerta."""
        pass


class ILogger(ABC):
    """Interfaz para logging del sistema."""
    
    @abstractmethod
    def log_info(self, message: str, extra: Dict[str, Any] = None):
        """Registra mensaje informativo."""
        pass
    
    @abstractmethod
    def log_warning(self, message: str, extra: Dict[str, Any] = None):
        """Registra mensaje de advertencia."""
        pass
    
    @abstractmethod
    def log_error(self, message: str, extra: Dict[str, Any] = None):
        """Registra mensaje de error."""
        pass


class FileAnalysisUseCase:
    """Caso de uso para análisis de archivos individuales."""
    
    def __init__(
        self,
        feature_extractor: IFeatureExtractor,
        ml_adapter: IMLModelAdapter,
        logger: ILogger
    ):
        self.feature_extractor = feature_extractor
        self.ml_adapter = ml_adapter
        self.logger = logger
        self.detection_engine = KeyloggerDetectionEngine()
    
    def analyze_file(self, file_path: Path) -> Optional[DetectionResult]:
        """Analiza un archivo completo."""
        try:
            if not self.feature_extractor.can_process(file_path):
                self.logger.log_warning(f"Tipo de archivo no soportado: {file_path}")
                return None
            
            self.logger.log_info(f"Analizando archivo: {file_path}")
            
            # Extraer características
            features = self.feature_extractor.extract_features(file_path)
            
            # Ejecutar predicción ML
            result = self.ml_adapter.predict(features)
            
            self.logger.log_info(
                f"Análisis completado - Confianza: {result.confidence:.2f}, "
                f"Nivel: {result.threat_level.value}",
                extra={"file": str(file_path), "confidence": result.confidence}
            )
            
            return result
            
        except Exception as e:
            self.logger.log_error(f"Error analizando {file_path}: {e}")
            return None


class DirectoryMonitoringUseCase:
    """Caso de uso para monitoreo continuo de directorios."""
    
    def __init__(
        self,
        file_analysis: FileAnalysisUseCase,
        alert_handler: IAlertHandler,
        logger: ILogger
    ):
        self.file_analysis = file_analysis
        self.alert_handler = alert_handler
        self.logger = logger
    
    def scan_directory_once(self, session: MonitoringSession) -> List[DetectionResult]:
        """Escanea un directorio una sola vez."""
        results = []
        
        if not session.watch_directory.exists():
            self.logger.log_warning(f"Directorio no existe: {session.watch_directory}")
            return results
        
        for file_path in session.watch_directory.iterdir():
            if not self._should_analyze_file(file_path):
                continue
            
            try:
                mtime = file_path.stat().st_mtime
                
                if not session.is_file_new_or_modified(file_path, mtime):
                    continue
                
                session.mark_file_seen(file_path, mtime)
                session.increment_scan_count()
                
                # Analizar archivo
                result = self.file_analysis.analyze_file(file_path)
                if result:
                    results.append(result)
                    
                    # Verificar si debe generar alerta
                    if result.is_threat():
                        session.increment_threat_count()
                        self._generate_alert(result, session)
                        
            except Exception as e:
                self.logger.log_error(f"Error procesando {file_path}: {e}")
        
        return results
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Determina si un archivo debe ser analizado."""
        return (
            file_path.is_file() and 
            not file_path.name.startswith('.') and
            file_path.stat().st_size > 0
        )
    
    def _generate_alert(self, result: DetectionResult, session: MonitoringSession):
        """Genera y maneja una alerta."""
        alert = AlertEvent(
            event_id=str(uuid.uuid4()),
            timestamp=time.time(),
            event_type="file_detection",
            detection_result=result
        )
        
        success = self.alert_handler.handle_alert(alert)
        if success:
            session.increment_alert_count()
            self.logger.log_info(f"Alerta generada para: {result.file_path}")
        else:
            self.logger.log_error(f"Error generando alerta para: {result.file_path}")


class ProcessMonitoringUseCase:
    """Caso de uso para monitoreo de procesos del sistema."""
    
    def __init__(
        self,
        process_monitor: IProcessMonitor,
        file_analysis: FileAnalysisUseCase,
        alert_handler: IAlertHandler,
        logger: ILogger
    ):
        self.process_monitor = process_monitor
        self.file_analysis = file_analysis
        self.alert_handler = alert_handler
        self.logger = logger
    
    def scan_running_processes(self) -> List[DetectionResult]:
        """Escanea procesos en ejecución buscando amenazas."""
        results = []
        processes = self.process_monitor.get_running_processes()
        
        self.logger.log_info(f"Escaneando {len(processes)} procesos en ejecución...")
        
        for process in processes:
            if not process.exe_path or not process.exe_path.exists():
                continue
            
            try:
                # Analizar el ejecutable del proceso
                result = self.file_analysis.analyze_file(process.exe_path)
                if result and result.is_threat():
                    results.append(result)
                    
                    # Generar alerta específica para proceso
                    alert = AlertEvent(
                        event_id=str(uuid.uuid4()),
                        timestamp=time.time(),
                        event_type="process_detection",
                        detection_result=result,
                        process_info=process
                    )
                    
                    self.alert_handler.handle_alert(alert)
                    self.logger.log_info(
                        f"Proceso sospechoso detectado: {process.name} (PID {process.pid})"
                    )
                    
            except Exception as e:
                self.logger.log_error(
                    f"Error analizando proceso {process.name} (PID {process.pid}): {e}"
                )
        
        return results


class ReportGenerationUseCase:
    """Caso de uso para generación de reportes."""
    
    def __init__(self, logger: ILogger):
        self.logger = logger
    
    def generate_session_report(
        self, 
        session: MonitoringSession,
        detections: List[DetectionResult]
    ) -> Dict[str, Any]:
        """Genera reporte de una sesión de monitoreo."""
        stats = session.get_stats()
        
        threat_summary = {
            'total_threats': len([d for d in detections if d.is_threat()]),
            'high_confidence': len([d for d in detections if d.confidence > 0.8]),
            'medium_confidence': len([d for d in detections if 0.6 <= d.confidence <= 0.8]),
            'by_threat_level': {}
        }
        
        for level in ThreatLevel:
            threat_summary['by_threat_level'][level.value] = len([
                d for d in detections if d.threat_level == level
            ])
        
        report = {
            'session_stats': stats,
            'threat_summary': threat_summary,
            'detections': [
                {
                    'file_path': str(d.file_path),
                    'threat_level': d.threat_level.value,
                    'confidence': d.confidence,
                    'timestamp': d.timestamp
                }
                for d in detections
            ]
        }
        
        self.logger.log_info(
            f"Reporte generado - Archivos: {stats['files_scanned']}, "
            f"Amenazas: {threat_summary['total_threats']}"
        )
        
        return report