"""
Adaptadores para infraestructura del sistema.
Implementa interfaces para logging, procesos y alertas.
"""

import json
import psutil
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..core.use_cases import IProcessMonitor, IAlertHandler, ILogger
from ..core.domain import ProcessInfo, AlertEvent


class SystemProcessMonitor(IProcessMonitor):
    """Monitor de procesos del sistema usando psutil."""
    
    def __init__(self):
        self.excluded_processes = {
            'System', 'smss.exe', 'csrss.exe', 'wininit.exe', 'winlogon.exe',
            'services.exe', 'lsass.exe', 'svchost.exe', 'dwm.exe', 'explorer.exe'
        }
    
    def get_running_processes(self) -> List[ProcessInfo]:
        """Obtiene lista de procesos en ejecución."""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                info = proc.info
                
                # Filtrar procesos del sistema
                if info['name'] in self.excluded_processes:
                    continue
                
                exe_path = None
                if info.get('exe'):
                    exe_path = Path(info['exe'])
                
                process_info = ProcessInfo(
                    pid=info['pid'],
                    name=info['name'],
                    exe_path=exe_path,
                    cmdline=' '.join(info.get('cmdline', [])) if info.get('cmdline') else None
                )
                
                processes.append(process_info)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Proceso ya no existe o sin permisos
                continue
            except Exception:
                # Otros errores, continuar
                continue
        
        return processes


class FileSystemAlertHandler(IAlertHandler):
    """Manejador de alertas que escribe a archivos del sistema."""
    
    def __init__(self, alert_log_path: Path, detailed_log_path: Optional[Path] = None):
        self.alert_log_path = alert_log_path
        self.detailed_log_path = detailed_log_path or alert_log_path.parent / "detailed_alerts.json"
        
        # Asegurar que los directorios existan
        self.alert_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.detailed_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def handle_alert(self, alert: AlertEvent) -> bool:
        """Maneja un evento de alerta escribiendo a logs."""
        try:
            # Log de alerta simple
            alert_message = self._format_alert_message(alert)
            with open(self.alert_log_path, 'a', encoding='utf-8') as f:
                f.write(f"{alert_message}\n")
            
            # Log detallado en JSON
            alert_data = alert.to_dict()
            with open(self.detailed_log_path, 'a', encoding='utf-8') as f:
                json.dump(alert_data, f, ensure_ascii=False, indent=2)
                f.write('\n---\n')
            
            return True
            
        except Exception as e:
            print(f"Error manejando alerta: {e}")
            return False
    
    def _format_alert_message(self, alert: AlertEvent) -> str:
        """Formatea mensaje de alerta para log simple."""
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(alert.timestamp))
        
        if alert.event_type == "file_detection":
            return (
                f"[{timestamp_str}] [ALERTA-ARCHIVO] "
                f"Archivo: {alert.detection_result.file_path} | "
                f"Confianza: {alert.detection_result.confidence:.2f} | "
                f"Nivel: {alert.detection_result.threat_level.value} | "
                f"ID: {alert.event_id}"
            )
        elif alert.event_type == "process_detection":
            proc = alert.process_info
            return (
                f"[{timestamp_str}] [ALERTA-PROCESO] "
                f"Proceso: {proc.name} (PID {proc.pid}) | "
                f"Ruta: {proc.exe_path} | "
                f"Confianza: {alert.detection_result.confidence:.2f} | "
                f"ID: {alert.event_id}"
            )
        else:
            return f"[{timestamp_str}] [ALERTA] {alert.event_id} - {alert.event_type}"


class ConsoleAlertHandler(IAlertHandler):
    """Manejador de alertas que imprime a consola."""
    
    def handle_alert(self, alert: AlertEvent) -> bool:
        """Maneja un evento de alerta imprimiendo a consola."""
        try:
            timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(alert.timestamp))
            
            print(f"\n{'='*60}")
            print(f"🚨 ALERTA DE SEGURIDAD - {timestamp_str}")
            print(f"{'='*60}")
            print(f"Tipo: {alert.event_type.upper()}")
            print(f"Severidad: {alert.severity}")
            print(f"Archivo: {alert.detection_result.file_path}")
            print(f"Nivel de amenaza: {alert.detection_result.threat_level.value.upper()}")
            print(f"Confianza: {alert.detection_result.confidence:.2%}")
            
            if alert.process_info:
                print(f"Proceso: {alert.process_info.name} (PID {alert.process_info.pid})")
                if alert.process_info.exe_path:
                    print(f"Ejecutable: {alert.process_info.exe_path}")
            
            print(f"ID del evento: {alert.event_id}")
            print(f"{'='*60}\n")
            
            return True
            
        except Exception as e:
            print(f"Error en ConsoleAlertHandler: {e}")
            return False


class CompositeAlertHandler(IAlertHandler):
    """Manejador compuesto que puede usar múltiples handlers."""
    
    def __init__(self, handlers: List[IAlertHandler]):
        self.handlers = handlers
    
    def handle_alert(self, alert: AlertEvent) -> bool:
        """Maneja alerta usando todos los handlers."""
        success_count = 0
        
        for handler in self.handlers:
            try:
                if handler.handle_alert(alert):
                    success_count += 1
            except Exception as e:
                print(f"Error en handler {type(handler).__name__}: {e}")
        
        # Considerar exitoso si al menos uno funcionó
        return success_count > 0


class FileSystemLogger(ILogger):
    """Logger que escribe a archivos del sistema."""
    
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_info(self, message: str, extra: Dict[str, Any] = None):
        """Registra mensaje informativo."""
        self._write_log("INFO", message, extra)
    
    def log_warning(self, message: str, extra: Dict[str, Any] = None):
        """Registra mensaje de advertencia."""
        self._write_log("WARN", message, extra)
    
    def log_error(self, message: str, extra: Dict[str, Any] = None):
        """Registra mensaje de error."""
        self._write_log("ERROR", message, extra)
    
    def _write_log(self, level: str, message: str, extra: Dict[str, Any] = None):
        """Escribe entrada de log."""
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] {message}"
            
            if extra:
                log_entry += f" | Extra: {json.dumps(extra, ensure_ascii=False)}"
            
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(f"{log_entry}\n")
                
        except Exception as e:
            print(f"Error escribiendo log: {e}")


class ConsoleLogger(ILogger):
    """Logger que imprime a consola."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def log_info(self, message: str, extra: Dict[str, Any] = None):
        """Registra mensaje informativo."""
        if self.verbose:
            self._print_log("INFO", message, extra)
    
    def log_warning(self, message: str, extra: Dict[str, Any] = None):
        """Registra mensaje de advertencia."""
        self._print_log("WARN", message, extra)
    
    def log_error(self, message: str, extra: Dict[str, Any] = None):
        """Registra mensaje de error."""
        self._print_log("ERROR", message, extra)
    
    def _print_log(self, level: str, message: str, extra: Dict[str, Any] = None):
        """Imprime entrada de log."""
        timestamp = time.strftime("%H:%M:%S")
        
        # Colores para diferentes niveles
        colors = {
            "INFO": "\033[36m",   # Cyan
            "WARN": "\033[33m",   # Yellow
            "ERROR": "\033[31m",  # Red
        }
        reset = "\033[0m"
        
        color = colors.get(level, "")
        log_entry = f"{color}[{timestamp}] [{level}] {message}{reset}"
        
        print(log_entry)
        
        if extra and self.verbose:
            print(f"  └─ {json.dumps(extra, ensure_ascii=False, indent=2)}")


class CompositeLogger(ILogger):
    """Logger compuesto que puede usar múltiples loggers."""
    
    def __init__(self, loggers: List[ILogger]):
        self.loggers = loggers
    
    def log_info(self, message: str, extra: Dict[str, Any] = None):
        """Registra en todos los loggers."""
        for logger in self.loggers:
            try:
                logger.log_info(message, extra)
            except Exception:
                pass  # Ignorar errores de loggers individuales
    
    def log_warning(self, message: str, extra: Dict[str, Any] = None):
        """Registra en todos los loggers."""
        for logger in self.loggers:
            try:
                logger.log_warning(message, extra)
            except Exception:
                pass
    
    def log_error(self, message: str, extra: Dict[str, Any] = None):
        """Registra en todos los loggers."""
        for logger in self.loggers:
            try:
                logger.log_error(message, extra)
            except Exception:
                pass