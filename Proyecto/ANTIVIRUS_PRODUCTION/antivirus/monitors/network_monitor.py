"""
Monitor de Tráfico de Red
========================

Monitorea el tráfico de red en tiempo real para detectar patrones
sospechosos que puedan indicar actividad de keyloggers.
"""

import logging
import threading
import time
import socket
import psutil
from datetime import datetime
from typing import Dict, List, Callable, Optional
from collections import deque

logger = logging.getLogger(__name__)


class NetworkTrafficMonitor:
    """Monitor de tráfico de red en tiempo real"""
    
    def __init__(self, callback: Optional[Callable] = None, buffer_size: int = 1000):
        self.callback = callback
        self.buffer_size = buffer_size
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Buffer circular para datos recientes
        self.network_data = deque(maxlen=buffer_size)
        
        # Estadísticas
        self.stats = {
            'packets_captured': 0,
            'suspicious_connections': 0,
            'start_time': None,
            'last_activity': None
        }
        
        # Configuración de monitoreo
        self.config = {
            'monitor_interval': 1.0,  # segundos
            'capture_outbound': True,
            'capture_inbound': True,
            'suspicious_ports': [21, 22, 23, 25, 53, 80, 443, 993, 995],  # Puertos comunes para exfiltración
            'monitor_processes': True
        }
        
        logger.info("[NET] NetworkTrafficMonitor inicializado")
    
    def start_monitoring(self):
        """Inicia el monitoreo de red"""
        if self.is_monitoring:
            logger.warning("[WARNING] El monitor de red ya está activo")
            return
        
        self.is_monitoring = True
        self.stats['start_time'] = datetime.now()
        
        # Iniciar hilo de monitoreo
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            name="NetworkMonitor",
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info("[SYNC] Monitor de red iniciado")
    
    def stop_monitoring(self):
        """Detiene el monitoreo de red"""
        if not self.is_monitoring:
            logger.warning("[WARNING] El monitor de red no está activo")
            return
        
        self.is_monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        
        logger.info("[STOP] Monitor de red detenido")
    
    def _monitoring_loop(self):
        """Bucle principal de monitoreo"""
        logger.info("[SEARCH] Iniciando bucle de monitoreo de red...")
        
        while self.is_monitoring:
            try:
                # Capturar datos de conexiones activas
                connections_data = self._capture_network_connections()
                
                # Procesar cada conexión
                for conn_data in connections_data:
                    self._process_connection(conn_data)
                
                # Pausa entre capturas
                time.sleep(self.config['monitor_interval'])
                
            except Exception as e:
                logger.error(f"[ERROR] Error en bucle de monitoreo: {e}")
                time.sleep(5)  # Pausa más larga en caso de error
    
    def _capture_network_connections(self) -> List[Dict]:
        """Captura las conexiones de red activas"""
        connections_data = []
        
        try:
            # Obtener conexiones usando psutil
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                try:
                    # Filtrar conexiones válidas
                    if conn.status == psutil.CONN_ESTABLISHED:
                        conn_data = self._extract_connection_info(conn)
                        if conn_data:
                            connections_data.append(conn_data)
                            
                except Exception as e:
                    logger.debug(f"Error procesando conexión: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"[ERROR] Error capturando conexiones: {e}")
        
        return connections_data
    
    def _extract_connection_info(self, conn) -> Optional[Dict]:
        """Extrae información relevante de una conexión"""
        try:
            # Información básica de la conexión
            conn_info = {
                'timestamp': datetime.now().isoformat(),
                'pid': conn.pid,
                'family': conn.family.name if conn.family else 'unknown',
                'type': conn.type.name if conn.type else 'unknown',
                'status': conn.status
            }
            
            # Información de direcciones local y remota
            if conn.laddr:
                conn_info.update({
                    'local_ip': conn.laddr.ip,
                    'local_port': conn.laddr.port,
                    'src_ip': conn.laddr.ip,
                    'src_port': conn.laddr.port
                })
            
            if conn.raddr:
                conn_info.update({
                    'remote_ip': conn.raddr.ip,
                    'remote_port': conn.raddr.port,
                    'dst_ip': conn.raddr.ip,
                    'dst_port': conn.raddr.port
                })
            
            # Información del proceso asociado
            if conn.pid:
                try:
                    process = psutil.Process(conn.pid)
                    conn_info.update({
                        'process_name': process.name(),
                        'process_exe': process.exe(),
                        'process_cmdline': ' '.join(process.cmdline()),
                        'process_create_time': process.create_time()
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    conn_info.update({
                        'process_name': 'unknown',
                        'process_exe': 'unknown',
                        'process_cmdline': 'unknown'
                    })
            
            # Calcular características adicionales
            conn_info.update(self._calculate_connection_features(conn_info))
            
            return conn_info
            
        except Exception as e:
            logger.debug(f"Error extrayendo info de conexión: {e}")
            return None
    
    def _calculate_connection_features(self, conn_info: Dict) -> Dict:
        """Calcula características adicionales para la conexión"""
        features = {}
        
        try:
            # Características de puertos
            local_port = conn_info.get('local_port', 0)
            remote_port = conn_info.get('remote_port', 0)
            
            features.update({
                'is_suspicious_local_port': local_port in self.config['suspicious_ports'],
                'is_suspicious_remote_port': remote_port in self.config['suspicious_ports'],
                'is_high_port': remote_port > 1024,
                'port_difference': abs(local_port - remote_port) if local_port and remote_port else 0
            })
            
            # Características de direcciones IP
            remote_ip = conn_info.get('remote_ip', '')
            if remote_ip:
                features.update({
                    'is_local_network': self._is_local_network(remote_ip),
                    'is_private_ip': self._is_private_ip(remote_ip),
                    'ip_reputation_risk': self._check_ip_reputation(remote_ip)
                })
            
            # Características del proceso
            process_name = conn_info.get('process_name', '').lower()
            features.update({
                'is_system_process': process_name in ['system', 'svchost.exe', 'explorer.exe'],
                'is_browser_process': any(browser in process_name for browser in 
                                        ['chrome', 'firefox', 'edge', 'safari', 'opera']),
                'is_suspicious_process_name': any(suspicious in process_name for suspicious in 
                                                ['keylog', 'capture', 'monitor', 'spy', 'hack'])
            })
            
            # Estimación de tamaño de paquete (simplificado)
            features.update({
                'packet_size': 1500,  # MTU estándar Ethernet
                'direction': 'outbound' if conn_info.get('dst_ip') else 'inbound'
            })
            
        except Exception as e:
            logger.debug(f"Error calculando características: {e}")
        
        return features
    
    def _is_local_network(self, ip: str) -> bool:
        """Verifica si una IP pertenece a la red local"""
        try:
            import ipaddress
            ip_obj = ipaddress.ip_address(ip)
            
            local_networks = [
                ipaddress.ip_network('192.168.0.0/16'),
                ipaddress.ip_network('10.0.0.0/8'),
                ipaddress.ip_network('172.16.0.0/12'),
                ipaddress.ip_network('127.0.0.0/8')
            ]
            
            return any(ip_obj in network for network in local_networks)
            
        except Exception:
            return False
    
    def _is_private_ip(self, ip: str) -> bool:
        """Verifica si una IP es privada"""
        try:
            import ipaddress
            return ipaddress.ip_address(ip).is_private
        except Exception:
            return False
    
    def _check_ip_reputation(self, ip: str) -> float:
        """Verifica la reputación de una IP (simplificado)"""
        # En un sistema real, esto consultaría bases de datos de reputación
        # Por ahora, retorna un valor basado en heurísticas simples
        
        if self._is_private_ip(ip):
            return 0.1  # IPs privadas son generalmente seguras
        
        # IPs públicas tienen riesgo medio por defecto
        return 0.5
    
    def _process_connection(self, conn_data: Dict):
        """Procesa una conexión individual"""
        try:
            # Añadir al buffer
            self.network_data.append(conn_data)
            self.stats['packets_captured'] += 1
            self.stats['last_activity'] = datetime.now()
            
            # Verificar si es sospechosa
            if self._is_suspicious_connection(conn_data):
                self.stats['suspicious_connections'] += 1
                logger.warning(f"[ALERT] Conexión sospechosa detectada: {conn_data.get('remote_ip')}:{conn_data.get('remote_port')}")
                
                # Llamar callback si existe
                if self.callback:
                    self.callback(conn_data)
            
        except Exception as e:
            logger.error(f"[ERROR] Error procesando conexión: {e}")
    
    def _is_suspicious_connection(self, conn_data: Dict) -> bool:
        """Determina si una conexión es sospechosa"""
        suspicious_indicators = 0
        
        # Verificar puerto sospechoso
        if conn_data.get('is_suspicious_remote_port', False):
            suspicious_indicators += 1
        
        # Verificar proceso sospechoso
        if conn_data.get('is_suspicious_process_name', False):
            suspicious_indicators += 3  # Peso mayor
        
        # Verificar IP externa no común
        if not conn_data.get('is_local_network', True) and not conn_data.get('is_browser_process', False):
            suspicious_indicators += 1
        
        # Conexiones desde procesos no identificados
        if conn_data.get('process_name') == 'unknown':
            suspicious_indicators += 1
        
        # Umbral de sospecha
        return suspicious_indicators >= 2
    
    def get_recent_data(self, count: Optional[int] = None) -> List[Dict]:
        """Obtiene datos recientes capturados"""
        if count is None:
            return list(self.network_data)
        else:
            return list(self.network_data)[-count:]
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del monitor"""
        stats = self.stats.copy()
        if stats['start_time']:
            uptime = (datetime.now() - stats['start_time']).total_seconds()
            stats['uptime_seconds'] = uptime
            stats['packets_per_second'] = stats['packets_captured'] / max(uptime, 1)
        
        return stats
    
    def is_active(self) -> bool:
        """Verifica si el monitor está activo"""
        return self.is_monitoring
    
    def clear_data(self):
        """Limpia el buffer de datos"""
        self.network_data.clear()
        logger.info("[CLEAN] Buffer de datos de red limpiado")
    
    def set_config(self, config: Dict):
        """Actualiza la configuración del monitor"""
        self.config.update(config)
        logger.info(f"[PROC] Configuración actualizada: {config}")
    
    def export_data(self, filepath: str, format: str = 'json'):
        """Exporta datos capturados a un archivo"""
        try:
            data = list(self.network_data)
            
            if format.lower() == 'json':
                import json
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            
            elif format.lower() == 'csv':
                import csv
                if data:
                    with open(filepath, 'w', newline='', encoding='utf-8') as f:
                        if isinstance(data[0], dict):
                            fieldnames = data[0].keys()
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(data)
                        else:
                            writer = csv.writer(f)
                            writer.writerows(data)
            
            logger.info(f"[DOC] Datos exportados a {filepath} ({len(data)} registros)")
            
        except Exception as e:
            logger.error(f"[ERROR] Error exportando datos: {e}")


def test_network_monitor():
    """Función de prueba del monitor de red"""
    def on_suspicious_activity(data):
        print(f"🚨 Actividad sospechosa: {data['remote_ip']}:{data['remote_port']}")
        print(f"   Proceso: {data.get('process_name', 'unknown')}")
    
    monitor = NetworkTrafficMonitor(callback=on_suspicious_activity)
    
    try:
        print("[NET] Iniciando test del monitor de red...")
        monitor.start_monitoring()
        
        # Ejecutar por 30 segundos
        time.sleep(30)
        
        # Mostrar estadísticas
        stats = monitor.get_stats()
        print(f"[DATA] Estadísticas:")
        print(f"   Paquetes capturados: {stats['packets_captured']}")
        print(f"   Conexiones sospechosas: {stats['suspicious_connections']}")
        
        # Mostrar datos recientes
        recent_data = monitor.get_recent_data(5)
        print(f"\n[INFO] Últimas 5 conexiones:")
        for i, conn in enumerate(recent_data, 1):
            print(f"   {i}. {conn.get('remote_ip', 'N/A')}:{conn.get('remote_port', 'N/A')} - {conn.get('process_name', 'unknown')}")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrumpido por usuario")
    
    finally:
        monitor.stop_monitoring()
        print("[OK] Test completado")


if __name__ == "__main__":
    test_network_monitor()