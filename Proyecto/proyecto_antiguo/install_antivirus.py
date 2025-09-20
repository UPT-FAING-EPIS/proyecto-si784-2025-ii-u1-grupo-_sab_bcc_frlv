#!/usr/bin/env python3
"""
Instalador del Sistema Anti-Keylogger
=====================================

Script de instalación automática que configura el entorno,
instala dependencias y verifica la configuración del sistema.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import json


class AntivirusInstaller:
    """Instalador del sistema antivirus"""
    
    def __init__(self):
        self.python_version = sys.version_info
        self.platform = platform.system()
        self.root_dir = Path(__file__).parent
        self.errors = []
        self.warnings = []
        
    def run_installation(self):
        """Ejecuta la instalación completa"""
        print("[SHIELD] INSTALADOR DEL SISTEMA ANTI-KEYLOGGER")
        print("=" * 50)
        
        try:
            # Verificaciones previas
            self._check_system_requirements()
            
            # Instalación de dependencias
            self._install_dependencies()
            
            # Verificación de modelos ML
            self._check_ml_models()
            
            # Configuración del sistema
            self._setup_directories()
            
            # Pruebas finales
            self._run_system_tests()
            
            # Resumen de instalación
            self._show_installation_summary()
            
        except Exception as e:
            print(f"[ERROR] Error durante la instalación: {e}")
            sys.exit(1)
    
    def _check_system_requirements(self):
        """Verifica requisitos del sistema"""
        print("\n[SEARCH] VERIFICANDO REQUISITOS DEL SISTEMA")
        print("-" * 40)
        
        # Verificar versión de Python
        if self.python_version < (3, 8):
            self.errors.append(f"Python 3.8+ requerido, encontrado {self.python_version}")
        else:
            print(f"[OK] Python {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        
        # Verificar plataforma
        print(f"[OK] Plataforma: {self.platform}")
        if self.platform not in ['Windows', 'Linux', 'Darwin']:
            self.warnings.append(f"Plataforma {self.platform} no completamente soportada")
        
        # Verificar permisos
        if not os.access(self.root_dir, os.W_OK):
            self.errors.append("Sin permisos de escritura en directorio del proyecto")
        else:
            print("[OK] Permisos de escritura")
        
        # Verificar espacio en disco
        free_space = self._get_free_space()
        if free_space < 1024 * 1024 * 1024:  # 1GB
            self.warnings.append(f"Poco espacio libre: {free_space / (1024**3):.1f}GB")
        else:
            print(f"[OK] Espacio libre: {free_space / (1024**3):.1f}GB")
        
        if self.errors:
            print("\n[ERROR] ERRORES CRÍTICOS:")
            for error in self.errors:
                print(f"   - {error}")
            sys.exit(1)
        
        if self.warnings:
            print("\n[WARNING] ADVERTENCIAS:")
            for warning in self.warnings:
                print(f"   - {warning}")
    
    def _install_dependencies(self):
        """Instala dependencias del proyecto"""
        print("\n[PACKAGE] INSTALANDO DEPENDENCIAS")
        print("-" * 40)
        
        # Verificar pip
        try:
            import pip
            print("[OK] pip disponible")
        except ImportError:
            print("[ERROR] pip no encontrado")
            sys.exit(1)
        
        # Instalar dependencias principales
        requirements_files = [
            "requirements.txt",          # Dependencias ML básicas
            "requirements_antivirus.txt" # Dependencias del antivirus
        ]
        
        for req_file in requirements_files:
            req_path = self.root_dir / req_file
            if req_path.exists():
                print(f"[IN] Instalando desde {req_file}...")
                try:
                    result = subprocess.run([
                        sys.executable, "-m", "pip", "install", "-r", str(req_path)
                    ], capture_output=True, text=True, check=True)
                    print(f"[OK] {req_file} instalado")
                except subprocess.CalledProcessError as e:
                    print(f"[WARNING] Error instalando {req_file}: {e}")
                    self.warnings.append(f"Fallo en instalación de {req_file}")
            else:
                print(f"[WARNING] {req_file} no encontrado")
        
        # Verificar dependencias críticas
        critical_deps = [
            'psutil', 'numpy', 'pandas', 'scikit-learn', 
            'onnxruntime', 'joblib', 'toml'
        ]
        
        print("\n[SEARCH] Verificando dependencias críticas...")
        for dep in critical_deps:
            try:
                __import__(dep)
                print(f"[OK] {dep}")
            except ImportError:
                print(f"[ERROR] {dep} - FALTANTE")
                self.errors.append(f"Dependencia crítica faltante: {dep}")
        
        # Verificar dependencias opcionales
        optional_deps = [
            ('magic', 'Detección de tipos de archivo'),
            ('watchdog', 'Monitoreo de archivos avanzado'),
            ('cryptography', 'Análisis de archivos cifrados'),
            ('pefile', 'Análisis de ejecutables PE')
        ]
        
        print("\n[SEARCH] Verificando dependencias opcionales...")
        for dep, description in optional_deps:
            try:
                __import__(dep)
                print(f"[OK] {dep}: {description}")
            except ImportError:
                print(f"[WARNING] {dep}: {description} - OPCIONAL")
    
    def _check_ml_models(self):
        """Verifica la disponibilidad de modelos ML"""
        print("\n[ML] VERIFICANDO MODELOS DE MACHINE LEARNING")
        print("-" * 40)
        
        models_dir = self.root_dir / "models" / "development"
        
        if not models_dir.exists():
            print(f"[WARNING] Directorio de modelos no encontrado: {models_dir}")
            self.warnings.append("Modelos ML no encontrados - ejecutar entrenamiento")
            return
        
        # Verificar archivos de modelo
        model_files = {
            "modelo_keylogger_from_datos.pkl": "Modelo scikit-learn",
            "modelo_keylogger_from_datos.onnx": "Modelo ONNX optimizado", 
            "metadata.json": "Metadatos del modelo",
            "label_classes.json": "Clases de clasificación"
        }
        
        models_found = 0
        for filename, description in model_files.items():
            file_path = models_dir / filename
            if file_path.exists():
                size_kb = file_path.stat().st_size / 1024
                print(f"[OK] {filename}: {description} ({size_kb:.1f} KB)")
                models_found += 1
            else:
                print(f"[ERROR] {filename}: {description} - NO ENCONTRADO")
        
        if models_found == 0:
            self.errors.append("No se encontraron modelos ML - ejecutar entrenamiento primero")
        elif models_found < len(model_files):
            self.warnings.append("Algunos modelos ML faltantes - funcionalidad limitada")
        
        # Verificar integridad de modelos
        if models_found > 0:
            print("\n[SEARCH] Verificando integridad de modelos...")
            self._test_model_loading()
    
    def _test_model_loading(self):
        """Prueba la carga de modelos ML"""
        try:
            # Intentar cargar modelo sklearn
            sklearn_path = self.root_dir / "models" / "development" / "modelo_keylogger_from_datos.pkl"
            if sklearn_path.exists():
                import joblib
                model = joblib.load(sklearn_path)
                print("[OK] Modelo sklearn carga correctamente")
        except Exception as e:
            print(f"[ERROR] Error cargando modelo sklearn: {e}")
            self.warnings.append("Modelo sklearn corrupto o incompatible")
        
        try:
            # Intentar cargar modelo ONNX
            onnx_path = self.root_dir / "models" / "development" / "modelo_keylogger_from_datos.onnx"
            if onnx_path.exists():
                import onnxruntime as ort
                session = ort.InferenceSession(str(onnx_path))
                print("[OK] Modelo ONNX carga correctamente")
        except Exception as e:
            print(f"[ERROR] Error cargando modelo ONNX: {e}")
            self.warnings.append("Modelo ONNX corrupto o incompatible")
    
    def _setup_directories(self):
        """Configura directorios necesarios"""
        print("\n[FILE] CONFIGURANDO DIRECTORIOS")
        print("-" * 40)
        
        # Directorios requeridos
        required_dirs = [
            "logs",
            "quarantine", 
            "temp",
            "data/exports",
            "data/backups"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.root_dir / dir_name
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"[OK] {dir_name}")
            except Exception as e:
                print(f"[ERROR] Error creando {dir_name}: {e}")
                self.warnings.append(f"No se pudo crear directorio {dir_name}")
        
        # Configurar permisos (Unix/Linux)
        if self.platform in ['Linux', 'Darwin']:
            try:
                quarantine_dir = self.root_dir / "quarantine"
                os.chmod(quarantine_dir, 0o700)  # Solo propietario
                print("[OK] Permisos de cuarentena configurados")
            except Exception as e:
                print(f"[WARNING] Error configurando permisos: {e}")
    
    def _run_system_tests(self):
        """Ejecuta pruebas básicas del sistema"""
        print("\n🧪 EJECUTANDO PRUEBAS DEL SISTEMA")
        print("-" * 40)
        
        # Test 1: Importar módulos principales
        print("[SEARCH] Probando imports...")
        try:
            from antivirus import AntiKeyloggerEngine
            from antivirus.monitors import NetworkTrafficMonitor
            from antivirus.detectors import MLKeyloggerDetector
            print("[OK] Imports principales exitosos")
        except ImportError as e:
            print(f"[ERROR] Error en imports: {e}")
            self.errors.append("Fallo en importación de módulos principales")
        
        # Test 2: Crear instancias básicas
        print("[SEARCH] Probando inicialización de componentes...")
        try:
            # Test ML Detector
            ml_detector = MLKeyloggerDetector()
            if ml_detector.is_loaded():
                print("[OK] ML Detector inicializado")
            else:
                print("[WARNING] ML Detector sin modelos cargados")
            
            # Test Network Monitor
            net_monitor = NetworkTrafficMonitor()
            print("[OK] Network Monitor inicializado")
            
        except Exception as e:
            print(f"[ERROR] Error en inicialización: {e}")
            self.warnings.append("Algunos componentes no se inicializaron correctamente")
        
        # Test 3: Verificar configuración
        print("[SEARCH] Probando configuración...")
        config_path = self.root_dir / "antivirus" / "config.toml"
        if config_path.exists():
            try:
                import toml
                config = toml.load(config_path)
                print("[OK] Configuración TOML válida")
            except Exception as e:
                print(f"[ERROR] Error en configuración: {e}")
                self.warnings.append("Archivo de configuración inválido")
        else:
            print("[WARNING] Archivo de configuración no encontrado")
    
    def _show_installation_summary(self):
        """Muestra resumen de la instalación"""
        print("\n" + "=" * 50)
        print("[INFO] RESUMEN DE INSTALACIÓN")
        print("=" * 50)
        
        # Estado general
        if not self.errors:
            print("[OK] INSTALACIÓN EXITOSA")
        else:
            print("[ERROR] INSTALACIÓN CON ERRORES")
        
        # Estadísticas
        print(f"\n[DATA] Estadísticas:")
        print(f"   Errores críticos: {len(self.errors)}")
        print(f"   Advertencias: {len(self.warnings)}")
        print(f"   Plataforma: {self.platform}")
        print(f"   Python: {self.python_version.major}.{self.python_version.minor}")
        
        # Errores
        if self.errors:
            print(f"\n[ERROR] ERRORES CRÍTICOS:")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        # Advertencias
        if self.warnings:
            print(f"\n[WARNING] ADVERTENCIAS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        # Siguientes pasos
        print(f"\n[START] SIGUIENTES PASOS:")
        
        if not self.errors:
            print("   1. Ejecutar: python antivirus_launcher.py --test")
            print("   2. Ejecutar: python antivirus_launcher.py --info")
            print("   3. Iniciar protección: python antivirus_launcher.py")
            
            if self.warnings:
                print("\n[WARNING] RECOMENDACIONES:")
                print("   - Revisar advertencias mostradas arriba")
                print("   - Instalar dependencias opcionales para funcionalidad completa")
                if "Modelos ML" in str(self.warnings):
                    print("   - Ejecutar entrenamiento: python scripts/train_from_datos.py")
        else:
            print("   1. Resolver errores críticos mostrados arriba")
            print("   2. Re-ejecutar instalación")
            print("   3. Contactar soporte si problemas persisten")
        
        # Archivos importantes
        print(f"\n[DOC] ARCHIVOS IMPORTANTES:")
        print(f"   Launcher: {self.root_dir / 'antivirus_launcher.py'}")
        print(f"   Configuración: {self.root_dir / 'antivirus' / 'config.toml'}")
        print(f"   README: {self.root_dir / 'ANTIVIRUS_README.md'}")
        print(f"   Logs: {self.root_dir / 'logs'}")
    
    def _get_free_space(self):
        """Obtiene espacio libre en disco"""
        try:
            import shutil
            return shutil.disk_usage(self.root_dir)[2]  # bytes libres
        except Exception:
            return float('inf')  # Si no se puede determinar, asumir suficiente


def main():
    """Función principal del instalador"""
    installer = AntivirusInstaller()
    
    try:
        installer.run_installation()
    except KeyboardInterrupt:
        print("\n🛑 Instalación cancelada por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado durante instalación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()