"""
Módulo principal del dominio Anti-Keylogger.
Contiene las entidades, value objects y lógica de negocio central.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional
import time


class ThreatLevel(Enum):
    """Niveles de amenaza para clasificación."""
    BENIGN = "benign"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"


class FileType(Enum):
    """Tipos de archivos soportados para análisis."""
    EXECUTABLE = "executable"
    DOCUMENT = "document"
    IMAGE = "image"
    ARCHIVE = "archive"
    MEDIA = "media"
    CSV = "csv"
    UNKNOWN = "unknown"


@dataclass
class FileFeatures:
    """Value object que representa las características extraídas de un archivo."""
    file_size: int
    file_type: FileType
    md5_hash: Optional[str] = None
    entropy: Optional[float] = None
    num_sections: Optional[int] = None
    has_imports: bool = False
    is_document: bool = False
    is_image: bool = False
    is_archive: bool = False
    is_media: bool = False
    custom_features: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_features is None:
            self.custom_features = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte las features a diccionario para el modelo ML."""
        base_features = {
            'file_size': self.file_size,
            'entropy': self.entropy or 0,
            'num_sections': self.num_sections or 0,
            'has_imports': int(self.has_imports),
            'is_document': int(self.is_document),
            'is_image': int(self.is_image),
            'is_archive': int(self.is_archive),
            'is_media': int(self.is_media)
        }
        base_features.update(self.custom_features)
        return base_features


@dataclass
class DetectionResult:
    """Resultado de una detección de keylogger."""
    file_path: Path
    threat_level: ThreatLevel
    confidence: float
    features: FileFeatures
    timestamp: float
    model_version: str
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
    
    def is_threat(self, threshold: float = 0.6) -> bool:
        """Determina si el archivo representa una amenaza basado en el umbral."""
        return self.confidence >= threshold and self.threat_level != ThreatLevel.BENIGN


@dataclass
class ProcessInfo:
    """Información de un proceso en ejecución."""
    pid: int
    name: str
    exe_path: Optional[Path]
    cmdline: Optional[str]
    features: Optional[FileFeatures] = None


@dataclass
class AlertEvent:
    """Evento de alerta generado por el sistema."""
    event_id: str
    timestamp: float
    event_type: str  # 'file_detection', 'process_detection'
    detection_result: DetectionResult
    process_info: Optional[ProcessInfo] = None
    severity: str = "HIGH"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario para logging."""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp,
            'event_type': self.event_type,
            'severity': self.severity,
            'file_path': str(self.detection_result.file_path),
            'threat_level': self.detection_result.threat_level.value,
            'confidence': self.detection_result.confidence,
            'process_info': {
                'pid': self.process_info.pid,
                'name': self.process_info.name,
                'exe_path': str(self.process_info.exe_path) if self.process_info.exe_path else None
            } if self.process_info else None
        }


class KeyloggerDetectionEngine:
    """Motor principal de detección de keyloggers."""
    
    def __init__(self, threat_threshold: float = 0.6):
        self.threat_threshold = threat_threshold
        self.model_version = "1.0.0"
    
    def analyze_file(self, file_path: Path, features: FileFeatures) -> DetectionResult:
        """Analiza un archivo y retorna el resultado de detección."""
        # Esta lógica será implementada por los adaptadores externos
        # Por ahora retornamos un resultado básico
        threat_level = ThreatLevel.BENIGN
        confidence = 0.0
        
        return DetectionResult(
            file_path=file_path,
            threat_level=threat_level,
            confidence=confidence,
            features=features,
            timestamp=time.time(),
            model_version=self.model_version
        )
    
    def should_alert(self, detection_result: DetectionResult) -> bool:
        """Determina si se debe generar una alerta."""
        return detection_result.is_threat(self.threat_threshold)


class MonitoringSession:
    """Sesión de monitoreo que mantiene el estado del sistema."""
    
    def __init__(self, watch_directory: Path):
        self.watch_directory = watch_directory
        self.start_time = time.time()
        self.files_scanned = 0
        self.threats_detected = 0
        self.alerts_generated = 0
        self.seen_mtimes: Dict[Path, float] = {}
    
    def mark_file_seen(self, file_path: Path, mtime: float):
        """Marca un archivo como visto con su tiempo de modificación."""
        self.seen_mtimes[file_path] = mtime
    
    def is_file_new_or_modified(self, file_path: Path, mtime: float) -> bool:
        """Verifica si un archivo es nuevo o ha sido modificado."""
        last_seen = self.seen_mtimes.get(file_path)
        return last_seen is None or mtime > last_seen
    
    def increment_scan_count(self):
        """Incrementa el contador de archivos escaneados."""
        self.files_scanned += 1
    
    def increment_threat_count(self):
        """Incrementa el contador de amenazas detectadas."""
        self.threats_detected += 1
    
    def increment_alert_count(self):
        """Incrementa el contador de alertas generadas."""
        self.alerts_generated += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de la sesión."""
        return {
            'watch_directory': str(self.watch_directory),
            'start_time': self.start_time,
            'duration': time.time() - self.start_time,
            'files_scanned': self.files_scanned,
            'threats_detected': self.threats_detected,
            'alerts_generated': self.alerts_generated
        }