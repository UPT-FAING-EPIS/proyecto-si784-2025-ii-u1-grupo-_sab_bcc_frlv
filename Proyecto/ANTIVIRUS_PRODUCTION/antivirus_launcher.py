#!/usr/bin/env python3
"""
Launcher del Sistema Anti-Keylogger
===================================

Script principal para ejecutar el sistema antivirus anti-keylogger
con todas sus funcionalidades integradas.
"""

import sys
import os
import argparse
import signal
import time
from pathlib import Path

# Añadir el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Imports del sistema antivirus
try:
    from antivirus import AntiKeyloggerEngine
    from antivirus.monitors import NetworkTrafficMonitor, ProcessBehaviorMonitor, FileSystemMonitor
    from antivirus.detectors import MLKeyloggerDetector, BehaviorDetector, NetworkPatternDetector
    from antivirus.utils import FileScanner
except ImportError as e:
    print(f"❌ Error importando módulos del antivirus: {e}")
    print("Asegúrate de que el sistema está correctamente instalado")
    sys.exit(1)


class AntivirusLauncher:
    """Launcher principal del sistema antivirus"""
    
    def __init__(self):
        self.engine = None
        self.running = True
        
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Manejo de señales para cierre limpio"""
        print(f"\n🛑 Recibida señal {signum}, cerrando sistema...")
        self.running = False
        if self.engine:
            self.engine.stop_protection()
    
    def run_real_time_protection(self, config_file: str = None):
        """Ejecuta la protección en tiempo real"""
        try:
            print("🛡️ SISTEMA ANTI-KEYLOGGER CON MACHINE LEARNING")
            print("=" * 50)
            print("🔄 Iniciando protección en tiempo real...")
            
            # Crear motor del antivirus
            config_path = config_file or "antivirus/config.toml"
            self.engine = AntiKeyloggerEngine(config_path)
            
            # Callback para mostrar amenazas
            def on_threat_detected(threat):
                severity_icon = "🚨" if threat.get('severity') == 'high' else "⚠️"
                print(f"\n{severity_icon} AMENAZA DETECTADA:")
                print(f"   Tipo: {threat.get('type', 'Desconocido')}")
                print(f"   Severidad: {threat.get('severity', 'Media')}")
                print(f"   Confianza: {threat.get('confidence', 0.0):.1%}")
                print(f"   Fuente: {threat.get('source', 'N/A')}")
                print(f"   Timestamp: {threat.get('timestamp', 'N/A')}")
                
                # Mostrar detalles adicionales
                details = threat.get('details', {})
                if details:
                    print("   Detalles:")
                    for key, value in details.items():
                        print(f"     {key}: {value}")
            
            # Registrar callback
            self.engine.add_threat_callback(on_threat_detected)
            
            # Iniciar protección
            self.engine.start_protection()
            print("✅ Protección activa. Presiona Ctrl+C para detener...")
            
            # Bucle principal con estadísticas periódicas
            last_stats_time = time.time()
            
            while self.running:
                time.sleep(1)
                
                # Mostrar estadísticas cada 30 segundos
                current_time = time.time()
                if current_time - last_stats_time >= 30:
                    self._show_stats()
                    last_stats_time = current_time
            
        except KeyboardInterrupt:
            print("\n🛑 Protección interrumpida por usuario")
        except Exception as e:
            print(f"❌ Error ejecutando protección: {e}")
        finally:
            if self.engine:
                self.engine.stop_protection()
                print("✅ Sistema detenido correctamente")
    
    def _show_stats(self):
        """Muestra estadísticas del sistema"""
        if not self.engine:
            return
        
        try:
            status = self.engine.get_status()
            stats = status.get('stats', {})
            
            print(f"\n📊 ESTADÍSTICAS DEL SISTEMA:")
            print(f"   Escaneos realizados: {stats.get('scans_performed', 0)}")
            print(f"   Amenazas detectadas: {stats.get('threats_detected', 0)}")
            print(f"   Monitores activos: {status.get('monitors_active', 0)}")
            print(f"   ML detector: {'✅' if status.get('ml_detector_loaded') else '❌'}")
            
            if stats.get('start_time'):
                uptime = time.time() - stats['start_time'].timestamp()
                hours, remainder = divmod(uptime, 3600)
                minutes, _ = divmod(remainder, 60)
                print(f"   Tiempo activo: {int(hours):02d}:{int(minutes):02d}")
                
        except Exception as e:
            print(f"❌ Error mostrando estadísticas: {e}")
    
    def run_manual_scan(self, target_path: str):
        """Ejecuta un escaneo manual"""
        try:
            print(f"🔍 ESCANEO MANUAL: {target_path}")
            print("=" * 50)
            
            # Crear motor del antivirus
            self.engine = AntiKeyloggerEngine()
            
            # Realizar escaneo
            print(f"🔄 Escaneando: {target_path}")
            self.engine.perform_manual_scan(target_path)
            
            # Mostrar resultados
            status = self.engine.get_status()
            stats = status.get('stats', {})
            print(f"\n📊 RESULTADOS:")
            print(f"   Amenazas detectadas: {stats.get('threats_detected', 0)}")
            
        except Exception as e:
            print(f"❌ Error en escaneo manual: {e}")
    
    def test_components(self):
        """Prueba los componentes del sistema"""
        print("🧪 PRUEBA DE COMPONENTES")
        print("=" * 50)
        
        # Test ML Detector
        print("\n🤖 Probando ML Detector...")
        try:
            ml_detector = MLKeyloggerDetector()
            if ml_detector.is_loaded():
                print("   ✅ ML Detector cargado correctamente")
                stats = ml_detector.get_stats()
                print(f"   📊 Modelo: {stats['model_type']}")
                print(f"   📊 Features: {stats['feature_count']}")
            else:
                print("   ❌ Error cargando ML Detector")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test Network Monitor
        print("\n🌐 Probando Network Monitor...")
        try:
            net_monitor = NetworkTrafficMonitor()
            print("   ✅ Network Monitor inicializado")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test Process Monitor
        print("\n⚙️ Probando Process Monitor...")
        try:
            proc_monitor = ProcessBehaviorMonitor()
            print("   ✅ Process Monitor inicializado")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test File Monitor
        print("\n📁 Probando File Monitor...")
        try:
            file_monitor = FileSystemMonitor()
            print("   ✅ File Monitor inicializado")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test File Scanner
        print("\n📄 Probando File Scanner...")
        try:
            scanner = FileScanner()
            print("   ✅ File Scanner inicializado")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n✅ Prueba de componentes completada")
    
    def show_system_info(self):
        """Muestra información del sistema"""
        print("ℹ️ INFORMACIÓN DEL SISTEMA")
        print("=" * 50)
        
        try:
            # Información básica
            print(f"🐍 Python: {sys.version}")
            print(f"💻 Plataforma: {sys.platform}")
            print(f"📁 Directorio de trabajo: {os.getcwd()}")
            
            # Verificar dependencias
            print("\n📦 DEPENDENCIAS:")
            
            dependencies = [
                ('psutil', 'Monitoreo de procesos y sistema'),
                ('numpy', 'Computación numérica'),
                ('pandas', 'Análisis de datos'), 
                ('scikit-learn', 'Machine Learning'),
                ('onnxruntime', 'Runtime ONNX'),
                ('toml', 'Configuración'),
                ('joblib', 'Serialización de modelos'),
                ('magic', 'Detección de tipos de archivo')
            ]
            
            for dep_name, description in dependencies:
                try:
                    __import__(dep_name)
                    print(f"   ✅ {dep_name}: {description}")
                except ImportError:
                    print(f"   ❌ {dep_name}: {description} (NO INSTALADO)")
            
            # Verificar modelos ML
            print("\n🤖 MODELOS ML:")
            models_dir = Path("models/development")
            if models_dir.exists():
                print(f"   📁 Directorio: {models_dir}")
                
                model_files = [
                    ("modelo_keylogger_from_datos.pkl", "Modelo sklearn"),
                    ("modelo_keylogger_from_datos.onnx", "Modelo ONNX"),
                    ("metadata.json", "Metadatos del modelo"),
                    ("label_classes.json", "Clases de etiquetas")
                ]
                
                for filename, description in model_files:
                    file_path = models_dir / filename
                    if file_path.exists():
                        size_kb = file_path.stat().st_size / 1024
                        print(f"   ✅ {filename}: {description} ({size_kb:.1f} KB)")
                    else:
                        print(f"   ❌ {filename}: {description} (NO ENCONTRADO)")
            else:
                print(f"   ❌ Directorio de modelos no encontrado: {models_dir}")
            
        except Exception as e:
            print(f"❌ Error obteniendo información: {e}")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Sistema Anti-Keylogger con Machine Learning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python antivirus_launcher.py                    # Protección en tiempo real
  python antivirus_launcher.py --scan C:\\Temp     # Escaneo manual
  python antivirus_launcher.py --test             # Probar componentes
  python antivirus_launcher.py --info             # Información del sistema
        """
    )
    
    parser.add_argument(
        '--scan', 
        type=str, 
        metavar='PATH',
        help='Realizar escaneo manual de directorio o archivo'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        metavar='FILE',
        help='Archivo de configuración personalizado'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Probar componentes del sistema'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Mostrar información del sistema'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Salida detallada'
    )
    
    args = parser.parse_args()
    
    # Configurar logging si verbose
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Crear launcher
    launcher = AntivirusLauncher()
    
    try:
        if args.test:
            launcher.test_components()
        elif args.info:
            launcher.show_system_info()
        elif args.scan:
            launcher.run_manual_scan(args.scan)
        else:
            launcher.run_real_time_protection(args.config)
            
    except Exception as e:
        print(f"❌ Error ejecutando launcher: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()