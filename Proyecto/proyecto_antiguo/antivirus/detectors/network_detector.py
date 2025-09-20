"""
Detector de Patrones de Red
===========================

Especializado en detectar patrones de red característicos de keyloggers
y malware que exfiltran datos o se comunican con servidores C&C.
"""

import logging
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import ipaddress
import socket

logger = logging.getLogger(__name__)


class NetworkPatternDetector:
    """Detector especializado en patrones de red maliciosos"""
    
    def __init__(self):
        # Bases de datos de patrones
        self.known_malicious_ips = set()
        self.suspicious_domains = set()
        self.tracked_connections = defaultdict(list)  # IP -> [connection_data]
        self.connection_patterns = defaultdict(dict)  # IP -> pattern_analysis
        
        # Estadísticas
        self.stats = {
            'connections_analyzed': 0,
            'suspicious_patterns_detected': 0,
            'c2_communications_detected': 0,
            'data_exfiltration_detected': 0
        }
        
        # Configuración de detección
        self.config = {
            'min_connections_for_pattern': 3,
            'beacon_interval_tolerance': 0.3,  # 30% de tolerancia
            'suspicious_upload_threshold': 1024,  # bytes
            'c2_pattern_confidence_threshold': 0.7,
            'data_exfiltration_threshold': 0.6,
            'max_tracking_age_hours': 24
        }
        
        # Cargar listas de IPs/dominios conocidos
        self._load_threat_intelligence()
        
        logger.info("[NET] NetworkPatternDetector inicializado")
    
    def _load_threat_intelligence(self):
        """Carga inteligencia de amenazas conocidas"""
        # En un sistema real, esto cargaría desde feeds de threat intelligence
        
        # IPs maliciosas conocidas (ejemplos)
        self.known_malicious_ips.update([
            '185.220.100.240',  # Ejemplo de IP maliciosa
            '195.133.40.71',
            '46.166.139.111'
        ])
        
        # Dominios sospechosos (ejemplos)
        self.suspicious_domains.update([
            'malware-c2.com',
            'keylogger-data.net',
            'steal-info.org'
        ])
        
        logger.info(f"[INFO] Cargadas {len(self.known_malicious_ips)} IPs maliciosas y {len(self.suspicious_domains)} dominios sospechosos")
    
    def analyze(self, monitor_name: str, data: List[Dict]) -> List[Dict]:
        """Analiza datos de red y detecta patrones maliciosos"""
        threats = []
        
        try:
            if monitor_name == 'network':
                # Actualizar tracking de conexiones
                self._update_connection_tracking(data)
                
                # Limpiar datos antiguos
                self._cleanup_old_tracking_data()
                
                # Analizar patrones
                threats.extend(self._detect_c2_communications())
                threats.extend(self._detect_data_exfiltration())
                threats.extend(self._detect_suspicious_protocols())
                threats.extend(self._detect_domain_generation_algorithms())
                
                self.stats['connections_analyzed'] += len(data)
                self.stats['suspicious_patterns_detected'] += len(threats)
                
        except Exception as e:
            logger.error(f"[ERROR] Error en análisis de patrones de red: {e}")
        
        return threats
    
    def _update_connection_tracking(self, connections: List[Dict]):
        """Actualiza el tracking de conexiones por IP"""
        for conn in connections:
            try:
                remote_ip = conn.get('remote_ip') or conn.get('dst_ip')
                if not remote_ip:
                    continue
                
                # Enriquecer datos de conexión
                enriched_conn = self._enrich_connection_data(conn)
                
                # Añadir al tracking
                self.tracked_connections[remote_ip].append(enriched_conn)
                
                # Mantener solo las últimas N conexiones por IP
                if len(self.tracked_connections[remote_ip]) > 100:
                    self.tracked_connections[remote_ip] = self.tracked_connections[remote_ip][-100:]
                
            except Exception as e:
                logger.debug(f"Error actualizando tracking: {e}")
    
    def _enrich_connection_data(self, conn: Dict) -> Dict:
        """Enriquece datos de conexión con información adicional"""
        enriched = conn.copy()
        
        try:
            # Añadir timestamp si no existe
            if 'timestamp' not in enriched:
                enriched['timestamp'] = datetime.now().isoformat()
            
            # Análisis de puertos
            remote_port = conn.get('remote_port') or conn.get('dst_port', 0)
            enriched['port_category'] = self._categorize_port(remote_port)
            
            # Análisis de IP
            remote_ip = conn.get('remote_ip') or conn.get('dst_ip', '')
            if remote_ip:
                enriched['ip_analysis'] = self._analyze_ip_address(remote_ip)
            
            # Análisis de proceso
            process_name = conn.get('process_name', '')
            enriched['process_category'] = self._categorize_process(process_name)
            
            # Estimación de datos transferidos
            packet_size = conn.get('packet_size', 0)
            if packet_size == 0:
                # Estimación basada en tipo de conexión
                enriched['estimated_bytes'] = self._estimate_data_transfer(conn)
            else:
                enriched['estimated_bytes'] = packet_size
                
        except Exception as e:
            logger.debug(f"Error enriqueciendo conexión: {e}")
        
        return enriched
    
    def _categorize_port(self, port: int) -> str:
        """Categoriza un puerto según su uso común"""
        if port == 0:
            return 'unknown'
        elif port < 1024:
            return 'system'
        elif port in [80, 443, 8080, 8443]:
            return 'web'
        elif port in [21, 22, 23, 25, 53, 110, 143, 993, 995]:
            return 'standard'
        elif port in [1337, 31337, 4444, 5555, 6666, 7777]:
            return 'suspicious'
        else:
            return 'dynamic'
    
    def _analyze_ip_address(self, ip: str) -> Dict:
        """Analiza una dirección IP"""
        analysis = {
            'is_private': False,
            'is_malicious': False,
            'geolocation': 'unknown',
            'reputation_score': 0.5  # Neutral por defecto
        }
        
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Verificar si es privada
            analysis['is_private'] = ip_obj.is_private or ip_obj.is_loopback
            
            # Verificar listas de IPs maliciosas
            analysis['is_malicious'] = ip in self.known_malicious_ips
            
            # Análisis de reputación simplificado
            if analysis['is_malicious']:
                analysis['reputation_score'] = 0.9
            elif analysis['is_private']:
                analysis['reputation_score'] = 0.1
            else:
                # IP pública - evaluar según rangos
                analysis['reputation_score'] = self._calculate_ip_reputation(ip)
            
            # Geolocalización simplificada (en sistema real usaría GeoIP)
            analysis['geolocation'] = self._simple_geolocation(ip)
            
        except Exception as e:
            logger.debug(f"Error analizando IP {ip}: {e}")
        
        return analysis
    
    def _calculate_ip_reputation(self, ip: str) -> float:
        """Calcula un score de reputación para una IP"""
        # Análisis simplificado basado en rangos conocidos
        reputation = 0.5  # Neutral
        
        try:
            # Rangos de hosting conocidos por alojar malware (ejemplos)
            if ip.startswith('185.'):
                reputation = 0.7  # Más sospechoso
            elif ip.startswith('46.'):
                reputation = 0.6
            elif ip.startswith('95.'):
                reputation = 0.6
            elif ip.startswith('8.8.') or ip.startswith('1.1.'):
                reputation = 0.1  # DNS públicos, menos sospechoso
            
        except Exception:
            pass
        
        return reputation
    
    def _simple_geolocation(self, ip: str) -> str:
        """Geolocalización simplificada"""
        # En un sistema real, usaría una base de datos GeoIP
        try:
            # Intentar resolución inversa
            hostname = socket.gethostbyaddr(ip)[0]
            
            # Extraer país del hostname (muy simplificado)
            if '.ru' in hostname or '.russian' in hostname:
                return 'RU'
            elif '.cn' in hostname or '.china' in hostname:
                return 'CN'
            elif '.de' in hostname or '.german' in hostname:
                return 'DE'
            else:
                return 'unknown'
                
        except Exception:
            return 'unknown'
    
    def _categorize_process(self, process_name: str) -> str:
        """Categoriza un proceso según su tipo"""
        if not process_name:
            return 'unknown'
        
        name_lower = process_name.lower()
        
        if name_lower in ['chrome.exe', 'firefox.exe', 'edge.exe', 'safari.exe']:
            return 'browser'
        elif name_lower in ['outlook.exe', 'thunderbird.exe']:
            return 'email'
        elif name_lower in ['svchost.exe', 'system', 'winlogon.exe']:
            return 'system'
        elif any(word in name_lower for word in ['update', 'antivirus', 'security']):
            return 'security'
        elif any(word in name_lower for word in ['game', 'steam', 'discord']):
            return 'gaming'
        else:
            return 'application'
    
    def _estimate_data_transfer(self, conn: Dict) -> int:
        """Estima la cantidad de datos transferidos"""
        # Estimación muy simplificada
        port_category = conn.get('port_category', 'unknown')
        
        if port_category == 'web':
            return 1500  # Tamaño típico de paquete web
        elif port_category == 'system':
            return 64   # Paquetes pequeños del sistema
        else:
            return 512  # Valor por defecto
    
    def _cleanup_old_tracking_data(self):
        """Limpia datos de tracking antiguos"""
        cutoff_time = datetime.now() - timedelta(hours=self.config['max_tracking_age_hours'])
        
        for ip in list(self.tracked_connections.keys()):
            try:
                # Filtrar conexiones recientes
                recent_connections = []
                for conn in self.tracked_connections[ip]:
                    try:
                        conn_time = datetime.fromisoformat(conn['timestamp'].replace('Z', '+00:00'))
                        if conn_time > cutoff_time:
                            recent_connections.append(conn)
                    except Exception:
                        continue
                
                if recent_connections:
                    self.tracked_connections[ip] = recent_connections
                else:
                    del self.tracked_connections[ip]
                    
            except Exception as e:
                logger.debug(f"Error limpiando datos para {ip}: {e}")
    
    def _detect_c2_communications(self) -> List[Dict]:
        """Detecta comunicaciones con servidores Command & Control"""
        threats = []
        
        for ip, connections in self.tracked_connections.items():
            try:
                if len(connections) < self.config['min_connections_for_pattern']:
                    continue
                
                c2_analysis = self._analyze_c2_pattern(ip, connections)
                
                if c2_analysis['is_c2'] and c2_analysis['confidence'] >= self.config['c2_pattern_confidence_threshold']:
                    threat = {
                        'type': 'c2_communication',
                        'severity': 'high',
                        'confidence': c2_analysis['confidence'],
                        'source': 'network_pattern_detector',
                        'details': {
                            'remote_ip': ip,
                            'connection_count': len(connections),
                            'pattern_type': c2_analysis['pattern_type'],
                            'beacon_interval': c2_analysis.get('beacon_interval'),
                            'regularity_score': c2_analysis.get('regularity_score'),
                            'indicators': c2_analysis['indicators']
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                    threats.append(threat)
                    self.stats['c2_communications_detected'] += 1
                    
            except Exception as e:
                logger.debug(f"Error detectando C2 para {ip}: {e}")
        
        return threats
    
    def _analyze_c2_pattern(self, ip: str, connections: List[Dict]) -> Dict:
        """Analiza patrones típicos de C2"""
        analysis = {
            'is_c2': False,
            'confidence': 0.0,
            'pattern_type': 'none',
            'indicators': []
        }
        
        try:
            # Análisis temporal - buscar patrones de beacon
            timestamps = self._extract_timestamps(connections)
            
            if len(timestamps) >= 3:
                intervals = self._calculate_intervals(timestamps)
                regularity = self._calculate_regularity(intervals)
                
                analysis['regularity_score'] = regularity
                
                # Patrón de beacon regular
                if regularity > 0.7:  # 70% de regularidad
                    analysis['indicators'].append('regular_beacon_pattern')
                    analysis['confidence'] += 0.6
                    analysis['pattern_type'] = 'beacon'
                    
                    # Calcular intervalo promedio
                    if intervals:
                        avg_interval = sum(intervals) / len(intervals)
                        analysis['beacon_interval'] = avg_interval
                        
                        # Intervalos típicos de C2
                        if 30 <= avg_interval <= 3600:  # Entre 30 segundos y 1 hora
                            analysis['indicators'].append('c2_typical_interval')
                            analysis['confidence'] += 0.3
            
            # Análisis de IP de destino
            first_conn = connections[0]
            ip_analysis = first_conn.get('ip_analysis', {})
            
            if ip_analysis.get('is_malicious'):
                analysis['indicators'].append('known_malicious_ip')
                analysis['confidence'] += 0.9
            
            if ip_analysis.get('reputation_score', 0.5) > 0.7:
                analysis['indicators'].append('high_risk_ip')
                analysis['confidence'] += 0.4
            
            # Análisis de puertos
            ports = [conn.get('remote_port', 0) for conn in connections]
            unique_ports = set(ports)
            
            # Uso consistente de puerto no estándar
            if len(unique_ports) == 1 and list(unique_ports)[0] > 1024:
                port = list(unique_ports)[0]
                if connections[0].get('port_category') == 'suspicious':
                    analysis['indicators'].append('suspicious_port_usage')
                    analysis['confidence'] += 0.5
                elif port not in [80, 443, 8080, 8443]:
                    analysis['indicators'].append('non_standard_port_consistency')
                    analysis['confidence'] += 0.2
            
            # Análisis de proceso
            processes = [conn.get('process_name', '') for conn in connections]
            unique_processes = set(processes)
            
            # Proceso único (no browser) haciendo conexiones regulares
            if len(unique_processes) == 1:
                process = list(unique_processes)[0]
                if process and connections[0].get('process_category') not in ['browser', 'email', 'system']:
                    analysis['indicators'].append('non_browser_regular_connections')
                    analysis['confidence'] += 0.3
            
            # Análisis de tamaño de datos
            data_sizes = [conn.get('estimated_bytes', 0) for conn in connections]
            
            # Transferencias pequeñas y consistentes (típico de C2)
            if data_sizes and all(size < 1024 for size in data_sizes):
                avg_size = sum(data_sizes) / len(data_sizes)
                size_variance = self._calculate_variance(data_sizes)
                
                if size_variance < 100:  # Tamaños muy consistentes
                    analysis['indicators'].append('consistent_small_transfers')
                    analysis['confidence'] += 0.3
            
            # Determinar si es C2
            analysis['is_c2'] = analysis['confidence'] >= 0.5 and len(analysis['indicators']) >= 2
            
            # Normalizar confianza
            analysis['confidence'] = min(analysis['confidence'], 1.0)
            
        except Exception as e:
            logger.debug(f"Error en análisis C2: {e}")
        
        return analysis
    
    def _detect_data_exfiltration(self) -> List[Dict]:
        """Detecta patrones de exfiltración de datos"""
        threats = []
        
        for ip, connections in self.tracked_connections.items():
            try:
                if len(connections) < 2:
                    continue
                
                exfil_analysis = self._analyze_exfiltration_pattern(ip, connections)
                
                if exfil_analysis['is_exfiltration'] and exfil_analysis['confidence'] >= self.config['data_exfiltration_threshold']:
                    threat = {
                        'type': 'data_exfiltration',
                        'severity': 'high',
                        'confidence': exfil_analysis['confidence'],
                        'source': 'network_pattern_detector',
                        'details': {
                            'remote_ip': ip,
                            'total_data_estimated': exfil_analysis.get('total_data'),
                            'upload_sessions': exfil_analysis.get('upload_sessions'),
                            'exfiltration_type': exfil_analysis.get('exfiltration_type'),
                            'indicators': exfil_analysis['indicators']
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                    threats.append(threat)
                    self.stats['data_exfiltration_detected'] += 1
                    
            except Exception as e:
                logger.debug(f"Error detectando exfiltración para {ip}: {e}")
        
        return threats
    
    def _analyze_exfiltration_pattern(self, ip: str, connections: List[Dict]) -> Dict:
        """Analiza patrones de exfiltración de datos"""
        analysis = {
            'is_exfiltration': False,
            'confidence': 0.0,
            'indicators': []
        }
        
        try:
            # Calcular total de datos transferidos
            total_data = sum(conn.get('estimated_bytes', 0) for conn in connections)
            analysis['total_data'] = total_data
            
            # Detectar sesiones de subida (uploads)
            upload_sessions = self._detect_upload_sessions(connections)
            analysis['upload_sessions'] = len(upload_sessions)
            
            # Múltiples sesiones de subida
            if len(upload_sessions) > 1:
                analysis['indicators'].append('multiple_upload_sessions')
                analysis['confidence'] += 0.4
            
            # Gran cantidad de datos transferidos
            if total_data > 10 * 1024 * 1024:  # > 10MB
                analysis['indicators'].append('large_data_transfer')
                analysis['confidence'] += 0.5
                analysis['exfiltration_type'] = 'bulk'
            elif total_data > 1024 * 1024:  # > 1MB
                analysis['indicators'].append('moderate_data_transfer')
                analysis['confidence'] += 0.3
                analysis['exfiltration_type'] = 'gradual'
            
            # Análisis temporal de subidas
            if upload_sessions:
                session_intervals = self._analyze_upload_timing(upload_sessions)
                
                # Subidas en intervalos regulares (datos robados gradualmente)
                if session_intervals.get('is_regular', False):
                    analysis['indicators'].append('scheduled_exfiltration')
                    analysis['confidence'] += 0.4
                
                # Subidas fuera de horario laboral
                if session_intervals.get('off_hours_activity', False):
                    analysis['indicators'].append('off_hours_exfiltration')
                    analysis['confidence'] += 0.3
            
            # Análisis del proceso fuente
            processes = [conn.get('process_name', '') for conn in connections]
            unique_processes = set(p for p in processes if p)
            
            if unique_processes:
                for process in unique_processes:
                    process_category = connections[0].get('process_category', 'unknown')
                    
                    # Procesos no autorizados para grandes transferencias
                    if (process_category not in ['browser', 'email', 'system'] and 
                        total_data > 1024 * 1024):
                        analysis['indicators'].append('unauthorized_process_large_transfer')
                        analysis['confidence'] += 0.6
            
            # Análisis de destino
            first_conn = connections[0]
            ip_analysis = first_conn.get('ip_analysis', {})
            
            # Exfiltración a IP sospechosa
            if ip_analysis.get('reputation_score', 0.5) > 0.6:
                analysis['indicators'].append('exfiltration_to_suspicious_ip')
                analysis['confidence'] += 0.5
            
            # Exfiltración a país de alto riesgo
            geolocation = ip_analysis.get('geolocation', 'unknown')
            high_risk_countries = ['RU', 'CN', 'KP', 'IR']
            if geolocation in high_risk_countries:
                analysis['indicators'].append('exfiltration_to_high_risk_country')
                analysis['confidence'] += 0.4
            
            # Determinar si es exfiltración
            analysis['is_exfiltration'] = (
                analysis['confidence'] >= 0.4 and 
                len(analysis['indicators']) >= 2 and
                total_data > self.config['suspicious_upload_threshold']
            )
            
            # Normalizar confianza
            analysis['confidence'] = min(analysis['confidence'], 1.0)
            
        except Exception as e:
            logger.debug(f"Error en análisis de exfiltración: {e}")
        
        return analysis
    
    def _detect_upload_sessions(self, connections: List[Dict]) -> List[List[Dict]]:
        """Detecta sesiones de subida de datos"""
        # Simplificado: agrupar conexiones cercanas en tiempo como sesiones
        sessions = []
        current_session = []
        
        # Ordenar por timestamp
        sorted_connections = sorted(connections, key=lambda x: x.get('timestamp', ''))
        
        for conn in sorted_connections:
            try:
                # Si el tamaño estimado sugiere subida (simplificado)
                estimated_bytes = conn.get('estimated_bytes', 0)
                
                if estimated_bytes > self.config['suspicious_upload_threshold']:
                    if not current_session:
                        current_session = [conn]
                    else:
                        # Verificar si está cerca en tiempo de la última conexión
                        last_conn = current_session[-1]
                        time_diff = self._time_difference(last_conn['timestamp'], conn['timestamp'])
                        
                        if time_diff < 300:  # Menos de 5 minutos
                            current_session.append(conn)
                        else:
                            # Nueva sesión
                            if current_session:
                                sessions.append(current_session)
                            current_session = [conn]
            except Exception:
                continue
        
        if current_session:
            sessions.append(current_session)
        
        return sessions
    
    def _analyze_upload_timing(self, sessions: List[List[Dict]]) -> Dict:
        """Analiza el timing de las sesiones de subida"""
        timing_analysis = {
            'is_regular': False,
            'off_hours_activity': False
        }
        
        try:
            if len(sessions) < 2:
                return timing_analysis
            
            # Extraer timestamps de inicio de cada sesión
            session_times = []
            for session in sessions:
                if session:
                    timestamp_str = session[0]['timestamp']
                    try:
                        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        session_times.append(dt)
                    except Exception:
                        continue
            
            if len(session_times) < 2:
                return timing_analysis
            
            # Analizar regularidad
            intervals = []
            for i in range(1, len(session_times)):
                interval = (session_times[i] - session_times[i-1]).total_seconds()
                intervals.append(interval)
            
            if intervals:
                regularity = self._calculate_regularity(intervals)
                timing_analysis['is_regular'] = regularity > 0.6
            
            # Verificar actividad fuera de horario
            off_hours_count = 0
            for dt in session_times:
                # Considerar fuera de horario: 22:00 - 06:00 o fines de semana
                if dt.hour >= 22 or dt.hour <= 6 or dt.weekday() >= 5:
                    off_hours_count += 1
            
            timing_analysis['off_hours_activity'] = off_hours_count > len(session_times) * 0.5
            
        except Exception as e:
            logger.debug(f"Error analizando timing: {e}")
        
        return timing_analysis
    
    def _detect_suspicious_protocols(self) -> List[Dict]:
        """Detecta uso de protocolos sospechosos"""
        threats = []
        
        # Análisis simplificado basado en puertos
        port_usage = defaultdict(int)
        process_port_map = defaultdict(set)
        
        for ip, connections in self.tracked_connections.items():
            for conn in connections:
                try:
                    port = conn.get('remote_port', 0)
                    process = conn.get('process_name', 'unknown')
                    
                    port_usage[port] += 1
                    process_port_map[process].add(port)
                    
                except Exception:
                    continue
        
        # Detectar uso inusual de puertos
        for process, ports in process_port_map.items():
            try:
                if len(ports) > 5 and process not in ['chrome.exe', 'firefox.exe', 'svchost.exe']:
                    # Proceso usando muchos puertos diferentes
                    threat = {
                        'type': 'suspicious_protocol_usage',
                        'severity': 'medium',
                        'confidence': 0.6,
                        'source': 'network_pattern_detector',
                        'details': {
                            'process_name': process,
                            'ports_used': list(ports),
                            'port_count': len(ports),
                            'description': 'Process using unusually many different ports'
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                    threats.append(threat)
                    
            except Exception as e:
                logger.debug(f"Error analizando protocolos para {process}: {e}")
        
        return threats
    
    def _detect_domain_generation_algorithms(self) -> List[Dict]:
        """Detecta uso de algoritmos de generación de dominios (DGA)"""
        threats = []
        
        # Análisis simplificado: buscar patrones en hostnames resueltos
        suspicious_hostnames = []
        
        for ip, connections in self.tracked_connections.items():
            try:
                # Intentar resolución inversa para detectar dominios DGA
                hostname = self._resolve_hostname(ip)
                
                if hostname and self._is_dga_domain(hostname):
                    suspicious_hostnames.append((ip, hostname))
                    
            except Exception:
                continue
        
        if suspicious_hostnames:
            threat = {
                'type': 'dga_domain_usage',
                'severity': 'high',
                'confidence': 0.8,
                'source': 'network_pattern_detector',
                'details': {
                    'suspicious_domains': suspicious_hostnames,
                    'domain_count': len(suspicious_hostnames),
                    'description': 'Potential Domain Generation Algorithm usage detected'
                },
                'timestamp': datetime.now().isoformat()
            }
            threats.append(threat)
        
        return threats
    
    def _resolve_hostname(self, ip: str) -> Optional[str]:
        """Resuelve hostname para una IP"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return None
    
    def _is_dga_domain(self, domain: str) -> bool:
        """Detecta si un dominio parece generado por DGA"""
        try:
            # Heurísticas simples para DGA
            parts = domain.split('.')
            if len(parts) < 2:
                return False
            
            domain_name = parts[0]
            
            # Dominio muy largo o muy corto
            if len(domain_name) > 20 or len(domain_name) < 3:
                return True
            
            # Alto ratio de consonantes
            vowels = 'aeiou'
            consonant_count = sum(1 for c in domain_name.lower() if c.isalpha() and c not in vowels)
            vowel_count = sum(1 for c in domain_name.lower() if c in vowels)
            
            if vowel_count > 0 and consonant_count / vowel_count > 3:
                return True
            
            # Contiene números (común en DGA)
            if any(c.isdigit() for c in domain_name):
                return True
            
            # Patrones de repetición
            if len(set(domain_name)) < len(domain_name) * 0.6:
                return True
                
        except Exception:
            pass
        
        return False
    
    # Métodos de utilidad
    def _extract_timestamps(self, connections: List[Dict]) -> List[datetime]:
        """Extrae timestamps válidos de las conexiones"""
        timestamps = []
        
        for conn in connections:
            try:
                timestamp_str = conn.get('timestamp', '')
                if timestamp_str:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    timestamps.append(dt)
            except Exception:
                continue
        
        return sorted(timestamps)
    
    def _calculate_intervals(self, timestamps: List[datetime]) -> List[float]:
        """Calcula intervalos entre timestamps"""
        intervals = []
        
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        return intervals
    
    def _calculate_regularity(self, intervals: List[float]) -> float:
        """Calcula la regularidad de una serie de intervalos"""
        if len(intervals) < 2:
            return 0.0
        
        try:
            import statistics
            mean_interval = statistics.mean(intervals)
            stdev_interval = statistics.stdev(intervals)
            
            if mean_interval == 0:
                return 0.0
            
            # Coeficiente de variación inverso (menor variación = mayor regularidad)
            cv = stdev_interval / mean_interval
            regularity = max(0.0, 1.0 - cv)
            
            return regularity
            
        except Exception:
            return 0.0
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calcula la varianza de una lista de valores"""
        if len(values) < 2:
            return 0.0
        
        try:
            import statistics
            return statistics.variance(values)
        except Exception:
            return 0.0
    
    def _time_difference(self, timestamp1: str, timestamp2: str) -> float:
        """Calcula diferencia en segundos entre dos timestamps"""
        try:
            dt1 = datetime.fromisoformat(timestamp1.replace('Z', '+00:00'))
            dt2 = datetime.fromisoformat(timestamp2.replace('Z', '+00:00'))
            return abs((dt2 - dt1).total_seconds())
        except Exception:
            return float('inf')
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del detector"""
        stats = self.stats.copy()
        stats.update({
            'tracked_ips': len(self.tracked_connections),
            'known_malicious_ips': len(self.known_malicious_ips),
            'suspicious_domains': len(self.suspicious_domains)
        })
        return stats
    
    def add_malicious_ip(self, ip: str):
        """Añade una IP a la lista de IPs maliciosas"""
        self.known_malicious_ips.add(ip)
        logger.info(f"➕ IP maliciosa añadida: {ip}")
    
    def add_suspicious_domain(self, domain: str):
        """Añade un dominio a la lista de dominios sospechosos"""
        self.suspicious_domains.add(domain)
        logger.info(f"➕ Dominio sospechoso añadido: {domain}")


def test_network_pattern_detector():
    """Función de prueba del detector de patrones de red"""
    detector = NetworkPatternDetector()
    
    # Datos de prueba - patrón C2
    test_network_data = []
    base_time = datetime.now()
    
    # Simular beacon regular cada 60 segundos
    for i in range(5):
        conn_data = {
            'remote_ip': '185.220.100.240',  # IP maliciosa de ejemplo
            'remote_port': 8080,
            'process_name': 'malware.exe',
            'timestamp': (base_time + timedelta(seconds=i*60)).isoformat(),
            'estimated_bytes': 256
        }
        test_network_data.append(conn_data)
    
    print("[NET] Testing NetworkPatternDetector...")
    
    # Test análisis de patrones
    threats = detector.analyze('network', test_network_data)
    print(f"[DATA] Amenazas detectadas: {len(threats)}")
    
    for threat in threats:
        print(f"   🚨 {threat['type']} - Severidad: {threat['severity']}")
        print(f"      Confianza: {threat['confidence']:.2f}")
        print(f"      Detalles: {threat['details']}")
    
    # Estadísticas
    stats = detector.get_stats()
    print(f"\n[STATS] Estadísticas:")
    print(f"   Conexiones analizadas: {stats['connections_analyzed']}")
    print(f"   Patrones sospechosos: {stats['suspicious_patterns_detected']}")
    print(f"   Comunicaciones C2: {stats['c2_communications_detected']}")
    print(f"   IPs rastreadas: {stats['tracked_ips']}")
    
    print("[OK] Test completado")


if __name__ == "__main__":
    test_network_pattern_detector()