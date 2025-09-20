"""
Detector de Comportamiento de Keyloggers
========================================

Detecta patrones de comportamiento típicos de keyloggers mediante
análisis heurístico y reglas especializadas.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class BehaviorDetector:
    """Detector de comportamiento de keyloggers"""
    
    def __init__(self):
        self.detection_rules = self._initialize_rules()
        self.stats = {
            'analyses_performed': 0,
            'threats_detected': 0,
            'patterns_matched': 0
        }
        
        logger.info("[SEARCH] BehaviorDetector inicializado")
    
    def _initialize_rules(self) -> Dict:
        """Inicializa las reglas de detección"""
        return {
            'process_behavior': {
                'keylogger_process_patterns': [
                    r'.*keylog.*',
                    r'.*spyware.*',
                    r'.*stealer.*',
                    r'.*monitor.*',
                    r'.*capture.*',
                    r'.*recorder.*'
                ],
                'suspicious_command_lines': [
                    r'.*hook.*keyboard.*',
                    r'.*capture.*key.*',
                    r'.*log.*key.*',
                    r'.*GetAsyncKeyState.*',
                    r'.*SetWindowsHookEx.*',
                    r'.*RegisterRawInputDevices.*'
                ],
                'hidden_process_indicators': [
                    'no_window',
                    'background_only',
                    'system_impersonation'
                ]
            },
            'network_behavior': {
                'data_exfiltration_patterns': [
                    'frequent_small_uploads',
                    'encrypted_data_streams',
                    'unusual_protocol_usage',
                    'suspicious_destination_ips'
                ],
                'command_control_patterns': [
                    'periodic_beacons',
                    'encrypted_communications',
                    'non_standard_ports'
                ]
            },
            'file_behavior': {
                'suspicious_file_operations': [
                    'credential_file_access',
                    'temporary_file_creation',
                    'log_file_generation',
                    'encrypted_file_storage'
                ],
                'keylogger_file_patterns': [
                    r'.*\.keylog$',
                    r'.*passwords?\.txt$',
                    r'.*credentials?\.txt$',
                    r'.*capture.*\.log$',
                    r'.*keys?\.dat$'
                ]
            },
            'system_behavior': {
                'registry_modifications': [
                    'startup_entries',
                    'persistence_mechanisms',
                    'security_bypasses'
                ],
                'api_call_patterns': [
                    'keyboard_hook_apis',
                    'screen_capture_apis',
                    'clipboard_access_apis',
                    'process_injection_apis'
                ]
            }
        }
    
    def analyze(self, monitor_name: str, data: List[Dict]) -> List[Dict]:
        """Analiza datos y detecta comportamientos sospechosos"""
        threats = []
        self.stats['analyses_performed'] += 1
        
        try:
            if monitor_name == 'process':
                threats.extend(self._analyze_process_behavior(data))
            elif monitor_name == 'network':
                threats.extend(self._analyze_network_behavior(data))
            elif monitor_name == 'filesystem':
                threats.extend(self._analyze_file_behavior(data))
            
            self.stats['threats_detected'] += len(threats)
            
        except Exception as e:
            logger.error(f"[ERROR] Error en análisis de comportamiento: {e}")
        
        return threats
    
    def _analyze_process_behavior(self, process_data: List[Dict]) -> List[Dict]:
        """Analiza comportamiento de procesos"""
        threats = []
        
        for proc_data in process_data:
            try:
                threat_indicators = []
                risk_score = 0.0
                
                # Verificar patrones de proceso keylogger
                process_name = proc_data.get('process_info', {}).get('name', '').lower()
                cmdline = proc_data.get('process_info', {}).get('cmdline', '').lower()
                
                # Patrones de nombre de proceso
                for pattern in self.detection_rules['process_behavior']['keylogger_process_patterns']:
                    if re.search(pattern, process_name):
                        threat_indicators.append('suspicious_process_name')
                        risk_score += 0.8
                        self.stats['patterns_matched'] += 1
                        break
                
                # Patrones de línea de comandos
                for pattern in self.detection_rules['process_behavior']['suspicious_command_lines']:
                    if re.search(pattern, cmdline):
                        threat_indicators.append('suspicious_command_line')
                        risk_score += 0.9
                        self.stats['patterns_matched'] += 1
                        break
                
                # Comportamientos específicos de keylogger
                behaviors = proc_data.get('behaviors', [])
                
                if 'keylogger_pattern' in behaviors:
                    threat_indicators.append('keylogger_behavior_pattern')
                    risk_score += 1.0
                
                if 'external_network_access' in behaviors:
                    threat_indicators.append('external_communication')
                    risk_score += 0.4
                
                if 'suspicious_file_access' in behaviors:
                    threat_indicators.append('credential_file_access')
                    risk_score += 0.5
                
                if 'potentially_hidden' in behaviors:
                    threat_indicators.append('hidden_process')
                    risk_score += 0.3
                
                # Análisis avanzado de comportamiento
                advanced_analysis = self._advanced_process_analysis(proc_data)
                threat_indicators.extend(advanced_analysis['indicators'])
                risk_score += advanced_analysis['risk_score']
                
                # Crear amenaza si supera el umbral
                if risk_score >= 0.6 and threat_indicators:
                    threat = {
                        'type': 'keylogger_behavior',
                        'severity': 'high' if risk_score > 0.8 else 'medium',
                        'confidence': min(risk_score, 1.0),
                        'source': 'behavior_detector',
                        'indicators': threat_indicators,
                        'details': {
                            'process_pid': proc_data.get('pid'),
                            'process_name': process_name,
                            'command_line': cmdline,
                            'risk_score': risk_score,
                            'behaviors': behaviors
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                    threats.append(threat)
                    
            except Exception as e:
                logger.debug(f"Error analizando proceso: {e}")
        
        return threats
    
    def _advanced_process_analysis(self, proc_data: Dict) -> Dict:
        """Análisis avanzado de comportamiento de proceso"""
        indicators = []
        risk_score = 0.0
        
        try:
            process_info = proc_data.get('process_info', {})
            
            # Análisis de conexiones de red
            network_connections = process_info.get('network_connections', 0)
            external_connections = process_info.get('external_connections', 0)
            
            # Proceso con muchas conexiones externas
            if external_connections > 3:
                indicators.append('high_external_connectivity')
                risk_score += 0.3
            
            # Proceso con conexiones pero sin ventana visible
            if network_connections > 0 and 'potentially_hidden' in proc_data.get('behaviors', []):
                indicators.append('hidden_network_activity')
                risk_score += 0.5
            
            # Análisis de archivos abiertos
            open_files = process_info.get('open_files', [])
            suspicious_file_access = False
            
            for file_path in open_files:
                file_path_lower = file_path.lower()
                
                # Archivos de credenciales o logs
                credential_patterns = ['password', 'credential', 'login', 'auth', 'key', 'token']
                if any(pattern in file_path_lower for pattern in credential_patterns):
                    indicators.append('credential_file_access')
                    risk_score += 0.4
                    suspicious_file_access = True
                    break
                
                # Archivos de log sospechosos
                if '.log' in file_path_lower or '.keylog' in file_path_lower:
                    indicators.append('log_file_creation')
                    risk_score += 0.6
                    suspicious_file_access = True
                    break
            
            # Análisis de uso de memoria y CPU
            memory_percent = process_info.get('memory_percent', 0)
            cpu_percent = process_info.get('cpu_percent', 0)
            
            # Proceso con bajo uso de recursos pero actividad de red (típico de keyloggers)
            if memory_percent < 1.0 and cpu_percent < 5.0 and external_connections > 0:
                indicators.append('low_resource_network_activity')
                risk_score += 0.3
            
            # Proceso con nombre genérico pero comportamiento sospechoso
            process_name = process_info.get('name', '').lower()
            generic_names = ['svchost.exe', 'rundll32.exe', 'explorer.exe', 'system']
            
            if (process_name in generic_names and 
                (suspicious_file_access or external_connections > 1)):
                indicators.append('generic_name_suspicious_behavior')
                risk_score += 0.4
            
        except Exception as e:
            logger.debug(f"Error en análisis avanzado: {e}")
        
        return {
            'indicators': indicators,
            'risk_score': risk_score
        }
    
    def _analyze_network_behavior(self, network_data: List[Dict]) -> List[Dict]:
        """Analiza comportamiento de red"""
        threats = []
        
        # Agrupar datos por proceso/conexión
        connection_groups = {}
        
        for conn_data in network_data:
            try:
                process_name = conn_data.get('process_name', 'unknown')
                remote_ip = conn_data.get('remote_ip', '')
                
                key = f"{process_name}_{remote_ip}"
                if key not in connection_groups:
                    connection_groups[key] = []
                connection_groups[key].append(conn_data)
                
            except Exception as e:
                logger.debug(f"Error agrupando conexiones: {e}")
        
        # Analizar cada grupo de conexiones
        for group_key, connections in connection_groups.items():
            try:
                threat_analysis = self._analyze_connection_group(connections)
                if threat_analysis['is_threat']:
                    threats.append(threat_analysis['threat'])
                    
            except Exception as e:
                logger.debug(f"Error analizando grupo de conexiones: {e}")
        
        return threats
    
    def _analyze_connection_group(self, connections: List[Dict]) -> Dict:
        """Analiza un grupo de conexiones relacionadas"""
        threat_indicators = []
        risk_score = 0.0
        
        try:
            if not connections:
                return {'is_threat': False}
            
            # Información del grupo
            first_conn = connections[0]
            process_name = first_conn.get('process_name', 'unknown')
            remote_ip = first_conn.get('remote_ip', '')
            
            # Análisis de frecuencia
            connection_count = len(connections)
            if connection_count > 10:  # Muchas conexiones
                threat_indicators.append('high_connection_frequency')
                risk_score += 0.3
            
            # Análisis de patrones temporales
            timestamps = [conn.get('timestamp') for conn in connections if conn.get('timestamp')]
            if len(timestamps) > 1:
                # Verificar patrones regulares (posible beacon)
                time_intervals = self._calculate_time_intervals(timestamps)
                if self._is_regular_pattern(time_intervals):
                    threat_indicators.append('regular_beacon_pattern')
                    risk_score += 0.6
            
            # Análisis de puertos
            remote_ports = [conn.get('remote_port') for conn in connections]
            unique_ports = set(remote_ports)
            
            # Uso de múltiples puertos no estándar
            non_standard_ports = [p for p in unique_ports if p and p > 1024 and p not in [80, 443, 8080, 8443]]
            if len(non_standard_ports) > 2:
                threat_indicators.append('multiple_non_standard_ports')
                risk_score += 0.4
            
            # Análisis del proceso
            if process_name != 'unknown':
                # Proceso con nombre sospechoso
                suspicious_names = ['temp', 'tmp', 'cache', 'svc', 'run']
                if any(name in process_name.lower() for name in suspicious_names):
                    threat_indicators.append('suspicious_process_name')
                    risk_score += 0.3
                
                # Proceso no común haciendo conexiones externas
                common_processes = ['chrome.exe', 'firefox.exe', 'edge.exe', 'outlook.exe']
                if process_name.lower() not in common_processes:
                    threat_indicators.append('uncommon_process_network_activity')
                    risk_score += 0.2
            
            # Análisis de IP de destino
            if remote_ip:
                ip_analysis = self._analyze_destination_ip(remote_ip)
                threat_indicators.extend(ip_analysis['indicators'])
                risk_score += ip_analysis['risk_score']
            
            # Determinar si es amenaza
            is_threat = risk_score >= 0.5 and len(threat_indicators) >= 2
            
            threat_data = {
                'is_threat': is_threat
            }
            
            if is_threat:
                threat_data['threat'] = {
                    'type': 'suspicious_network_behavior',
                    'severity': 'high' if risk_score > 0.8 else 'medium',
                    'confidence': min(risk_score, 1.0),
                    'source': 'behavior_detector',
                    'indicators': threat_indicators,
                    'details': {
                        'process_name': process_name,
                        'remote_ip': remote_ip,
                        'connection_count': connection_count,
                        'unique_ports': list(unique_ports),
                        'risk_score': risk_score
                    },
                    'timestamp': datetime.now().isoformat()
                }
            
            return threat_data
            
        except Exception as e:
            logger.debug(f"Error en análisis de grupo de conexiones: {e}")
            return {'is_threat': False}
    
    def _calculate_time_intervals(self, timestamps: List[str]) -> List[float]:
        """Calcula intervalos de tiempo entre conexiones"""
        intervals = []
        
        try:
            # Convertir timestamps a datetime objects
            dt_timestamps = []
            for ts in timestamps:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    dt_timestamps.append(dt)
                except Exception:
                    continue
            
            # Calcular intervalos
            dt_timestamps.sort()
            for i in range(1, len(dt_timestamps)):
                interval = (dt_timestamps[i] - dt_timestamps[i-1]).total_seconds()
                intervals.append(interval)
                
        except Exception as e:
            logger.debug(f"Error calculando intervalos: {e}")
        
        return intervals
    
    def _is_regular_pattern(self, intervals: List[float], tolerance: float = 0.2) -> bool:
        """Detecta si hay un patrón regular en los intervalos"""
        if len(intervals) < 3:
            return False
        
        try:
            # Calcular la desviación estándar de los intervalos
            import statistics
            mean_interval = statistics.mean(intervals)
            stdev_interval = statistics.stdev(intervals)
            
            # Si la desviación estándar es pequeña relativa a la media, es regular
            coefficient_of_variation = stdev_interval / mean_interval if mean_interval > 0 else 1
            
            return coefficient_of_variation < tolerance
            
        except Exception:
            return False
    
    def _analyze_destination_ip(self, ip: str) -> Dict:
        """Analiza la IP de destino"""
        indicators = []
        risk_score = 0.0
        
        try:
            import ipaddress
            ip_obj = ipaddress.ip_address(ip)
            
            # IP privada/local es menos sospechosa
            if ip_obj.is_private or ip_obj.is_loopback:
                risk_score -= 0.2
            else:
                # IP pública requiere más análisis
                indicators.append('external_ip_communication')
                risk_score += 0.2
                
                # IPs en rangos conocidos de hosting/VPS (simplificado)
                # En un sistema real, esto consultaría bases de datos de reputación
                ip_str = str(ip_obj)
                
                # Patrones de IPs sospechosas (ejemplos)
                suspicious_patterns = [
                    ip_str.startswith('185.'),  # Rango común para VPS maliciosos
                    ip_str.startswith('95.'),   # Otro rango común
                    ip_str.startswith('46.'),   # Hosting barato
                ]
                
                if any(suspicious_patterns):
                    indicators.append('suspicious_ip_range')
                    risk_score += 0.3
                    
        except Exception as e:
            logger.debug(f"Error analizando IP {ip}: {e}")
        
        return {
            'indicators': indicators,
            'risk_score': risk_score
        }
    
    def _analyze_file_behavior(self, file_data: List[Dict]) -> List[Dict]:
        """Analiza comportamiento de archivos"""
        threats = []
        
        for file_event in file_data:
            try:
                threat_analysis = self._analyze_file_event(file_event)
                if threat_analysis['is_threat']:
                    threats.append(threat_analysis['threat'])
                    
            except Exception as e:
                logger.debug(f"Error analizando evento de archivo: {e}")
        
        return threats
    
    def _analyze_file_event(self, file_event: Dict) -> Dict:
        """Analiza un evento de archivo individual"""
        threat_indicators = []
        risk_score = 0.0
        
        try:
            file_info = file_event.get('file_info', {})
            file_path = file_info.get('path', '')
            file_name = file_info.get('name', '').lower()
            
            # Verificar patrones de archivos de keylogger
            for pattern in self.detection_rules['file_behavior']['keylogger_file_patterns']:
                if re.search(pattern, file_name):
                    threat_indicators.append('keylogger_file_pattern')
                    risk_score += 0.9
                    self.stats['patterns_matched'] += 1
                    break
            
            # Análisis de ubicación del archivo
            path_lower = file_path.lower()
            
            # Archivos en ubicaciones temporales
            temp_locations = ['temp', 'tmp', 'cache', 'appdata\\local\\temp']
            if any(loc in path_lower for loc in temp_locations):
                threat_indicators.append('temporary_location')
                risk_score += 0.3
            
            # Archivos ocultos con extensiones sospechosas
            if (file_info.get('is_hidden', False) and 
                file_info.get('extension') in ['.exe', '.dll', '.bat', '.vbs']):
                threat_indicators.append('hidden_executable')
                risk_score += 0.7
            
            # Análisis de contenido
            if file_info.get('contains_credentials', False):
                threat_indicators.append('contains_credentials')
                risk_score += 0.8
            
            if file_info.get('has_suspicious_strings', False):
                threat_indicators.append('suspicious_content')
                risk_score += 0.4
            
            # Archivos muy pequeños o vacíos con extensiones ejecutables
            if (file_info.get('size', 0) < 1024 and 
                file_info.get('extension') in ['.exe', '.dll']):
                threat_indicators.append('suspicious_small_executable')
                risk_score += 0.5
            
            # Archivos creados recientemente con patrones sospechosos
            if file_event.get('type') == 'file_created':
                # Archivos de log creados por procesos no del sistema
                if (file_info.get('extension') in ['.log', '.txt'] and
                    any(word in file_name for word in ['key', 'pass', 'cred', 'capture'])):
                    threat_indicators.append('suspicious_log_creation')
                    risk_score += 0.6
            
            # Determinar si es amenaza
            is_threat = risk_score >= 0.5 and len(threat_indicators) >= 1
            
            threat_data = {
                'is_threat': is_threat
            }
            
            if is_threat:
                threat_data['threat'] = {
                    'type': 'suspicious_file_behavior',
                    'severity': 'high' if risk_score > 0.8 else 'medium',
                    'confidence': min(risk_score, 1.0),
                    'source': 'behavior_detector',
                    'indicators': threat_indicators,
                    'details': {
                        'file_path': file_path,
                        'file_name': file_name,
                        'event_type': file_event.get('type'),
                        'file_size': file_info.get('size', 0),
                        'risk_score': risk_score
                    },
                    'timestamp': datetime.now().isoformat()
                }
            
            return threat_data
            
        except Exception as e:
            logger.debug(f"Error en análisis de evento de archivo: {e}")
            return {'is_threat': False}
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del detector"""
        return self.stats.copy()
    
    def update_rules(self, new_rules: Dict):
        """Actualiza las reglas de detección"""
        try:
            self.detection_rules.update(new_rules)
            logger.info("[OK] Reglas de detección actualizadas")
        except Exception as e:
            logger.error(f"[ERROR] Error actualizando reglas: {e}")
    
    def add_custom_pattern(self, category: str, subcategory: str, pattern: str):
        """Añade un patrón personalizado de detección"""
        try:
            if category not in self.detection_rules:
                self.detection_rules[category] = {}
            
            if subcategory not in self.detection_rules[category]:
                self.detection_rules[category][subcategory] = []
            
            self.detection_rules[category][subcategory].append(pattern)
            logger.info(f"➕ Patrón añadido: {category}.{subcategory} -> {pattern}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error añadiendo patrón: {e}")


def test_behavior_detector():
    """Función de prueba del detector de comportamiento"""
    detector = BehaviorDetector()
    
    # Datos de prueba - proceso sospechoso
    test_process_data = [{
        'pid': 1234,
        'process_info': {
            'name': 'keylogger.exe',
            'cmdline': 'keylogger.exe --hook keyboard --capture all',
            'network_connections': 2,
            'external_connections': 1,
            'open_files': [
                'C:\\Users\\user\\passwords.txt',
                'C:\\Temp\\keylog.dat'
            ],
            'memory_percent': 0.5,
            'cpu_percent': 2.0
        },
        'behaviors': ['keylogger_pattern', 'external_network_access', 'suspicious_file_access']
    }]
    
    print("[SEARCH] Testing BehaviorDetector...")
    
    # Test análisis de procesos
    threats = detector.analyze('process', test_process_data)
    print(f"[DATA] Amenazas detectadas en procesos: {len(threats)}")
    
    for threat in threats:
        print(f"   🚨 {threat['type']} - Severidad: {threat['severity']}")
        print(f"      Confianza: {threat['confidence']:.2f}")
        print(f"      Indicadores: {threat['indicators']}")
    
    # Estadísticas
    stats = detector.get_stats()
    print(f"\n[STATS] Estadísticas:")
    print(f"   Análisis realizados: {stats['analyses_performed']}")
    print(f"   Amenazas detectadas: {stats['threats_detected']}")
    print(f"   Patrones coincidentes: {stats['patterns_matched']}")
    
    print("[OK] Test completado")


if __name__ == "__main__":
    test_behavior_detector()