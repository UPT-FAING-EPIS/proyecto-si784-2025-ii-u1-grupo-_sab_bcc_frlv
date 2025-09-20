"""
Escáner de Archivos
==================

Utilidades para escanear archivos y detectar amenazas usando
análisis estático y el detector ML.
"""

import logging
import hashlib
import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import magic  # python-magic para detección de tipo de archivo

logger = logging.getLogger(__name__)


class FileScanner:
    """Escáner de archivos para detección de amenazas"""
    
    def __init__(self, ml_detector=None):
        self.ml_detector = ml_detector
        
        # Configuración
        self.config = {
            'max_file_size_mb': 100,
            'scan_archives': False,
            'deep_scan': True,
            'calculate_hashes': True,
            'suspicious_extensions': [
                '.exe', '.dll', '.scr', '.pif', '.com', '.bat', '.cmd',
                '.vbs', '.js', '.jar', '.zip', '.rar', '.7z'
            ],
            'skip_extensions': [
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
                '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.wmv'
            ]
        }
        
        # Estadísticas
        self.stats = {
            'files_scanned': 0,
            'threats_found': 0,
            'files_skipped': 0,
            'scan_errors': 0
        }
        
        # Base de datos de hashes maliciosos (simplificada)
        self.malicious_hashes = {
            # Hashes de ejemplo - en un sistema real se cargarían desde feeds
            'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',  # Ejemplo
            '5d41402abc4b2a76b9719d911017c592',  # Otro ejemplo
        }
        
        logger.info("[DOC] FileScanner inicializado")
    
    def scan_file(self, file_path: str) -> Dict:
        """Escanea un archivo individual"""
        result = {
            'file_path': file_path,
            'is_threat': False,
            'threat_type': 'none',
            'confidence': 0.0,
            'scan_time': datetime.now().isoformat(),
            'details': {},
            'errors': []
        }
        
        try:
            path_obj = Path(file_path)
            
            # Verificar si el archivo existe
            if not path_obj.exists():
                result['errors'].append('File not found')
                self.stats['scan_errors'] += 1
                return result
            
            # Verificar tamaño
            file_size = path_obj.stat().st_size
            if file_size > self.config['max_file_size_mb'] * 1024 * 1024:
                result['errors'].append('File too large for scanning')
                self.stats['files_skipped'] += 1
                return result
            
            # Verificar extensión
            extension = path_obj.suffix.lower()
            if extension in self.config['skip_extensions']:
                result['details']['skipped_reason'] = 'Extension in skip list'
                self.stats['files_skipped'] += 1
                return result
            
            # Análisis básico del archivo
            basic_analysis = self._basic_file_analysis(file_path)
            result['details'].update(basic_analysis)
            
            # Análisis de hash
            if self.config['calculate_hashes']:
                hash_analysis = self._hash_analysis(file_path)
                result['details'].update(hash_analysis)
                
                # Verificar hashes maliciosos conocidos
                if hash_analysis.get('sha256') in self.malicious_hashes:
                    result['is_threat'] = True
                    result['threat_type'] = 'known_malware'
                    result['confidence'] = 1.0
                    result['details']['detection_method'] = 'hash_signature'
            
            # Análisis de contenido
            if self.config['deep_scan']:
                content_analysis = self._content_analysis(file_path)
                result['details'].update(content_analysis)
                
                # Verificar contenido sospechoso
                if content_analysis.get('is_suspicious', False):
                    result['is_threat'] = True
                    result['threat_type'] = 'suspicious_content'
                    result['confidence'] = content_analysis.get('suspicion_score', 0.5)
                    result['details']['detection_method'] = 'content_analysis'
            
            # Análisis con ML si está disponible
            if self.ml_detector and not result['is_threat']:
                ml_analysis = self._ml_analysis(file_path, result['details'])
                if ml_analysis.get('is_threat', False):
                    result['is_threat'] = True
                    result['threat_type'] = 'ml_detection'
                    result['confidence'] = ml_analysis.get('confidence', 0.5)
                    result['details']['ml_analysis'] = ml_analysis
                    result['details']['detection_method'] = 'machine_learning'
            
            self.stats['files_scanned'] += 1
            if result['is_threat']:
                self.stats['threats_found'] += 1
                
        except Exception as e:
            error_msg = f"Scan error: {str(e)}"
            result['errors'].append(error_msg)
            self.stats['scan_errors'] += 1
            logger.error(f"[ERROR] Error escaneando {file_path}: {e}")
        
        return result
    
    def _basic_file_analysis(self, file_path: str) -> Dict:
        """Análisis básico del archivo"""
        analysis = {}
        
        try:
            path_obj = Path(file_path)
            stat = path_obj.stat()
            
            # Información básica
            analysis.update({
                'file_name': path_obj.name,
                'file_extension': path_obj.suffix.lower(),
                'file_size': stat.st_size,
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'is_hidden': self._is_hidden_file(file_path)
            })
            
            # Detección de tipo MIME
            try:
                mime_type = magic.from_file(file_path, mime=True)
                analysis['mime_type'] = mime_type
                analysis['is_executable'] = 'executable' in mime_type or mime_type.startswith('application/')
            except Exception:
                # Fallback si python-magic no está disponible
                analysis['mime_type'] = 'unknown'
                analysis['is_executable'] = path_obj.suffix.lower() in ['.exe', '.dll', '.scr', '.com']
            
            # Análisis de nombre
            file_name_lower = path_obj.name.lower()
            suspicious_names = [
                'keylog', 'password', 'credential', 'stealer', 'hack',
                'spy', 'capture', 'monitor', 'trojan', 'virus'
            ]
            
            analysis['has_suspicious_name'] = any(name in file_name_lower for name in suspicious_names)
            
            # Análisis de ubicación
            path_lower = str(path_obj.parent).lower()
            suspicious_locations = ['temp', 'tmp', 'cache', 'downloads']
            analysis['in_suspicious_location'] = any(loc in path_lower for loc in suspicious_locations)
            
        except Exception as e:
            logger.debug(f"Error en análisis básico: {e}")
        
        return analysis
    
    def _hash_analysis(self, file_path: str) -> Dict:
        """Calcula hashes del archivo"""
        hashes = {}
        
        try:
            # Calcular múltiples hashes
            hash_algorithms = {
                'md5': hashlib.md5(),
                'sha1': hashlib.sha1(),
                'sha256': hashlib.sha256()
            }
            
            with open(file_path, 'rb') as f:
                # Leer archivo en chunks para manejar archivos grandes
                while chunk := f.read(8192):
                    for hash_obj in hash_algorithms.values():
                        hash_obj.update(chunk)
            
            # Obtener hashes finales
            for name, hash_obj in hash_algorithms.items():
                hashes[name] = hash_obj.hexdigest()
                
        except Exception as e:
            logger.debug(f"Error calculando hashes: {e}")
            hashes['error'] = str(e)
        
        return hashes
    
    def _content_analysis(self, file_path: str) -> Dict:
        """Análisis de contenido del archivo"""
        analysis = {
            'is_suspicious': False,
            'suspicion_score': 0.0,
            'suspicious_strings': [],
            'embedded_files': False,
            'encrypted_content': False
        }
        
        try:
            file_size = os.path.getsize(file_path)
            
            # Solo analizar archivos de texto/ejecutables pequeños
            if file_size > 10 * 1024 * 1024:  # > 10MB
                return analysis
            
            # Leer contenido
            try:
                # Intentar como texto primero
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(10000)  # Primeros 10KB
                    analysis.update(self._analyze_text_content(content))
            except Exception:
                # Si falla como texto, leer como binario
                with open(file_path, 'rb') as f:
                    binary_content = f.read(10000)
                    analysis.update(self._analyze_binary_content(binary_content))
            
        except Exception as e:
            logger.debug(f"Error en análisis de contenido: {e}")
        
        return analysis
    
    def _analyze_text_content(self, content: str) -> Dict:
        """Analiza contenido de texto"""
        analysis = {
            'is_suspicious': False,
            'suspicion_score': 0.0,
            'suspicious_strings': []
        }
        
        content_lower = content.lower()
        
        # Patrones sospechosos en texto
        suspicious_patterns = {
            'keylogger_strings': [
                'getkeystate', 'setwindowshookex', 'keyboard', 'keydown',
                'keypress', 'capture key', 'log key', 'hook key'
            ],
            'credential_theft': [
                'password', 'username', 'login', 'credential', 'auth',
                'cookie', 'session', 'token', 'steal', 'dump'
            ],
            'malware_behavior': [
                'inject', 'shellcode', 'payload', 'backdoor', 'rootkit',
                'virus', 'trojan', 'ransomware', 'crypter'
            ],
            'network_activity': [
                'send data', 'upload', 'download', 'http post', 'ftp',
                'email send', 'exfiltrate', 'beacon'
            ]
        }
        
        for category, patterns in suspicious_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    analysis['suspicious_strings'].append(f"{category}: {pattern}")
                    analysis['suspicion_score'] += 0.1
        
        # Verificar estructuras de código malicioso
        malicious_code_patterns = [
            'eval(', 'exec(', 'system(', 'shell_exec',
            'base64_decode', 'gzinflate', 'str_rot13'
        ]
        
        for pattern in malicious_code_patterns:
            if pattern in content_lower:
                analysis['suspicious_strings'].append(f"malicious_code: {pattern}")
                analysis['suspicion_score'] += 0.2
        
        # Normalizar score
        analysis['suspicion_score'] = min(analysis['suspicion_score'], 1.0)
        analysis['is_suspicious'] = analysis['suspicion_score'] > 0.3
        
        return analysis
    
    def _analyze_binary_content(self, content: bytes) -> Dict:
        """Analiza contenido binario"""
        analysis = {
            'is_suspicious': False,
            'suspicion_score': 0.0,
            'suspicious_strings': []
        }
        
        try:
            # Convertir a string para análisis
            content_str = content.decode('utf-8', errors='ignore').lower()
            
            # Buscar strings sospechosos en binarios
            binary_suspicious_patterns = [
                'kernel32.dll', 'ntdll.dll', 'user32.dll',
                'setwindowshookex', 'getasynckeystate', 'registerrawinputdevices',
                'writefile', 'createfile', 'internetopen',
                'winsock', 'socket', 'connect', 'send'
            ]
            
            for pattern in binary_suspicious_patterns:
                if pattern in content_str:
                    analysis['suspicious_strings'].append(f"binary_api: {pattern}")
                    analysis['suspicion_score'] += 0.15
            
            # Detectar contenido cifrado/comprimido
            entropy = self._calculate_entropy(content)
            if entropy > 7.5:  # Alta entropía indica cifrado/compresión
                analysis['suspicious_strings'].append(f"high_entropy: {entropy:.2f}")
                analysis['suspicion_score'] += 0.3
                analysis['encrypted_content'] = True
            
            # Verificar headers de ejecutables PE
            if content.startswith(b'MZ'):  # PE header
                analysis['suspicious_strings'].append("pe_executable")
                analysis['suspicion_score'] += 0.2
            
            # Verificar archivos embebidos
            embedded_signatures = [b'PK\x03\x04', b'\x1f\x8b', b'Rar!']  # ZIP, GZIP, RAR
            for sig in embedded_signatures:
                if sig in content:
                    analysis['suspicious_strings'].append("embedded_archive")
                    analysis['suspicion_score'] += 0.2
                    analysis['embedded_files'] = True
                    break
            
            analysis['suspicion_score'] = min(analysis['suspicion_score'], 1.0)
            analysis['is_suspicious'] = analysis['suspicion_score'] > 0.4
            
        except Exception as e:
            logger.debug(f"Error en análisis binario: {e}")
        
        return analysis
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calcula la entropía de Shannon de los datos"""
        if not data:
            return 0.0
        
        try:
            import math
            from collections import Counter
            
            # Contar frecuencia de bytes
            byte_counts = Counter(data)
            data_len = len(data)
            
            # Calcular entropía
            entropy = 0.0
            for count in byte_counts.values():
                probability = count / data_len
                entropy -= probability * math.log2(probability)
            
            return entropy
            
        except Exception:
            return 0.0
    
    def _ml_analysis(self, file_path: str, file_details: Dict) -> Dict:
        """Análisis usando el detector ML"""
        analysis = {
            'is_threat': False,
            'confidence': 0.0,
            'ml_prediction': 'unknown'
        }
        
        try:
            if not self.ml_detector:
                return analysis
            
            # Convertir información del archivo a formato para ML
            # Esto requeriría adaptar los datos del archivo al formato esperado
            # por el modelo ML (características de red, etc.)
            
            # Por ahora, análisis simplificado basado en características
            risk_score = 0.0
            
            # Factores de riesgo
            if file_details.get('has_suspicious_name', False):
                risk_score += 0.3
            
            if file_details.get('is_executable', False):
                risk_score += 0.2
            
            if file_details.get('in_suspicious_location', False):
                risk_score += 0.2
            
            if file_details.get('is_hidden', False):
                risk_score += 0.3
            
            # Si tenemos análisis de contenido
            if 'suspicion_score' in file_details:
                risk_score += file_details['suspicion_score'] * 0.5
            
            analysis['confidence'] = min(risk_score, 1.0)
            analysis['is_threat'] = risk_score > 0.6
            analysis['ml_prediction'] = 'malicious' if analysis['is_threat'] else 'benign'
            
        except Exception as e:
            logger.debug(f"Error en análisis ML: {e}")
        
        return analysis
    
    def _is_hidden_file(self, file_path: str) -> bool:
        """Verifica si un archivo está oculto"""
        try:
            import stat
            file_attributes = os.stat(file_path).st_file_attributes
            return bool(file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
        except Exception:
            return Path(file_path).name.startswith('.')
    
    def scan_directory(self, directory_path: str, recursive: bool = True) -> List[Dict]:
        """Escanea todos los archivos en un directorio"""
        results = []
        
        try:
            path_obj = Path(directory_path)
            
            if not path_obj.exists():
                logger.error(f"[ERROR] Directorio no existe: {directory_path}")
                return results
            
            # Obtener lista de archivos
            if recursive:
                files = list(path_obj.rglob('*'))
            else:
                files = list(path_obj.glob('*'))
            
            # Filtrar solo archivos (no directorios)
            files = [f for f in files if f.is_file()]
            
            logger.info(f"[SEARCH] Escaneando {len(files)} archivos en {directory_path}")
            
            # Escanear cada archivo
            for i, file_path in enumerate(files):
                try:
                    result = self.scan_file(str(file_path))
                    results.append(result)
                    
                    # Log de progreso cada 100 archivos
                    if (i + 1) % 100 == 0:
                        threats_found = sum(1 for r in results if r['is_threat'])
                        logger.info(f"[DATA] Progreso: {i+1}/{len(files)} archivos, {threats_found} amenazas")
                        
                except Exception as e:
                    logger.error(f"[ERROR] Error escaneando {file_path}: {e}")
                    self.stats['scan_errors'] += 1
            
            # Resumen final
            threats_found = sum(1 for r in results if r['is_threat'])
            logger.info(f"[OK] Escaneo completado: {len(results)} archivos, {threats_found} amenazas")
            
        except Exception as e:
            logger.error(f"[ERROR] Error escaneando directorio: {e}")
        
        return results
    
    def scan_file_list(self, file_paths: List[str]) -> List[Dict]:
        """Escanea una lista específica de archivos"""
        results = []
        
        logger.info(f"[SEARCH] Escaneando {len(file_paths)} archivos específicos")
        
        for i, file_path in enumerate(file_paths):
            try:
                result = self.scan_file(file_path)
                results.append(result)
                
                if (i + 1) % 50 == 0:
                    threats_found = sum(1 for r in results if r['is_threat'])
                    logger.info(f"[DATA] Progreso: {i+1}/{len(file_paths)} archivos, {threats_found} amenazas")
                    
            except Exception as e:
                logger.error(f"[ERROR] Error escaneando {file_path}: {e}")
                self.stats['scan_errors'] += 1
        
        threats_found = sum(1 for r in results if r['is_threat'])
        logger.info(f"[OK] Escaneo de lista completado: {threats_found} amenazas encontradas")
        
        return results
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del escáner"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reinicia las estadísticas"""
        self.stats = {
            'files_scanned': 0,
            'threats_found': 0,
            'files_skipped': 0,
            'scan_errors': 0
        }
        logger.info("[DATA] Estadísticas del escáner reiniciadas")
    
    def add_malicious_hash(self, hash_value: str):
        """Añade un hash a la lista de hashes maliciosos"""
        self.malicious_hashes.add(hash_value.lower())
        logger.info(f"➕ Hash malicioso añadido: {hash_value[:16]}...")
    
    def update_config(self, new_config: Dict):
        """Actualiza la configuración del escáner"""
        self.config.update(new_config)
        logger.info(f"[PROC] Configuración actualizada: {new_config}")


def test_file_scanner():
    """Función de prueba del escáner de archivos"""
    scanner = FileScanner()
    
    print("[DOC] Testing FileScanner...")
    
    # Crear archivo de prueba
    test_file = Path("test_suspicious.txt")
    test_content = """
    This is a test file with suspicious content.
    GetKeyState function call detected.
    Password: admin123
    SetWindowsHookEx keyboard hook
    """
    
    try:
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Escanear archivo de prueba
        result = scanner.scan_file(str(test_file))
        
        print(f"[DATA] Resultado del escaneo:")
        print(f"   Archivo: {result['file_path']}")
        print(f"   Es amenaza: {result['is_threat']}")
        print(f"   Tipo de amenaza: {result['threat_type']}")
        print(f"   Confianza: {result['confidence']:.2f}")
        print(f"   Strings sospechosos: {result['details'].get('suspicious_strings', [])}")
        
        # Estadísticas
        stats = scanner.get_stats()
        print(f"\n[STATS] Estadísticas:")
        print(f"   Archivos escaneados: {stats['files_scanned']}")
        print(f"   Amenazas encontradas: {stats['threats_found']}")
        print(f"   Errores de escaneo: {stats['scan_errors']}")
        
    finally:
        # Limpiar archivo de prueba
        if test_file.exists():
            test_file.unlink()
    
    print("[OK] Test completado")


if __name__ == "__main__":
    test_file_scanner()