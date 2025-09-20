"""
Interfaces para Strategy Pattern
===============================

Define interfaces comunes para detectores y monitores.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class DetectorInterface(ABC):
    """Interface para todos los detectores (Strategy Pattern)"""
    
    @abstractmethod
    def detect(self, data: Dict) -> bool:
        """Detecta amenazas en los datos proporcionados"""
        pass
    
    @abstractmethod
    def get_confidence(self) -> float:
        """Retorna la confianza de la última detección"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Retorna el nombre del detector"""
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict:
        """Retorna estadísticas del detector"""
        pass


class MonitorInterface(ABC):
    """Interface para todos los monitores (Strategy Pattern)"""
    
    @abstractmethod
    def start_monitoring(self) -> bool:
        """Inicia el monitoreo"""
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> bool:
        """Detiene el monitoreo"""
        pass
    
    @abstractmethod
    def is_monitoring(self) -> bool:
        """Verifica si está monitoreando"""
        pass
    
    @abstractmethod
    def get_data(self) -> List[Dict]:
        """Obtiene datos capturados"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Retorna el nombre del monitor"""
        pass


class ThreatHandlerInterface(ABC):
    """Interface para manejadores de amenazas (Strategy Pattern)"""
    
    @abstractmethod
    def handle_threat(self, threat: Dict) -> bool:
        """Maneja una amenaza detectada"""
        pass
    
    @abstractmethod
    def get_handler_type(self) -> str:
        """Retorna el tipo de manejador"""
        pass


# ========== IMPLEMENTACIONES BASE ==========

class BaseDetector(DetectorInterface):
    """Clase base para detectores"""
    
    def __init__(self, name: str):
        self.name = name
        self.confidence = 0.0
        self.detections = 0
        self.false_positives = 0
    
    def get_name(self) -> str:
        return self.name
    
    def get_confidence(self) -> float:
        return self.confidence
    
    def get_statistics(self) -> Dict:
        return {
            'name': self.name,
            'detections': self.detections,
            'false_positives': self.false_positives,
            'accuracy': (self.detections - self.false_positives) / max(self.detections, 1)
        }


class BaseMonitor(MonitorInterface):
    """Clase base para monitores"""
    
    def __init__(self, name: str):
        self.name = name
        self._is_monitoring = False
        self.data_buffer = []
    
    def get_name(self) -> str:
        return self.name
    
    def is_monitoring(self) -> bool:
        return self._is_monitoring
    
    def get_data(self) -> List[Dict]:
        return self.data_buffer.copy()


# ========== FACTORY PATTERN ==========

class DetectorFactory:
    """Factory para crear detectores (Strategy Pattern)"""
    
    _detectors = {}
    
    @classmethod
    def register_detector(cls, name: str, detector_class):
        """Registra un nuevo tipo de detector"""
        cls._detectors[name] = detector_class
    
    @classmethod
    def create_detector(cls, name: str, **kwargs) -> DetectorInterface:
        """Crea un detector por nombre"""
        if name not in cls._detectors:
            raise ValueError(f"Detector desconocido: {name}")
        
        return cls._detectors[name](**kwargs)
    
    @classmethod
    def get_available_detectors(cls) -> List[str]:
        """Lista detectores disponibles"""
        return list(cls._detectors.keys())


class MonitorFactory:
    """Factory para crear monitores (Strategy Pattern)"""
    
    _monitors = {}
    
    @classmethod
    def register_monitor(cls, name: str, monitor_class):
        """Registra un nuevo tipo de monitor"""
        cls._monitors[name] = monitor_class
    
    @classmethod
    def create_monitor(cls, name: str, **kwargs) -> MonitorInterface:
        """Crea un monitor por nombre"""
        if name not in cls._monitors:
            raise ValueError(f"Monitor desconocido: {name}")
        
        return cls._monitors[name](**kwargs)
    
    @classmethod
    def get_available_monitors(cls) -> List[str]:
        """Lista monitores disponibles"""
        return list(cls._monitors.keys())