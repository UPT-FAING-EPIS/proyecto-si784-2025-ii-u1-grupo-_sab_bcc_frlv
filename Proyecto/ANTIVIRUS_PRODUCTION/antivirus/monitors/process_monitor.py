"""
Monitor de Comportamiento de Procesos
=====================================

Monitorea el comportamiento de procesos en tiempo real para detectar
actividades sospechosas típicas de keyloggers.
"""

import logging
import threading
import time
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional, Set
from collections import deque, defaultdict

logger = logging.getLogger(__name__)


class ProcessBehaviorMonitor:
    """Monitor de comportamiento de procesos en tiempo real"""
    
    def __init__(self, callback: Optional[Callable] = None, buffer_size: int = 500):
        self.callback = callback
        self.buffer_size = buffer_size
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Buffers para datos
        self.process_data = deque(maxlen=buffer_size)
        self.process_history = defaultdict(list)  # Historial por PID
        
        # Tracking de procesos
        self.tracked_processes = {}  # PID -> process_info
        self.suspicious_processes = set()  # PIDs sospechosos
        
        # Estadísticas
        self.stats = {
            'processes_monitored': 0,
            'suspicious_activities': 0,
            'keylogger_patterns': 0,
            'start_time': None,
            'last_scan': None
        }
        
        # Configuración
        self.config = {
            'scan_interval': 2.0,  # segundos
            'track_new_processes': True,
            'monitor_file_access': True,
            'monitor_network_connections': True,
            'monitor_keyboard_hooks': True,
            'suspicious_file_patterns': [
                'keylog', 'capture', 'password', 'credential', 'spy',
                'hack', 'stealer', 'monitor', '.log', '.txt'
            ],
            'suspicious_process_names': [
                'keylogger', 'spyware', 'stealer', 'hack', 'spy',
                'capture', 'monitor', 'logger', 'recorder'
            ],
            'system_processes_whitelist': [
                'system', 'svchost.exe', 'explorer.exe', 'winlogon.exe',
                'csrss.exe', 'wininit.exe', 'services.exe', 'lsass.exe'
            ]
        }
        
        logger.info("[PROC] ProcessBehaviorMonitor inicializado")
    
    def start_monitoring(self):
        """Inicia el monitoreo de procesos"""
        if self.is_monitoring:
            logger.warning("[WARNING] El monitor de procesos ya está activo")
            return
        
        self.is_monitoring = True
        self.stats['start_time'] = datetime.now()
        
        # Obtener snapshot inicial de procesos
        self._initial_process_scan()
        
        # Iniciar hilo de monitoreo
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            name="ProcessMonitor",
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info("[SYNC] Monitor de procesos iniciado")
    
    def stop_monitoring(self):
        """Detiene el monitoreo de procesos"""
        if not self.is_monitoring:
            logger.warning("[WARNING] El monitor de procesos no está activo")
            return
        
        self.is_monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        
        logger.info("[STOP] Monitor de procesos detenido")
    
    def _initial_process_scan(self):
        """Escaneo inicial de procesos existentes"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                try:
                    proc_info = proc.info
                    self.tracked_processes[proc_info['pid']] = {
                        'name': proc_info['name'],
                        'create_time': proc_info['create_time'],
                        'first_seen': datetime.now(),
                        'is_new': False
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            logger.info(f"[DATA] Snapshot inicial: {len(self.tracked_processes)} procesos")
            
        except Exception as e:
            logger.error(f"[ERROR] Error en escaneo inicial: {e}")
    
    def _monitoring_loop(self):
        """Bucle principal de monitoreo"""
        logger.info("[SEARCH] Iniciando bucle de monitoreo de procesos...")
        
        while self.is_monitoring:
            try:
                self._scan_processes()
                time.sleep(self.config['scan_interval'])
                
            except Exception as e:
                logger.error(f"[ERROR] Error en bucle de monitoreo: {e}")
                time.sleep(5)
    
    def _scan_processes(self):
        """Escanea procesos activos y detecta cambios"""
        current_pids = set()
        self.stats['last_scan'] = datetime.now()
        
        try:
            for proc in psutil.process_iter():
                try:
                    pid = proc.pid
                    current_pids.add(pid)
                    
                    # Proceso nuevo
                    if pid not in self.tracked_processes:
                        self._handle_new_process(proc)
                    else:
                        # Proceso existente - verificar actividad
                        self._analyze_existing_process(proc)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Detectar procesos terminados
            terminated_pids = set(self.tracked_processes.keys()) - current_pids
            for pid in terminated_pids:
                self._handle_terminated_process(pid)
            
        except Exception as e:
            logger.error(f"[ERROR] Error escaneando procesos: {e}")
    
    def _handle_new_process(self, proc):
        """Maneja un proceso nuevo"""
        try:
            proc_info = self._extract_process_info(proc)
            proc_info['is_new'] = True
            proc_info['first_seen'] = datetime.now()
            
            self.tracked_processes[proc.pid] = proc_info
            self.stats['processes_monitored'] += 1
            
            # Analizar si es sospechoso
            if self._is_suspicious_process(proc_info):
                self._flag_suspicious_process(proc.pid, proc_info, "nuevo_proceso_sospechoso")
            
            logger.debug(f"[STATS] Nuevo proceso: {proc_info['name']} (PID: {proc.pid})")
            
        except Exception as e:
            logger.debug(f"Error procesando nuevo proceso: {e}")
    
    def _analyze_existing_process(self, proc):
        """Analiza un proceso existente"""
        try:
            current_info = self._extract_process_info(proc)
            pid = proc.pid
            
            # Obtener info previa
            prev_info = self.tracked_processes.get(pid, {})
            
            # Detectar cambios sospechosos
            suspicious_changes = self._detect_suspicious_changes(prev_info, current_info)
            
            if suspicious_changes:
                for change_type in suspicious_changes:
                    self._flag_suspicious_process(pid, current_info, change_type)
            
            # Actualizar información
            self.tracked_processes[pid].update(current_info)
            
            # Añadir al historial
            self.process_history[pid].append({
                'timestamp': datetime.now(),
                'info': current_info.copy()
            })
            
            # Limitar historial
            if len(self.process_history[pid]) > 20:
                self.process_history[pid].pop(0)
                
        except Exception as e:
            logger.debug(f"Error analizando proceso {proc.pid}: {e}")
    
    def _extract_process_info(self, proc) -> Dict:
        """Extrae información detallada de un proceso"""
        info = {}
        
        try:
            # Información básica
            info.update({
                'pid': proc.pid,
                'name': proc.name(),
                'exe': proc.exe() if proc.exe() else 'unknown',
                'cmdline': ' '.join(proc.cmdline()) if proc.cmdline() else '',
                'create_time': proc.create_time(),
                'status': proc.status(),
                'username': proc.username() if proc.username() else 'unknown'
            })
            
            # Información de memoria
            memory_info = proc.memory_info()
            info.update({
                'memory_rss': memory_info.rss,
                'memory_vms': memory_info.vms,
                'memory_percent': proc.memory_percent()
            })
            
            # Información de CPU
            info.update({
                'cpu_percent': proc.cpu_percent(),
                'num_threads': proc.num_threads()
            })
            
            # Archivos abiertos (limitado)
            try:
                open_files = proc.open_files()
                info['open_files'] = [f.path for f in open_files[:10]]  # Limitar a 10
                info['open_files_count'] = len(open_files)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                info['open_files'] = []
                info['open_files_count'] = 0
            
            # Conexiones de red
            try:
                connections = proc.connections()
                info['network_connections'] = len(connections)
                info['external_connections'] = len([c for c in connections 
                                                   if c.raddr and not self._is_local_ip(c.raddr.ip)])
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                info['network_connections'] = 0
                info['external_connections'] = 0
            
            # Análisis de comportamiento
            info.update(self._analyze_process_behavior(info))
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            logger.debug(f"Error accediendo a proceso: {e}")
            info['error'] = str(e)
        
        return info
    
    def _analyze_process_behavior(self, proc_info: Dict) -> Dict:
        """Analiza el comportamiento del proceso"""
        behaviors = []
        risk_score = 0.0
        
        name = proc_info.get('name', '').lower()
        exe = proc_info.get('exe', '').lower()
        cmdline = proc_info.get('cmdline', '').lower()
        
        # Verificar nombre sospechoso
        for suspicious_name in self.config['suspicious_process_names']:
            if suspicious_name in name or suspicious_name in exe:
                behaviors.append('suspicious_name')
                risk_score += 0.8
                break
        
        # Verificar archivos abiertos sospechosos
        open_files = proc_info.get('open_files', [])
        for file_path in open_files:
            file_path_lower = file_path.lower()
            for pattern in self.config['suspicious_file_patterns']:
                if pattern in file_path_lower:
                    behaviors.append('suspicious_file_access')
                    risk_score += 0.3
                    break
        
        # Verificar conexiones externas sospechosas
        external_connections = proc_info.get('external_connections', 0)
        if external_connections > 0 and not self._is_whitelisted_process(name):
            behaviors.append('external_network_access')
            risk_score += 0.2 * min(external_connections, 5)
        
        # Verificar patrones de keylogger
        keylogger_indicators = [
            'hook' in cmdline,
            'keyboard' in cmdline,
            'capture' in cmdline,
            'log' in cmdline and 'key' in cmdline,
            proc_info.get('open_files_count', 0) > 20,  # Muchos archivos abiertos
            proc_info.get('memory_percent', 0) < 1.0 and external_connections > 0  # Bajo uso de memoria pero con red
        ]
        
        if sum(keylogger_indicators) >= 2:
            behaviors.append('keylogger_pattern')
            risk_score += 1.0
        
        # Verificar proceso oculto o sin ventana
        if proc_info.get('username') != 'SYSTEM' and 'explorer' not in name:
            # Proceso potencialmente oculto
            behaviors.append('potentially_hidden')
            risk_score += 0.1
        
        return {
            'behaviors': behaviors,
            'risk_score': min(risk_score, 1.0),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _detect_suspicious_changes(self, prev_info: Dict, current_info: Dict) -> List[str]:
        """Detecta cambios sospechosos en un proceso"""
        changes = []
        
        try:
            # Incremento súbito en conexiones de red
            prev_connections = prev_info.get('external_connections', 0)
            current_connections = current_info.get('external_connections', 0)
            
            if current_connections > prev_connections + 3:
                changes.append('sudden_network_increase')
            
            # Incremento súbito en archivos abiertos
            prev_files = prev_info.get('open_files_count', 0)
            current_files = current_info.get('open_files_count', 0)
            
            if current_files > prev_files + 10:
                changes.append('sudden_file_access_increase')
            
            # Cambio en comportamientos
            prev_behaviors = set(prev_info.get('behaviors', []))
            current_behaviors = set(current_info.get('behaviors', []))
            
            new_behaviors = current_behaviors - prev_behaviors
            if 'keylogger_pattern' in new_behaviors:
                changes.append('new_keylogger_behavior')
            
        except Exception as e:
            logger.debug(f"Error detectando cambios: {e}")
        
        return changes
    
    def _is_suspicious_process(self, proc_info: Dict) -> bool:
        """Determina si un proceso es sospechoso"""
        risk_score = proc_info.get('risk_score', 0.0)
        behaviors = proc_info.get('behaviors', [])
        
        # Criterios de sospecha
        suspicious_criteria = [
            risk_score > 0.7,
            'keylogger_pattern' in behaviors,
            'suspicious_name' in behaviors,
            len(behaviors) >= 3
        ]
        
        return any(suspicious_criteria)
    
    def _flag_suspicious_process(self, pid: int, proc_info: Dict, reason: str):
        """Marca un proceso como sospechoso"""
        if pid not in self.suspicious_processes:
            self.suspicious_processes.add(pid)
            self.stats['suspicious_activities'] += 1
            
            if 'keylogger' in reason.lower():
                self.stats['keylogger_patterns'] += 1
            
            # Crear evento de amenaza
            threat_data = {
                'type': 'suspicious_process',
                'pid': pid,
                'process_info': proc_info,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'behaviors': proc_info.get('behaviors', []),
                'risk_score': proc_info.get('risk_score', 0.0)
            }
            
            logger.warning(f"[ALERT] Proceso sospechoso detectado: {proc_info.get('name')} (PID: {pid}) - {reason}")
            
            # Llamar callback
            if self.callback:
                self.callback(threat_data)
    
    def _handle_terminated_process(self, pid: int):
        """Maneja un proceso terminado"""
        if pid in self.tracked_processes:
            proc_info = self.tracked_processes.pop(pid)
            logger.debug(f"📉 Proceso terminado: {proc_info.get('name')} (PID: {pid})")
        
        # Limpiar de procesos sospechosos
        self.suspicious_processes.discard(pid)
        
        # Limpiar historial antiguo
        if pid in self.process_history:
            del self.process_history[pid]
    
    def _is_local_ip(self, ip: str) -> bool:
        """Verifica si una IP es local"""
        try:
            import ipaddress
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private or ip_obj.is_loopback
        except Exception:
            return False
    
    def _is_whitelisted_process(self, process_name: str) -> bool:
        """Verifica si un proceso está en la lista blanca"""
        return process_name.lower() in [p.lower() for p in self.config['system_processes_whitelist']]
    
    def get_recent_data(self, count: Optional[int] = None) -> List[Dict]:
        """Obtiene datos recientes de procesos"""
        if count is None:
            return list(self.process_data)
        else:
            return list(self.process_data)[-count:]
    
    def get_suspicious_processes(self) -> List[Dict]:
        """Obtiene lista de procesos sospechosos activos"""
        suspicious = []
        
        for pid in self.suspicious_processes:
            if pid in self.tracked_processes:
                proc_info = self.tracked_processes[pid].copy()
                proc_info['pid'] = pid
                suspicious.append(proc_info)
        
        return suspicious
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del monitor"""
        stats = self.stats.copy()
        stats.update({
            'active_processes': len(self.tracked_processes),
            'suspicious_processes_active': len(self.suspicious_processes),
            'is_monitoring': self.is_monitoring
        })
        
        if stats['start_time']:
            uptime = (datetime.now() - stats['start_time']).total_seconds()
            stats['uptime_seconds'] = uptime
        
        return stats
    
    def is_active(self) -> bool:
        """Verifica si el monitor está activo"""
        return self.is_monitoring
    
    def kill_suspicious_process(self, pid: int) -> bool:
        """Termina un proceso sospechoso"""
        try:
            if pid in self.suspicious_processes:
                proc = psutil.Process(pid)
                proc.terminate()
                logger.warning(f"[LOCK] Proceso sospechoso terminado: PID {pid}")
                return True
            else:
                logger.warning(f"[WARNING] Proceso {pid} no está marcado como sospechoso")
                return False
                
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"[ERROR] No se pudo terminar proceso {pid}: {e}")
            return False


def test_process_monitor():
    """Función de prueba del monitor de procesos"""
    def on_suspicious_process(data):
        print(f"🚨 Proceso sospechoso: {data['process_info']['name']} (PID: {data['pid']})")
        print(f"   Razón: {data['reason']}")
        print(f"   Comportamientos: {data['behaviors']}")
        print(f"   Risk Score: {data['risk_score']:.2f}")
    
    monitor = ProcessBehaviorMonitor(callback=on_suspicious_process)
    
    try:
        print("[PROC] Iniciando test del monitor de procesos...")
        monitor.start_monitoring()
        
        # Ejecutar por 60 segundos
        for i in range(12):
            time.sleep(5)
            stats = monitor.get_stats()
            print(f"[DATA] [{i*5:2d}s] Procesos: {stats['active_processes']}, Sospechosos: {stats['suspicious_processes_active']}")
        
        # Mostrar procesos sospechosos
        suspicious = monitor.get_suspicious_processes()
        if suspicious:
            print(f"\n🚨 Procesos sospechosos detectados ({len(suspicious)}):")
            for proc in suspicious:
                print(f"   - {proc['name']} (PID: {proc['pid']}) - Risk: {proc.get('risk_score', 0):.2f}")
        else:
            print("\n[OK] No se detectaron procesos sospechosos")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrumpido por usuario")
    
    finally:
        monitor.stop_monitoring()
        print("[OK] Test completado")


if __name__ == "__main__":
    test_process_monitor()