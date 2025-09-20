"""
Interfaz de línea de comandos para el sistema Anti-Keylogger.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

from ..core.config import AntiKeyloggerConfig, create_development_config, create_production_config
from ..core.domain import MonitoringSession
from ..core.use_cases import (
    FileAnalysisUseCase, DirectoryMonitoringUseCase, 
    ProcessMonitoringUseCase, ReportGenerationUseCase
)
from ..adapters.feature_extractors import FileFeatureExtractor
from ..adapters.ml_adapters import create_model_adapter
from ..infrastructure.system_adapters import (
    SystemProcessMonitor, FileSystemAlertHandler, ConsoleAlertHandler,
    FileSystemLogger, ConsoleLogger, CompositeAlertHandler, CompositeLogger
)


class AntiKeyloggerCLI:
    """Interfaz de línea de comandos principal."""
    
    def __init__(self):
        self.config: Optional[AntiKeyloggerConfig] = None
        self.session: Optional[MonitoringSession] = None
    
    def run(self):
        """Ejecuta la aplicación CLI."""
        try:
            args = self._parse_arguments()
            self._setup_configuration(args)
            self._validate_configuration()
            self._execute_command(args)
            
        except KeyboardInterrupt:
            print("\n🛑 Operación interrumpida por el usuario.")
            sys.exit(0)
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            sys.exit(1)
    
    def _parse_arguments(self) -> argparse.Namespace:
        """Analiza argumentos de línea de comandos."""
        parser = argparse.ArgumentParser(
            description="Sistema Anti-Keylogger - Detección de amenazas con ML",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Ejemplos de uso:
  python -m src.ui.cli scan-once --directory ~/Downloads
  python -m src.ui.cli monitor --interval 30 --duration 3600
  python -m src.ui.cli analyze-file malware_sample.exe
  python -m src.ui.cli scan-processes
  python -m src.ui.cli generate-config --environment development
            """
        )
        
        # Argumentos globales
        parser.add_argument(
            '--config', '-c',
            type=Path,
            help='Archivo de configuración JSON'
        )
        parser.add_argument(
            '--environment', '-e',
            choices=['development', 'production'],
            default='development',
            help='Entorno de ejecución'
        )
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Salida detallada'
        )
        
        # Subcomandos
        subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
        
        # Comando: scan-once
        scan_once = subparsers.add_parser('scan-once', help='Escanear directorio una vez')
        scan_once.add_argument(
            '--directory', '-d',
            type=Path,
            help='Directorio a escanear (por defecto: ~/Downloads)'
        )
        
        # Comando: monitor
        monitor = subparsers.add_parser('monitor', help='Monitoreo continuo')
        monitor.add_argument(
            '--interval', '-i',
            type=int,
            default=10,
            help='Intervalo entre escaneos en segundos (por defecto: 10)'
        )
        monitor.add_argument(
            '--duration', '-d',
            type=int,
            help='Duración del monitoreo en segundos (infinito si no se especifica)'
        )
        monitor.add_argument(
            '--directory',
            type=Path,
            help='Directorio a monitorear (por defecto: ~/Downloads)'
        )
        
        # Comando: analyze-file
        analyze = subparsers.add_parser('analyze-file', help='Analizar archivo específico')
        analyze.add_argument(
            'file_path',
            type=Path,
            help='Ruta del archivo a analizar'
        )
        
        # Comando: scan-processes
        processes = subparsers.add_parser('scan-processes', help='Escanear procesos en ejecución')
        
        # Comando: generate-config
        gen_config = subparsers.add_parser('generate-config', help='Generar archivo de configuración')
        gen_config.add_argument(
            '--output', '-o',
            type=Path,
            default=Path('config.json'),
            help='Archivo de salida (por defecto: config.json)'
        )
        gen_config.add_argument(
            '--environment',
            choices=['development', 'production'],
            default='development',
            help='Tipo de configuración'
        )
        
        return parser.parse_args()
    
    def _setup_configuration(self, args: argparse.Namespace):
        """Configura el sistema basado en argumentos."""
        base_dir = Path(__file__).parent.parent.parent
        
        if args.config and args.config.exists():
            # Cargar desde archivo
            self.config = AntiKeyloggerConfig.from_file(args.config)
        else:
            # Crear configuración por defecto
            if args.environment == 'production':
                self.config = create_production_config(base_dir)
            else:
                self.config = create_development_config(base_dir)
        
        # Aplicar overrides de argumentos
        if hasattr(args, 'directory') and args.directory:
            self.config.monitoring.watch_directory = args.directory
        
        if hasattr(args, 'interval') and args.interval:
            self.config.monitoring.scan_interval = args.interval
        
        if args.verbose:
            self.config.logging.console_output = True
            self.config.logging.log_level = "DEBUG"
    
    def _validate_configuration(self):
        """Valida la configuración actual."""
        errors = self.config.validate()
        if errors:
            print("[ERROR] Errores de configuración:")
            for error in errors:
                print(f"  • {error}")
            sys.exit(1)
    
    def _execute_command(self, args: argparse.Namespace):
        """Ejecuta el comando especificado."""
        if args.command == 'generate-config':
            self._generate_config_file(args)
        elif args.command == 'analyze-file':
            self._analyze_single_file(args)
        elif args.command == 'scan-once':
            self._scan_directory_once(args)
        elif args.command == 'monitor':
            self._monitor_continuously(args)
        elif args.command == 'scan-processes':
            self._scan_processes()
        else:
            print("[ERROR] Comando no especificado. Use --help para ver opciones.")
            sys.exit(1)
    
    def _generate_config_file(self, args: argparse.Namespace):
        """Genera archivo de configuración."""
        base_dir = Path(__file__).parent.parent.parent
        
        if args.environment == 'production':
            config = create_production_config(base_dir)
        else:
            config = create_development_config(base_dir)
        
        config.save_to_file(args.output)
        print(f"[OK] Configuración generada: {args.output}")
    
    def _analyze_single_file(self, args: argparse.Namespace):
        """Analiza un archivo específico."""
        if not args.file_path.exists():
            print(f"[ERROR] Archivo no encontrado: {args.file_path}")
            sys.exit(1)
        
        print(f"[SEARCH] Analizando archivo: {args.file_path}")
        
        # Configurar componentes
        logger = self._create_logger()
        feature_extractor = FileFeatureExtractor()
        ml_adapter = self._create_ml_adapter()
        
        # Crear caso de uso
        file_analysis = FileAnalysisUseCase(feature_extractor, ml_adapter, logger)
        
        # Analizar archivo
        result = file_analysis.analyze_file(args.file_path)
        
        if result:
            self._print_analysis_result(result)
        else:
            print("[ERROR] No se pudo analizar el archivo")
    
    def _scan_directory_once(self, args: argparse.Namespace):
        """Escanea directorio una sola vez."""
        directory = self.config.monitoring.watch_directory
        print(f"[SEARCH] Escaneando directorio: {directory}")
        
        # Configurar componentes
        logger = self._create_logger()
        feature_extractor = FileFeatureExtractor()
        ml_adapter = self._create_ml_adapter()
        alert_handler = self._create_alert_handler()
        
        # Crear casos de uso
        file_analysis = FileAnalysisUseCase(feature_extractor, ml_adapter, logger)
        directory_monitoring = DirectoryMonitoringUseCase(file_analysis, alert_handler, logger)
        
        # Crear sesión y escanear
        session = MonitoringSession(directory)
        results = directory_monitoring.scan_directory_once(session)
        
        # Mostrar resultados
        print(f"\n[DATA] Resultados del escaneo:")
        print(f"  • Archivos escaneados: {session.files_scanned}")
        print(f"  • Amenazas detectadas: {session.threats_detected}")
        print(f"  • Alertas generadas: {session.alerts_generated}")
        
        # Mostrar amenazas encontradas
        threats = [r for r in results if r.is_threat()]
        if threats:
            print(f"\n[WARNING]  Amenazas detectadas:")
            for threat in threats:
                print(f"  • {threat.file_path.name} - {threat.confidence:.2%}")
    
    def _monitor_continuously(self, args: argparse.Namespace):
        """Monitoreo continuo."""
        directory = self.config.monitoring.watch_directory
        interval = self.config.monitoring.scan_interval
        duration = getattr(args, 'duration', None)
        
        print(f"[SYNC] Iniciando monitoreo continuo...")
        print(f"  • Directorio: {directory}")
        print(f"  • Intervalo: {interval} segundos")
        print(f"  • Duración: {'indefinida' if not duration else f'{duration} segundos'}")
        print("  • Presiona Ctrl+C para detener\n")
        
        # Configurar componentes
        logger = self._create_logger()
        feature_extractor = FileFeatureExtractor()
        ml_adapter = self._create_ml_adapter()
        alert_handler = self._create_alert_handler()
        process_monitor = SystemProcessMonitor()
        
        # Crear casos de uso
        file_analysis = FileAnalysisUseCase(feature_extractor, ml_adapter, logger)
        directory_monitoring = DirectoryMonitoringUseCase(file_analysis, alert_handler, logger)
        process_monitoring = ProcessMonitoringUseCase(
            process_monitor, file_analysis, alert_handler, logger
        )
        
        # Crear sesión
        session = MonitoringSession(directory)
        start_time = time.time()
        
        try:
            while True:
                # Verificar duración
                if duration and (time.time() - start_time) >= duration:
                    break
                
                # Escanear archivos
                if self.config.monitoring.monitor_files:
                    directory_monitoring.scan_directory_once(session)
                
                # Escanear procesos (menos frecuente)
                if self.config.monitoring.monitor_processes and session.files_scanned % 5 == 0:
                    process_monitoring.scan_running_processes()
                
                # Esperar antes del siguiente escaneo
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoreo detenido por el usuario")
        
        # Mostrar estadísticas finales
        print(f"\n[DATA] Estadísticas de la sesión:")
        stats = session.get_stats()
        print(f"  • Duración: {stats['duration']:.1f} segundos")
        print(f"  • Archivos escaneados: {stats['files_scanned']}")
        print(f"  • Amenazas detectadas: {stats['threats_detected']}")
        print(f"  • Alertas generadas: {stats['alerts_generated']}")
    
    def _scan_processes(self):
        """Escanea procesos en ejecución."""
        print("[SEARCH] Escaneando procesos en ejecución...")
        
        # Configurar componentes
        logger = self._create_logger()
        feature_extractor = FileFeatureExtractor()
        ml_adapter = self._create_ml_adapter()
        alert_handler = self._create_alert_handler()
        process_monitor = SystemProcessMonitor()
        
        # Crear casos de uso
        file_analysis = FileAnalysisUseCase(feature_extractor, ml_adapter, logger)
        process_monitoring = ProcessMonitoringUseCase(
            process_monitor, file_analysis, alert_handler, logger
        )
        
        # Escanear procesos
        results = process_monitoring.scan_running_processes()
        
        print(f"\n[DATA] Resultados del escaneo de procesos:")
        print(f"  • Procesos analizados: {len(process_monitor.get_running_processes())}")
        print(f"  • Amenazas detectadas: {len(results)}")
        
        if results:
            print(f"\n[WARNING]  Procesos sospechosos:")
            for result in results:
                print(f"  • {result.file_path.name} - {result.confidence:.2%}")
    
    def _create_logger(self):
        """Crea logger basado en configuración."""
        loggers = []
        
        if self.config.logging.console_output:
            console_logger = ConsoleLogger(verbose=(self.config.logging.log_level == "DEBUG"))
            loggers.append(console_logger)
        
        if self.config.logging.file_output:
            log_path = self.config.logging.log_directory / "antikeylogger.log"
            file_logger = FileSystemLogger(log_path)
            loggers.append(file_logger)
        
        return CompositeLogger(loggers)
    
    def _create_alert_handler(self):
        """Crea manejador de alertas basado en configuración."""
        handlers = []
        
        if self.config.alerts.console_alerts:
            console_handler = ConsoleAlertHandler()
            handlers.append(console_handler)
        
        if self.config.alerts.file_alerts:
            alert_path = self.config.alerts.alert_directory / "alerts.log"
            detail_path = self.config.alerts.alert_directory / "alerts_detailed.json"
            file_handler = FileSystemAlertHandler(alert_path, detail_path)
            handlers.append(file_handler)
        
        return CompositeAlertHandler(handlers)
    
    def _create_ml_adapter(self):
        """Crea adaptador de ML basado en configuración."""
        model_adapter = create_model_adapter(
            self.config.model.model_path,
            self.config.model.features_path,
            self.config.model.labels_path
        )
        
        # Cargar el modelo
        success = model_adapter.load_model(self.config.model.model_path)
        if not success:
            raise RuntimeError(f"No se pudo cargar el modelo: {self.config.model.model_path}")
        
        return model_adapter
    
    def _print_analysis_result(self, result):
        """Imprime resultado de análisis."""
        print(f"\n[DATA] Resultado del análisis:")
        print(f"  • Archivo: {result.file_path}")
        print(f"  • Nivel de amenaza: {result.threat_level.value.upper()}")
        print(f"  • Confianza: {result.confidence:.2%}")
        print(f"  • Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result.timestamp))}")
        
        if result.is_threat():
            print(f"  [WARNING]  ARCHIVO MARCADO COMO AMENAZA")
        else:
            print(f"  [OK] Archivo parece benigno")
        
        if result.details:
            print(f"  • Detalles adicionales: {json.dumps(result.details, indent=2)}")


def main():
    """Punto de entrada principal."""
    cli = AntiKeyloggerCLI()
    cli.run()


if __name__ == '__main__':
    main()