"""
Adaptadores para extracción de características de archivos.
Implementa las interfaces definidas en use_cases.
"""

import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

from ..core.use_cases import IFeatureExtractor
from ..core.domain import FileFeatures, FileType

try:
    import pefile
    HAS_PEFILE = True
except ImportError:
    HAS_PEFILE = False
    pefile = None

try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    magic = None


class FileFeatureExtractor(IFeatureExtractor):
    """Extractor principal de características de archivos."""
    
    def __init__(self):
        self.extractors = {
            FileType.EXECUTABLE: ExecutableFeatureExtractor(),
            FileType.DOCUMENT: DocumentFeatureExtractor(),
            FileType.IMAGE: ImageFeatureExtractor(),
            FileType.ARCHIVE: ArchiveFeatureExtractor(),
            FileType.MEDIA: MediaFeatureExtractor(),
            FileType.CSV: CSVFeatureExtractor(),
        }
    
    def extract_features(self, file_path: Path) -> FileFeatures:
        """Extrae características del archivo."""
        file_type = self._detect_file_type(file_path)
        
        # Características básicas
        base_features = self._extract_base_features(file_path, file_type)
        
        # Características específicas del tipo
        if file_type in self.extractors:
            specific_extractor = self.extractors[file_type]
            specific_features = specific_extractor.extract_specific_features(file_path)
            base_features.custom_features.update(specific_features)
        
        return base_features
    
    def can_process(self, file_path: Path) -> bool:
        """Verifica si puede procesar el archivo."""
        return file_path.is_file() and file_path.stat().st_size > 0
    
    def _detect_file_type(self, file_path: Path) -> FileType:
        """Detecta el tipo de archivo basado en la extensión."""
        ext = file_path.suffix.lower()
        
        executable_exts = {'.exe', '.dll', '.com', '.scr', '.bat', '.cmd'}
        document_exts = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'}
        image_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        archive_exts = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'}
        media_exts = {'.mp3', '.wav', '.mp4', '.avi', '.mkv', '.mov', '.wmv'}
        
        if ext in executable_exts:
            return FileType.EXECUTABLE
        elif ext in document_exts:
            return FileType.DOCUMENT
        elif ext in image_exts:
            return FileType.IMAGE
        elif ext in archive_exts:
            return FileType.ARCHIVE
        elif ext in media_exts:
            return FileType.MEDIA
        elif ext == '.csv':
            return FileType.CSV
        else:
            return FileType.UNKNOWN
    
    def _extract_base_features(self, file_path: Path, file_type: FileType) -> FileFeatures:
        """Extrae características básicas del archivo."""
        try:
            stat = file_path.stat()
            
            # Hash MD5
            md5_hash = None
            try:
                with open(file_path, 'rb') as f:
                    md5_hash = hashlib.md5(f.read()).hexdigest()
            except (OSError, MemoryError):
                pass  # Archivo muy grande o inaccesible
            
            return FileFeatures(
                file_size=stat.st_size,
                file_type=file_type,
                md5_hash=md5_hash,
                is_document=(file_type == FileType.DOCUMENT),
                is_image=(file_type == FileType.IMAGE),
                is_archive=(file_type == FileType.ARCHIVE),
                is_media=(file_type == FileType.MEDIA),
                custom_features={}
            )
            
        except OSError as e:
            # Archivo inaccesible
            return FileFeatures(
                file_size=0,
                file_type=file_type,
                custom_features={'error': str(e)}
            )


class BaseSpecificExtractor:
    """Clase base para extractores específicos por tipo."""
    
    def extract_specific_features(self, file_path: Path) -> Dict[str, Any]:
        """Extrae características específicas del tipo de archivo."""
        return {}


class ExecutableFeatureExtractor(BaseSpecificExtractor):
    """Extractor de características para ejecutables."""
    
    def extract_specific_features(self, file_path: Path) -> Dict[str, Any]:
        """Extrae características específicas de ejecutables."""
        features = {}
        
        if not HAS_PEFILE:
            features['pefile_available'] = False
            return features
        
        try:
            pe = pefile.PE(str(file_path))
            
            # Características PE básicas
            features.update({
                'num_sections': len(pe.sections),
                'has_imports': int(hasattr(pe, 'DIRECTORY_ENTRY_IMPORT')),
                'has_exports': int(hasattr(pe, 'DIRECTORY_ENTRY_EXPORT')),
                'has_resources': int(hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE')),
                'has_tls': int(hasattr(pe, 'DIRECTORY_ENTRY_TLS')),
                'image_base': pe.OPTIONAL_HEADER.ImageBase,
                'entry_point': pe.OPTIONAL_HEADER.AddressOfEntryPoint,
                'machine_type': pe.FILE_HEADER.Machine,
                'characteristics': pe.FILE_HEADER.Characteristics,
            })
            
            # Entropía promedio de secciones
            if pe.sections:
                entropies = [s.get_entropy() for s in pe.sections]
                features['entropy'] = sum(entropies) / len(entropies)
                features['max_entropy'] = max(entropies)
                features['min_entropy'] = min(entropies)
            
            # Información de importaciones
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                import_count = sum(len(entry.imports) for entry in pe.DIRECTORY_ENTRY_IMPORT)
                features['import_count'] = import_count
                features['dll_count'] = len(pe.DIRECTORY_ENTRY_IMPORT)
                
                # APIs sospechosas comunes en keyloggers
                suspicious_apis = {
                    'SetWindowsHookEx', 'GetAsyncKeyState', 'GetKeyState',
                    'FindWindow', 'GetWindowText', 'CreateFile', 'WriteFile',
                    'RegCreateKey', 'RegSetValue', 'GetForegroundWindow'
                }
                
                found_suspicious = set()
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    for imp in entry.imports:
                        if imp.name and imp.name.decode('utf-8', errors='ignore') in suspicious_apis:
                            found_suspicious.add(imp.name.decode('utf-8', errors='ignore'))
                
                features['suspicious_api_count'] = len(found_suspicious)
                features['has_hook_apis'] = int('SetWindowsHookEx' in found_suspicious)
                features['has_keyboard_apis'] = int(any(api in found_suspicious for api in ['GetAsyncKeyState', 'GetKeyState']))
            
            pe.close()
            
        except Exception as e:
            features['pe_error'] = str(e)[:100]  # Truncar error
        
        return features


class DocumentFeatureExtractor(BaseSpecificExtractor):
    """Extractor de características para documentos."""
    
    def extract_specific_features(self, file_path: Path) -> Dict[str, Any]:
        """Extrae características específicas de documentos."""
        features = {}
        ext = file_path.suffix.lower()
        
        # Características básicas por tipo de documento
        features.update({
            'is_pdf': int(ext == '.pdf'),
            'is_office': int(ext in {'.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'}),
            'is_text': int(ext == '.txt'),
        })
        
        # Análisis de contenido básico
        try:
            if ext == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(10240)  # Primeros 10KB
                    features['line_count'] = content.count('\n')
                    features['char_count'] = len(content)
                    features['has_urls'] = int('http' in content.lower())
        except Exception:
            pass
        
        return features


class ImageFeatureExtractor(BaseSpecificExtractor):
    """Extractor de características para imágenes."""
    
    def extract_specific_features(self, file_path: Path) -> Dict[str, Any]:
        """Extrae características específicas de imágenes."""
        features = {}
        ext = file_path.suffix.lower()
        
        features.update({
            'is_jpeg': int(ext in {'.jpg', '.jpeg'}),
            'is_png': int(ext == '.png'),
            'is_gif': int(ext == '.gif'),
            'is_bmp': int(ext == '.bmp'),
        })
        
        # Aquí se podrían agregar más características usando PIL/Pillow
        # Como dimensiones, modo de color, etc.
        
        return features


class ArchiveFeatureExtractor(BaseSpecificExtractor):
    """Extractor de características para archivos comprimidos."""
    
    def extract_specific_features(self, file_path: Path) -> Dict[str, Any]:
        """Extrae características específicas de archivos."""
        features = {}
        ext = file_path.suffix.lower()
        
        features.update({
            'is_zip': int(ext == '.zip'),
            'is_rar': int(ext == '.rar'),
            'is_7z': int(ext == '.7z'),
            'is_tar': int(ext in {'.tar', '.tar.gz', '.tar.bz2'}),
        })
        
        # Aquí se podrían agregar características como:
        # - Número de archivos en el archivo
        # - Ratio de compresión
        # - Presencia de ejecutables dentro
        
        return features


class MediaFeatureExtractor(BaseSpecificExtractor):
    """Extractor de características para archivos multimedia."""
    
    def extract_specific_features(self, file_path: Path) -> Dict[str, Any]:
        """Extrae características específicas de multimedia."""
        features = {}
        ext = file_path.suffix.lower()
        
        features.update({
            'is_audio': int(ext in {'.mp3', '.wav', '.aac', '.flac'}),
            'is_video': int(ext in {'.mp4', '.avi', '.mkv', '.mov', '.wmv'}),
        })
        
        return features


class CSVFeatureExtractor(BaseSpecificExtractor):
    """Extractor de características para archivos CSV."""
    
    def extract_specific_features(self, file_path: Path) -> Dict[str, Any]:
        """Extrae características específicas de CSV."""
        features = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Leer las primeras líneas para análisis básico
                lines = []
                for i, line in enumerate(f):
                    if i >= 100:  # Solo las primeras 100 líneas
                        break
                    lines.append(line.strip())
                
                if lines:
                    # Detectar separador más común
                    separators = [',', ';', '\t', '|']
                    sep_counts = {sep: lines[0].count(sep) for sep in separators}
                    likely_sep = max(sep_counts, key=sep_counts.get)
                    
                    features.update({
                        'csv_lines_sampled': len(lines),
                        'csv_separator': ord(likely_sep),
                        'csv_avg_fields': sum(line.count(likely_sep) + 1 for line in lines) / len(lines),
                        'csv_has_header': int(any(char.isalpha() for char in lines[0])),
                    })
                    
        except Exception as e:
            features['csv_error'] = str(e)[:100]
        
        return features