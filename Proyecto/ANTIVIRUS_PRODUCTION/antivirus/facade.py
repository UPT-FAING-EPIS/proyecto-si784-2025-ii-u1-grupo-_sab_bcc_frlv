"""
API Facade Simplificada para el Sistema Antivirus
================================================

Interfaz unificada y simple para usar el sistema completo.
"""

from .core.engine import AntiKeyloggerEngine
from typing import Dict, List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class AntivirusFacade:
    """
    Facade Pattern: Interfaz simplificada para el sistema antivirus
    """
    
    def __init__(self, config_file: str = "config.toml"):
        """Inicializa el sistema completo con una sola línea"""
        self.engine = AntiKeyloggerEngine(config_file)
        self._is_monitoring = False
        
    # ========== MÉTODOS SIMPLES (FACADE) ==========
    
    def start(self) -> bool:
        """Inicia todo el sistema de protección"""
        try:
            self.engine.start_protection()
            self._is_monitoring = True
            return True
        except Exception as e:
            logger.error(f"Error iniciando sistema: {e}")
            return False
    
    def stop(self) -> bool:
        """Detiene todo el sistema"""
        try:
            self.engine.stop_protection()
            self._is_monitoring = False
            return True
        except Exception as e:
            logger.error(f"Error deteniendo sistema: {e}")
            return False
    
    def scan_file(self, file_path: str) -> Dict:
        """Escanea un archivo individual"""
        return self.engine.scan_file(file_path)
    
    def scan_directory(self, directory_path: str) -> List[Dict]:
        """Escanea un directorio completo"""
        return self.engine.scan_directory(directory_path)
    
    def get_status(self) -> Dict:
        """Obtiene el estado completo del sistema"""
        return {
            'is_monitoring': self._is_monitoring,
            'stats': self.engine.get_statistics(),
            'threats_detected': self.engine.stats['threats_detected'],
            'uptime': self.engine.get_uptime()
        }
    
    def get_threats(self) -> List[Dict]:
        """Obtiene lista de amenazas detectadas"""
        return self.engine.get_threat_history()
    
    def add_alert_handler(self, handler: Callable):
        """Añade un manejador para alertas de amenazas"""
        self.engine.add_threat_callback(handler)
    
    # ========== CONFIGURACIÓN SIMPLE ==========
    
    def set_sensitivity(self, level: str):
        """Configura sensibilidad: 'low', 'medium', 'high'"""
        thresholds = {
            'low': 0.9,
            'medium': 0.8,
            'high': 0.6
        }
        if level in thresholds and self.engine.ml_detector is not None:
            self.engine.ml_detector.confidence_threshold = thresholds[level]
            logger.info(f"Sensibilidad configurada a: {level}")
        else:
            logger.warning(f"No se pudo configurar sensibilidad: ML detector no disponible")
    
    def enable_realtime_protection(self, enabled: bool = True):
        """Habilita/deshabilita protección en tiempo real"""
        if enabled and not self._is_monitoring:
            self.start()
        elif not enabled and self._is_monitoring:
            self.stop()


# ========== USO SIMPLIFICADO ==========

def create_antivirus(config_file: str = "config.toml") -> AntivirusFacade:
    """Factory method para crear instancia del antivirus"""
    return AntivirusFacade(config_file)


# ========== EJEMPLO DE USO ==========
if __name__ == "__main__":
    # Uso super simple con Facade:
    antivirus = create_antivirus()
    
    # Configurar
    antivirus.set_sensitivity('medium')
    antivirus.add_alert_handler(lambda threat: print(f"🚨 AMENAZA: {threat}"))
    
    # Iniciar protección
    if antivirus.start():
        print("✅ Antivirus iniciado")
        
        # Escanear archivo
        result = antivirus.scan_file("archivo_sospechoso.exe")
        print(f"Resultado: {result}")
        
        # Ver estado
        status = antivirus.get_status()
        print(f"Estado: {status}")
        
        # Detener
        antivirus.stop()
        print("🛑 Antivirus detenido")