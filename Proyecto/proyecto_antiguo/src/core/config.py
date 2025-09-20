"""
Módulo de configuración del sistema Anti-Keylogger.
Centraliza la configuración y permite diferentes entornos.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, List


@dataclass
class ModelConfig:
    """Configuración del modelo ML."""
    model_path: Path
    features_path: Path
    labels_path: Optional[Path] = None
    threat_threshold: float = 0.6
    model_type: str = "auto"  # "auto", "onnx", "pickle"


@dataclass
class MonitoringConfig:
    """Configuración del monitoreo."""
    watch_directory: Path
    scan_interval: int = 10  # segundos
    monitor_processes: bool = True
    monitor_files: bool = True
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    excluded_extensions: set = None
    
    def __post_init__(self):
        if self.excluded_extensions is None:
            self.excluded_extensions = {'.log', '.tmp', '.temp', '.cache'}


@dataclass
class LoggingConfig:
    """Configuración del logging."""
    log_directory: Path
    log_level: str = "INFO"  # "DEBUG", "INFO", "WARN", "ERROR"
    max_log_size: int = 10 * 1024 * 1024  # 10MB
    console_output: bool = True
    file_output: bool = True


@dataclass
class AlertConfig:
    """Configuración de alertas."""
    alert_directory: Path
    console_alerts: bool = True
    file_alerts: bool = True
    stop_on_threat: bool = False  # Si debe parar al detectar amenaza
    alert_threshold: float = 0.6


@dataclass
class AntiKeyloggerConfig:
    """Configuración principal del sistema."""
    model: ModelConfig
    monitoring: MonitoringConfig
    logging: LoggingConfig
    alerts: AlertConfig
    
    @classmethod
    def create_default(cls, base_directory: Path) -> 'AntiKeyloggerConfig':
        """Crea configuración por defecto."""
        base_dir = Path(base_directory)
        
        # Configuración del modelo
        model = ModelConfig(
            model_path=base_dir / "modelos" / "modelo_keylogger_from_datos.onnx",
            features_path=base_dir / "modelos" / "modelo_keylogger_from_datos_features.json",
            labels_path=base_dir / "modelos" / "label_classes.json",
            threat_threshold=0.6
        )
        
        # Configuración del monitoreo
        monitoring = MonitoringConfig(
            watch_directory=Path.home() / "Downloads",
            scan_interval=10,
            monitor_processes=True,
            monitor_files=True
        )
        
        # Configuración del logging
        logs_dir = base_dir / "logs"
        logging = LoggingConfig(
            log_directory=logs_dir,
            console_output=True,
            file_output=True
        )
        
        # Configuración de alertas
        alerts = AlertConfig(
            alert_directory=logs_dir,
            console_alerts=True,
            file_alerts=True,
            stop_on_threat=False
        )
        
        return cls(
            model=model,
            monitoring=monitoring,
            logging=logging,
            alerts=alerts
        )
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'AntiKeyloggerConfig':
        """Carga configuración desde archivo JSON."""
        import json
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AntiKeyloggerConfig':
        """Crea configuración desde diccionario."""
        model_data = data.get('model', {})
        model = ModelConfig(
            model_path=Path(model_data['model_path']),
            features_path=Path(model_data['features_path']),
            labels_path=Path(model_data['labels_path']) if model_data.get('labels_path') else None,
            threat_threshold=model_data.get('threat_threshold', 0.6),
            model_type=model_data.get('model_type', 'auto')
        )
        
        monitoring_data = data.get('monitoring', {})
        monitoring = MonitoringConfig(
            watch_directory=Path(monitoring_data.get('watch_directory', Path.home() / "Downloads")),
            scan_interval=monitoring_data.get('scan_interval', 10),
            monitor_processes=monitoring_data.get('monitor_processes', True),
            monitor_files=monitoring_data.get('monitor_files', True),
            max_file_size=monitoring_data.get('max_file_size', 100 * 1024 * 1024),
            excluded_extensions=set(monitoring_data.get('excluded_extensions', ['.log', '.tmp', '.temp', '.cache']))
        )
        
        logging_data = data.get('logging', {})
        logging = LoggingConfig(
            log_directory=Path(logging_data.get('log_directory', 'logs')),
            log_level=logging_data.get('log_level', 'INFO'),
            max_log_size=logging_data.get('max_log_size', 10 * 1024 * 1024),
            console_output=logging_data.get('console_output', True),
            file_output=logging_data.get('file_output', True)
        )
        
        alerts_data = data.get('alerts', {})
        alerts = AlertConfig(
            alert_directory=Path(alerts_data.get('alert_directory', 'logs')),
            console_alerts=alerts_data.get('console_alerts', True),
            file_alerts=alerts_data.get('file_alerts', True),
            stop_on_threat=alerts_data.get('stop_on_threat', False),
            alert_threshold=alerts_data.get('alert_threshold', 0.6)
        )
        
        return cls(
            model=model,
            monitoring=monitoring,
            logging=logging,
            alerts=alerts
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte configuración a diccionario."""
        return {
            'model': {
                'model_path': str(self.model.model_path),
                'features_path': str(self.model.features_path),
                'labels_path': str(self.model.labels_path) if self.model.labels_path else None,
                'threat_threshold': self.model.threat_threshold,
                'model_type': self.model.model_type
            },
            'monitoring': {
                'watch_directory': str(self.monitoring.watch_directory),
                'scan_interval': self.monitoring.scan_interval,
                'monitor_processes': self.monitoring.monitor_processes,
                'monitor_files': self.monitoring.monitor_files,
                'max_file_size': self.monitoring.max_file_size,
                'excluded_extensions': list(self.monitoring.excluded_extensions)
            },
            'logging': {
                'log_directory': str(self.logging.log_directory),
                'log_level': self.logging.log_level,
                'max_log_size': self.logging.max_log_size,
                'console_output': self.logging.console_output,
                'file_output': self.logging.file_output
            },
            'alerts': {
                'alert_directory': str(self.alerts.alert_directory),
                'console_alerts': self.alerts.console_alerts,
                'file_alerts': self.alerts.file_alerts,
                'stop_on_threat': self.alerts.stop_on_threat,
                'alert_threshold': self.alerts.alert_threshold
            }
        }
    
    def save_to_file(self, config_path: Path):
        """Guarda configuración a archivo JSON."""
        import json
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    def validate(self) -> List[str]:
        """Valida la configuración y retorna lista de errores."""
        errors = []
        
        # Validar modelo
        if not self.model.model_path.exists():
            errors.append(f"Archivo del modelo no existe: {self.model.model_path}")
        
        if not self.model.features_path.exists():
            errors.append(f"Archivo de features no existe: {self.model.features_path}")
        
        if self.model.labels_path and not self.model.labels_path.exists():
            errors.append(f"Archivo de labels no existe: {self.model.labels_path}")
        
        if not (0.0 <= self.model.threat_threshold <= 1.0):
            errors.append(f"Umbral de amenaza debe estar entre 0.0 y 1.0: {self.model.threat_threshold}")
        
        # Validar monitoreo
        if not self.monitoring.watch_directory.exists():
            errors.append(f"Directorio a monitorear no existe: {self.monitoring.watch_directory}")
        
        if self.monitoring.scan_interval <= 0:
            errors.append(f"Intervalo de escaneo debe ser positivo: {self.monitoring.scan_interval}")
        
        # Validar alertas
        if not (0.0 <= self.alerts.alert_threshold <= 1.0):
            errors.append(f"Umbral de alerta debe estar entre 0.0 y 1.0: {self.alerts.alert_threshold}")
        
        return errors


def create_development_config(base_directory: Path) -> AntiKeyloggerConfig:
    """Crea configuración para desarrollo."""
    config = AntiKeyloggerConfig.create_default(base_directory)
    
    # Configuraciones específicas para desarrollo
    config.logging.log_level = "DEBUG"
    config.logging.console_output = True
    config.alerts.console_alerts = True
    config.alerts.stop_on_threat = True  # Parar en desarrollo para análisis
    config.model.threat_threshold = 0.5  # Más sensible en desarrollo
    
    return config


def create_production_config(base_directory: Path) -> AntiKeyloggerConfig:
    """Crea configuración para producción."""
    config = AntiKeyloggerConfig.create_default(base_directory)
    
    # Configuraciones específicas para producción
    config.logging.log_level = "INFO"
    config.logging.console_output = False
    config.alerts.console_alerts = False
    config.alerts.stop_on_threat = False  # Continuar en producción
    config.model.threat_threshold = 0.7  # Menos falsos positivos
    config.monitoring.scan_interval = 30  # Menos frecuente
    
    return config