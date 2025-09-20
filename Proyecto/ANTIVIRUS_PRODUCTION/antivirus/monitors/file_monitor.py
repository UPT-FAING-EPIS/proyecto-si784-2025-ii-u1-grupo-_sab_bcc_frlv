"""
Monitor del Sistema de Archivos
===============================

Monitorea cambios en el sistema de archivos para detectar actividades
sospechosas relacionadas con keyloggers y malware.
"""

import logging
import threading
import time
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Callable, Optional, Set
from collections import deque
import hashlib

logger = logging.getLogger(__name__)


class FileSystemMonitor:
    """Monitor del sistema de archivos en tiempo real"""
    
    def __init__(self, callback: Optional[Callable] = None, buffer_size: int = 1000):
        self.callback = callback
        self.buffer_size = buffer_size
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Buffer para eventos de archivos
        self.file_events = deque(maxlen=buffer_size)
        
        # Tracking de archivos
        self.tracked_files = {}  # path -> file_info
        self.suspicious_files = set()  # paths sospechosos
        self.quarantined_files = set()  # archivos en cuarentena
        
        # Estadísticas
        self.stats = {
            'files_monitored': 0,
            'suspicious_files_detected': 0,
            'files_quarantined': 0,
            'events_processed': 0,
            'start_time': None,
            'last_scan': None
        }
        
        # Configuración
        self.config = {
            'scan_interval': 5.0,  # segundos
            'monitored_directories': [
                str(Path.home()),  # Directorio del usuario
                'C:\\Windows\\Temp',
                'C:\\Temp',
                'C:\\Users\\Public',
                os.environ.get('APPDATA', ''),
                os.environ.get('LOCALAPPDATA', ''),
                os.environ.get('TEMP', ''),
            ],
            'suspicious_extensions': [
                '.exe', '.dll', '.scr', '.pif', '.com', '.bat', '.cmd',
                '.vbs', '.js', '.jar', '.tmp', '.log'
            ],
            'suspicious_filenames': [
                'keylog', 'password', 'credential', 'capture', 'spy',
                'hack', 'stealer', 'monitor', 'recorder', 'sniffer',
                'temp', 'cache', 'dump', 'backup'
            ],
            'ignore_extensions': [
                '.jpg', '.png', '.gif', '.bmp', '.ico', '.mp3', '.mp4',
                '.avi', '.mkv', '.pdf', '.doc', '.docx', '.xlsx'
            ],
            'max_file_size_mb': 100,  # Tamaño máximo para análisis
            'quarantine_enabled': True,
            'quarantine_directory': 'C:\\Quarantine'
        }
        
        # Filtrar directorios válidos
        self.config['monitored_directories'] = [
            d for d in self.config['monitored_directories'] 
            if d and os.path.exists(d)
        ]
        
        logger.info("[FILE] FileSystemMonitor inicializado")
    
    def start_monitoring(self):
        """Inicia el monitoreo del sistema de archivos"""
        if self.is_monitoring:
            logger.warning("[WARNING] El monitor de archivos ya está activo")
            return
        
        self.is_monitoring = True
        self.stats['start_time'] = datetime.now()
        
        # Crear directorio de cuarentena si no existe
        if self.config['quarantine_enabled']:
            self._ensure_quarantine_directory()
        
        # Escaneo inicial
        self._initial_file_scan()
        
        # Iniciar hilo de monitoreo
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            name="FileSystemMonitor",
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info("[SYNC] Monitor de archivos iniciado")
    
    def stop_monitoring(self):
        """Detiene el monitoreo del sistema de archivos"""
        if not self.is_monitoring:
            logger.warning("[WARNING] El monitor de archivos no está activo")
            return
        
        self.is_monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        
        logger.info("[STOP] Monitor de archivos detenido")
    
    def _ensure_quarantine_directory(self):
        """Asegura que existe el directorio de cuarentena"""
        try:
            quarantine_dir = Path(self.config['quarantine_directory'])
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"[PACKAGE] Directorio de cuarentena: {quarantine_dir}")
        except Exception as e:
            logger.error(f"[ERROR] Error creando directorio de cuarentena: {e}")
            self.config['quarantine_enabled'] = False
    
    def _initial_file_scan(self):
        """Escaneo inicial de archivos existentes"""
        logger.info("[SEARCH] Iniciando escaneo inicial de archivos...")
        
        total_files = 0
        for directory in self.config['monitored_directories']:
            try:
                for file_path in self._scan_directory(directory):
                    file_info = self._get_file_info(file_path)
                    if file_info:
                        self.tracked_files[file_path] = file_info
                        total_files += 1
                        
                        # Verificar si es sospechoso
                        if self._is_suspicious_file(file_info):
                            self._flag_suspicious_file(file_path, file_info, "archivo_existente_sospechoso")
                        
            except Exception as e:
                logger.error(f"[ERROR] Error escaneando {directory}: {e}")
        
        self.stats['files_monitored'] = total_files
        logger.info(f"[DATA] Escaneo inicial completado: {total_files} archivos")
    
    def _scan_directory(self, directory: str, max_depth: int = 3) -> List[str]:
        """Escanea un directorio recursivamente"""
        files = []
        
        try:
            path_obj = Path(directory)
            if not path_obj.exists() or not path_obj.is_dir():
                return files
            
            # Escaneo recursivo con límite de profundidad
            for root, dirs, filenames in os.walk(directory):
                # Controlar profundidad
                depth = len(Path(root).relative_to(path_obj).parts)
                if depth > max_depth:
                    dirs.clear()  # No profundizar más
                    continue
                
                # Filtrar directorios del sistema que causan problemas
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d.lower() not in ['system volume information', '$recycle.bin']]
                
                for filename in filenames:
                    try:
                        file_path = os.path.join(root, filename)
                        if self._should_monitor_file(file_path):
                            files.append(file_path)
                    except Exception:
                        continue
                
                # Limitar número de archivos por directorio
                if len(files) > 10000:
                    break
                    
        except (PermissionError, OSError) as e:
            logger.debug(f"Sin acceso a {directory}: {e}")
        except Exception as e:
            logger.error(f"[ERROR] Error escaneando directorio {directory}: {e}")
        
        return files
    
    def _should_monitor_file(self, file_path: str) -> bool:
        """Determina si un archivo debe ser monitoreado"""
        try:
            path_obj = Path(file_path)
            
            # Verificar extensión
            extension = path_obj.suffix.lower()
            if extension in self.config['ignore_extensions']:
                return False
            
            # Verificar tamaño
            try:
                size_mb = path_obj.stat().st_size / (1024 * 1024)
                if size_mb > self.config['max_file_size_mb']:
                    return False
            except (OSError, FileNotFoundError):
                return False
            
            # Verificar si es archivo del sistema crítico
            system_paths = ['windows\\system32', 'windows\\syswow64', 'program files']
            file_path_lower = file_path.lower()
            if any(sys_path in file_path_lower for sys_path in system_paths):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _monitoring_loop(self):
        """Bucle principal de monitoreo"""
        logger.info("[SEARCH] Iniciando bucle de monitoreo de archivos...")
        
        while self.is_monitoring:
            try:
                self._scan_for_changes()
                time.sleep(self.config['scan_interval'])
                
            except Exception as e:
                logger.error(f"[ERROR] Error en bucle de monitoreo: {e}")
                time.sleep(10)
    
    def _scan_for_changes(self):
        """Escanea cambios en archivos monitoreados"""
        self.stats['last_scan'] = datetime.now()
        changes_detected = 0
        
        # Verificar archivos existentes
        files_to_remove = []
        for file_path, old_info in self.tracked_files.items():
            try:
                if not os.path.exists(file_path):
                    # Archivo eliminado
                    self._handle_file_deleted(file_path, old_info)
                    files_to_remove.append(file_path)
                    changes_detected += 1
                else:
                    # Verificar modificaciones
                    current_info = self._get_file_info(file_path)
                    if current_info and self._file_changed(old_info, current_info):
                        self._handle_file_modified(file_path, old_info, current_info)
                        self.tracked_files[file_path] = current_info
                        changes_detected += 1
                        
            except Exception as e:
                logger.debug(f"Error verificando {file_path}: {e}")
        
        # Remover archivos eliminados
        for file_path in files_to_remove:
            del self.tracked_files[file_path]
        
        # Buscar archivos nuevos en directorios monitoreados
        for directory in self.config['monitored_directories'][:3]:  # Limitar a 3 directorios por ciclo
            try:
                new_files = self._find_new_files(directory)
                for file_path in new_files:
                    file_info = self._get_file_info(file_path)
                    if file_info:
                        self._handle_file_created(file_path, file_info)
                        self.tracked_files[file_path] = file_info
                        changes_detected += 1
                        
            except Exception as e:
                logger.debug(f"Error buscando nuevos archivos en {directory}: {e}")
        
        if changes_detected > 0:
            logger.debug(f"[DATA] Detectados {changes_detected} cambios en archivos")
    
    def _find_new_files(self, directory: str) -> List[str]:
        """Encuentra archivos nuevos en un directorio"""
        new_files = []
        
        try:
            # Escaneo superficial (solo nivel superior)
            for item in os.listdir(directory):
                file_path = os.path.join(directory, item)
                
                if (os.path.isfile(file_path) and 
                    file_path not in self.tracked_files and
                    self._should_monitor_file(file_path)):
                    
                    new_files.append(file_path)
                    
                    # Limitar nuevos archivos por ciclo
                    if len(new_files) >= 20:
                        break
                        
        except (PermissionError, OSError, FileNotFoundError):
            pass
        except Exception as e:
            logger.debug(f"Error buscando nuevos archivos: {e}")
        
        return new_files
    
    def _get_file_info(self, file_path: str) -> Optional[Dict]:
        """Obtiene información detallada de un archivo"""
        try:
            path_obj = Path(file_path)
            stat = path_obj.stat()
            
            info = {
                'path': file_path,
                'name': path_obj.name,
                'extension': path_obj.suffix.lower(),
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime,
                'is_hidden': self._is_hidden_file(file_path),
                'analysis_timestamp': datetime.now().timestamp()
            }
            
            # Hash del archivo (solo para archivos pequeños)
            if stat.st_size < 1024 * 1024:  # < 1MB
                info['hash'] = self._calculate_file_hash(file_path)
            
            # Análisis de contenido
            info.update(self._analyze_file_content(file_path, info))
            
            return info
            
        except (OSError, FileNotFoundError, PermissionError):
            return None
        except Exception as e:
            logger.debug(f"Error obteniendo info de {file_path}: {e}")
            return None
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcula el hash SHA256 de un archivo"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""
    
    def _is_hidden_file(self, file_path: str) -> bool:
        """Verifica si un archivo está oculto"""
        try:
            import stat
            return bool(os.stat(file_path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
        except Exception:
            return Path(file_path).name.startswith('.')
    
    def _analyze_file_content(self, file_path: str, file_info: Dict) -> Dict:
        """Analiza el contenido del archivo"""
        analysis = {
            'is_executable': False,
            'has_suspicious_strings': False,
            'contains_credentials': False,
            'is_log_file': False,
            'risk_score': 0.0
        }
        
        try:
            extension = file_info.get('extension', '').lower()
            name = file_info.get('name', '').lower()
            
            # Verificar si es ejecutable
            if extension in ['.exe', '.dll', '.scr', '.pif', '.com', '.bat', '.cmd', '.vbs', '.js']:
                analysis['is_executable'] = True
                analysis['risk_score'] += 0.3
            
            # Verificar nombre sospechoso
            for suspicious in self.config['suspicious_filenames']:
                if suspicious in name:
                    analysis['has_suspicious_strings'] = True
                    analysis['risk_score'] += 0.4
                    break
            
            # Análisis de contenido para archivos de texto pequeños
            if (extension in ['.txt', '.log', '.cfg', '.ini', '.conf'] and 
                file_info.get('size', 0) < 100 * 1024):  # < 100KB
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(1000)  # Primeros 1000 caracteres
                        
                        # Buscar patrones de credenciales
                        credential_patterns = [
                            'password', 'passwd', 'pwd', 'user', 'login',
                            'credential', 'token', 'key', 'secret', 'auth'
                        ]
                        
                        content_lower = content.lower()
                        for pattern in credential_patterns:
                            if pattern in content_lower:
                                analysis['contains_credentials'] = True
                                analysis['risk_score'] += 0.5
                                break
                        
                        # Verificar si es archivo de log
                        if any(word in content_lower for word in ['log', 'event', 'timestamp', 'date']):
                            analysis['is_log_file'] = True
                            analysis['risk_score'] += 0.2
                            
                except Exception:
                    pass
            
            # Verificar ubicación sospechosa
            path_lower = file_path.lower()
            suspicious_locations = ['temp', 'tmp', 'cache', 'appdata\\local\\temp']
            if any(location in path_lower for location in suspicious_locations):
                analysis['risk_score'] += 0.2
            
        except Exception as e:
            logger.debug(f"Error analizando contenido de {file_path}: {e}")
        
        return analysis
    
    def _file_changed(self, old_info: Dict, new_info: Dict) -> bool:
        """Verifica si un archivo ha cambiado"""
        return (old_info.get('modified', 0) != new_info.get('modified', 0) or
                old_info.get('size', 0) != new_info.get('size', 0))
    
    def _is_suspicious_file(self, file_info: Dict) -> bool:
        """Determina si un archivo es sospechoso"""
        risk_score = file_info.get('risk_score', 0.0)
        
        # Criterios de sospecha
        suspicious_criteria = [
            risk_score > 0.6,
            file_info.get('has_suspicious_strings', False),
            file_info.get('contains_credentials', False),
            file_info.get('is_executable', False) and file_info.get('is_hidden', False),
            file_info.get('size', 0) == 0 and file_info.get('extension') in ['.exe', '.dll']
        ]
        
        return any(suspicious_criteria)
    
    def _handle_file_created(self, file_path: str, file_info: Dict):
        """Maneja la creación de un archivo"""
        event = {
            'type': 'file_created',
            'path': file_path,
            'file_info': file_info,
            'timestamp': datetime.now().isoformat()
        }
        
        self.file_events.append(event)
        self.stats['events_processed'] += 1
        
        # Verificar si es sospechoso
        if self._is_suspicious_file(file_info):
            self._flag_suspicious_file(file_path, file_info, "archivo_nuevo_sospechoso")
        
        logger.debug(f"[DOC] Archivo creado: {file_path}")
    
    def _handle_file_modified(self, file_path: str, old_info: Dict, new_info: Dict):
        """Maneja la modificación de un archivo"""
        event = {
            'type': 'file_modified',
            'path': file_path,
            'old_info': old_info,
            'new_info': new_info,
            'timestamp': datetime.now().isoformat()
        }
        
        self.file_events.append(event)
        self.stats['events_processed'] += 1
        
        # Verificar si se volvió sospechoso
        if not self._is_suspicious_file(old_info) and self._is_suspicious_file(new_info):
            self._flag_suspicious_file(file_path, new_info, "archivo_modificado_sospechoso")
        
        logger.debug(f"[EDIT] Archivo modificado: {file_path}")
    
    def _handle_file_deleted(self, file_path: str, file_info: Dict):
        """Maneja la eliminación de un archivo"""
        event = {
            'type': 'file_deleted',
            'path': file_path,
            'file_info': file_info,
            'timestamp': datetime.now().isoformat()
        }
        
        self.file_events.append(event)
        self.stats['events_processed'] += 1
        
        # Remover de archivos sospechosos
        self.suspicious_files.discard(file_path)
        
        logger.debug(f"[DELETE] Archivo eliminado: {file_path}")
    
    def _flag_suspicious_file(self, file_path: str, file_info: Dict, reason: str):
        """Marca un archivo como sospechoso"""
        if file_path not in self.suspicious_files:
            self.suspicious_files.add(file_path)
            self.stats['suspicious_files_detected'] += 1
            
            # Crear evento de amenaza
            threat_data = {
                'type': 'suspicious_file',
                'path': file_path,
                'file_info': file_info,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'risk_score': file_info.get('risk_score', 0.0)
            }
            
            logger.warning(f"[ALERT] Archivo sospechoso detectado: {file_path} - {reason}")
            
            # Cuarentena automática si está habilitada
            if (self.config['quarantine_enabled'] and 
                file_info.get('risk_score', 0.0) > 0.8):
                self._quarantine_file(file_path)
            
            # Llamar callback
            if self.callback:
                self.callback(threat_data)
    
    def _quarantine_file(self, file_path: str) -> bool:
        """Pone un archivo en cuarentena"""
        try:
            if not self.config['quarantine_enabled']:
                return False
            
            source_path = Path(file_path)
            if not source_path.exists():
                return False
            
            # Crear nombre único en cuarentena
            quarantine_dir = Path(self.config['quarantine_directory'])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quarantine_name = f"{timestamp}_{source_path.name}"
            quarantine_path = quarantine_dir / quarantine_name
            
            # Mover archivo a cuarentena
            source_path.rename(quarantine_path)
            
            # Crear archivo de metadatos
            metadata = {
                'original_path': str(source_path),
                'quarantine_time': datetime.now().isoformat(),
                'reason': 'suspicious_file_detected',
                'file_hash': self._calculate_file_hash(str(quarantine_path))
            }
            
            metadata_path = quarantine_path.with_suffix(quarantine_path.suffix + '.metadata')
            with open(metadata_path, 'w') as f:
                import json
                json.dump(metadata, f, indent=2)
            
            self.quarantined_files.add(str(quarantine_path))
            self.stats['files_quarantined'] += 1
            
            logger.warning(f"[LOCK] Archivo puesto en cuarentena: {file_path} -> {quarantine_path}")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Error poniendo archivo en cuarentena: {e}")
            return False
    
    def get_recent_data(self, count: Optional[int] = None) -> List[Dict]:
        """Obtiene eventos recientes de archivos"""
        if count is None:
            return list(self.file_events)
        else:
            return list(self.file_events)[-count:]
    
    def get_suspicious_files(self) -> List[str]:
        """Obtiene lista de archivos sospechosos"""
        return list(self.suspicious_files)
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del monitor"""
        stats = self.stats.copy()
        stats.update({
            'suspicious_files_active': len(self.suspicious_files),
            'quarantined_files': len(self.quarantined_files),
            'tracked_files': len(self.tracked_files),
            'is_monitoring': self.is_monitoring
        })
        
        if stats['start_time']:
            uptime = (datetime.now() - stats['start_time']).total_seconds()
            stats['uptime_seconds'] = uptime
        
        return stats
    
    def is_active(self) -> bool:
        """Verifica si el monitor está activo"""
        return self.is_monitoring
    
    def restore_quarantined_file(self, quarantine_path: str) -> bool:
        """Restaura un archivo de la cuarentena"""
        try:
            quarantine_file = Path(quarantine_path)
            metadata_file = quarantine_file.with_suffix(quarantine_file.suffix + '.metadata')
            
            if not quarantine_file.exists() or not metadata_file.exists():
                return False
            
            # Leer metadatos
            with open(metadata_file, 'r') as f:
                import json
                metadata = json.load(f)
            
            original_path = Path(metadata['original_path'])
            
            # Restaurar archivo
            quarantine_file.rename(original_path)
            metadata_file.unlink()  # Eliminar metadatos
            
            self.quarantined_files.discard(quarantine_path)
            self.suspicious_files.discard(str(original_path))
            
            logger.info(f"[OUT] Archivo restaurado: {quarantine_path} -> {original_path}")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Error restaurando archivo: {e}")
            return False


def test_file_monitor():
    """Función de prueba del monitor de archivos"""
    def on_suspicious_file(data):
        print(f"🚨 Archivo sospechoso: {data['path']}")
        print(f"   Razón: {data['reason']}")
        print(f"   Risk Score: {data['risk_score']:.2f}")
        print(f"   Tamaño: {data['file_info'].get('size', 0)} bytes")
    
    monitor = FileSystemMonitor(callback=on_suspicious_file)
    
    try:
        print("[FILE] Iniciando test del monitor de archivos...")
        monitor.start_monitoring()
        
        # Ejecutar por 60 segundos
        for i in range(12):
            time.sleep(5)
            stats = monitor.get_stats()
            print(f"[DATA] [{i*5:2d}s] Archivos: {stats['tracked_files']}, Sospechosos: {stats['suspicious_files_active']}")
        
        # Mostrar archivos sospechosos
        suspicious = monitor.get_suspicious_files()
        if suspicious:
            print(f"\n🚨 Archivos sospechosos detectados ({len(suspicious)}):")
            for file_path in suspicious[:5]:  # Mostrar solo los primeros 5
                print(f"   - {file_path}")
        else:
            print("\n[OK] No se detectaron archivos sospechosos")
        
    except KeyboardInterrupt:
        print("\n[STOP] Test interrumpido por usuario")
    
    finally:
        monitor.stop_monitoring()
        print("[OK] Test completado")


if __name__ == "__main__":
    test_file_monitor()