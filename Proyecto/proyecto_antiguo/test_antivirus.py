#!/usr/bin/env python3
"""
Sistema de Pruebas del Anti-Keylogger
=====================================

Suite de pruebas para verificar el funcionamiento
de todos los componentes del sistema antivirus.
"""

import os
import sys
import time
import json
import tempfile
import threading
from pathlib import Path
from datetime import datetime


class AntivirusTestSuite:
    """Suite de pruebas del sistema antivirus"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'start_time': None,
            'end_time': None,
            'details': []
        }
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas disponibles"""
        print("🧪 SISTEMA DE PRUEBAS DEL ANTI-KEYLOGGER")
        print("=" * 50)
        
        self.results['start_time'] = datetime.now()
        
        try:
            # Pruebas de imports y módulos
            self._test_imports()
            
            # Pruebas de modelos ML
            self._test_ml_models()
            
            # Pruebas de monitores
            self._test_monitors()
            
            # Pruebas de detectores
            self._test_detectors()
            
            # Pruebas de utilidades
            self._test_utilities()
            
            # Pruebas de configuración
            self._test_configuration()
            
            # Pruebas de integración
            self._test_integration()
            
            # Pruebas de rendimiento
            self._test_performance()
            
        except Exception as e:
            self._record_test("FATAL_ERROR", False, f"Error fatal: {e}")
        
        finally:
            self.results['end_time'] = datetime.now()
            self._show_results()
    
    def _test_imports(self):
        """Prueba la importación de todos los módulos"""
        print("\n[PACKAGE] PRUEBAS DE IMPORTACIÓN")
        print("-" * 30)
        
        modules = [
            ('antivirus', 'Módulo principal'),
            ('antivirus.core.engine', 'Motor principal'),
            ('antivirus.monitors.network_monitor', 'Monitor de red'),
            ('antivirus.monitors.process_monitor', 'Monitor de procesos'),
            ('antivirus.monitors.file_monitor', 'Monitor de archivos'),
            ('antivirus.detectors.ml_detector', 'Detector ML'),
            ('antivirus.detectors.behavior_detector', 'Detector de comportamiento'),
            ('antivirus.detectors.network_detector', 'Detector de red'),
            ('antivirus.utils.file_scanner', 'Escáner de archivos'),
        ]
        
        for module_name, description in modules:
            try:
                __import__(module_name)
                self._record_test(f"IMPORT_{module_name}", True, f"{description} importado correctamente")
            except ImportError as e:
                self._record_test(f"IMPORT_{module_name}", False, f"Error importando {description}: {e}")
            except Exception as e:
                self._record_test(f"IMPORT_{module_name}", False, f"Error inesperado en {description}: {e}")
    
    def _test_ml_models(self):
        """Prueba la carga y funcionamiento de modelos ML"""
        print("\n[ML] PRUEBAS DE MODELOS ML")
        print("-" * 30)
        
        try:
            from antivirus.detectors.ml_detector import MLKeyloggerDetector
            
            # Test 1: Inicialización
            detector = MLKeyloggerDetector()
            self._record_test("ML_INIT", True, "ML Detector inicializado")
            
            # Test 2: Verificar carga de modelos
            if detector.is_loaded():
                self._record_test("ML_LOADED", True, "Modelos ML cargados correctamente")
                
                # Test 3: Predicción con datos sintéticos
                test_data = {
                    'connections_count': 5,
                    'data_sent_kb': 10.5,
                    'data_received_kb': 2.3,
                    'unique_destinations': 3,
                    'connection_duration_avg': 45.2
                }
                
                try:
                    prediction = detector.predict_keylogger(test_data)
                    if isinstance(prediction, dict) and 'is_keylogger' in prediction:
                        self._record_test("ML_PREDICTION", True, f"Predicción exitosa: {prediction}")
                    else:
                        self._record_test("ML_PREDICTION", False, "Formato de predicción inválido")
                except Exception as e:
                    self._record_test("ML_PREDICTION", False, f"Error en predicción: {e}")
                
            else:
                self._record_test("ML_LOADED", False, "No se pudieron cargar los modelos ML")
                
        except ImportError as e:
            self._record_test("ML_IMPORT", False, f"Error importando ML detector: {e}")
        except Exception as e:
            self._record_test("ML_ERROR", False, f"Error en pruebas ML: {e}")
    
    def _test_monitors(self):
        """Prueba el funcionamiento de los monitores"""
        print("\n📡 PRUEBAS DE MONITORES")
        print("-" * 30)
        
        # Test Network Monitor
        try:
            from antivirus.monitors.network_monitor import NetworkTrafficMonitor
            
            net_monitor = NetworkTrafficMonitor()
            self._record_test("NET_MONITOR_INIT", True, "Network Monitor inicializado")
            
            # Verificar que puede obtener conexiones
            connections = net_monitor._get_network_connections()
            if isinstance(connections, list):
                self._record_test("NET_MONITOR_DATA", True, f"Obtuvo {len(connections)} conexiones")
            else:
                self._record_test("NET_MONITOR_DATA", False, "No pudo obtener conexiones de red")
                
        except Exception as e:
            self._record_test("NET_MONITOR_ERROR", False, f"Error en Network Monitor: {e}")
        
        # Test Process Monitor
        try:
            from antivirus.monitors.process_monitor import ProcessBehaviorMonitor
            
            proc_monitor = ProcessBehaviorMonitor()
            self._record_test("PROC_MONITOR_INIT", True, "Process Monitor inicializado")
            
            # Verificar que puede obtener procesos
            processes = proc_monitor._get_running_processes()
            if isinstance(processes, list) and len(processes) > 0:
                self._record_test("PROC_MONITOR_DATA", True, f"Detectó {len(processes)} procesos")
            else:
                self._record_test("PROC_MONITOR_DATA", False, "No pudo obtener lista de procesos")
                
        except Exception as e:
            self._record_test("PROC_MONITOR_ERROR", False, f"Error en Process Monitor: {e}")
        
        # Test File Monitor
        try:
            from antivirus.monitors.file_monitor import FileSystemMonitor
            
            file_monitor = FileSystemMonitor()
            self._record_test("FILE_MONITOR_INIT", True, "File Monitor inicializado")
            
        except Exception as e:
            self._record_test("FILE_MONITOR_ERROR", False, f"Error en File Monitor: {e}")
    
    def _test_detectors(self):
        """Prueba el funcionamiento de los detectores"""
        print("\n[SEARCH] PRUEBAS DE DETECTORES")
        print("-" * 30)
        
        # Test Behavior Detector
        try:
            from antivirus.detectors.behavior_detector import BehaviorAnalysisDetector
            
            behavior_detector = BehaviorAnalysisDetector()
            self._record_test("BEHAVIOR_DETECTOR_INIT", True, "Behavior Detector inicializado")
            
        except Exception as e:
            self._record_test("BEHAVIOR_DETECTOR_ERROR", False, f"Error en Behavior Detector: {e}")
        
        # Test Network Pattern Detector
        try:
            from antivirus.detectors.network_detector import NetworkPatternDetector
            
            network_detector = NetworkPatternDetector()
            self._record_test("NETWORK_DETECTOR_INIT", True, "Network Pattern Detector inicializado")
            
        except Exception as e:
            self._record_test("NETWORK_DETECTOR_ERROR", False, f"Error en Network Pattern Detector: {e}")
    
    def _test_utilities(self):
        """Prueba las utilidades del sistema"""
        print("\n[TOOL] PRUEBAS DE UTILIDADES")
        print("-" * 30)
        
        try:
            from antivirus.utils.file_scanner import FileScanner
            
            scanner = FileScanner()
            self._record_test("FILE_SCANNER_INIT", True, "File Scanner inicializado")
            
            # Test con archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                tmp.write("Test content for scanning")
                tmp_path = tmp.name
            
            try:
                scan_result = scanner.scan_file(tmp_path)
                if isinstance(scan_result, dict):
                    self._record_test("FILE_SCANNER_SCAN", True, "Escaneo de archivo exitoso")
                else:
                    self._record_test("FILE_SCANNER_SCAN", False, "Formato de resultado inválido")
            finally:
                os.unlink(tmp_path)
                
        except Exception as e:
            self._record_test("FILE_SCANNER_ERROR", False, f"Error en File Scanner: {e}")
    
    def _test_configuration(self):
        """Prueba la configuración del sistema"""
        print("\n[PROC] PRUEBAS DE CONFIGURACIÓN")
        print("-" * 30)
        
        config_path = self.root_dir / "antivirus" / "config.toml"
        
        if config_path.exists():
            try:
                import toml
                config = toml.load(config_path)
                
                # Verificar secciones principales
                required_sections = ['monitoring', 'detection', 'logging', 'security']
                for section in required_sections:
                    if section in config:
                        self._record_test(f"CONFIG_{section.upper()}", True, f"Sección {section} presente")
                    else:
                        self._record_test(f"CONFIG_{section.upper()}", False, f"Sección {section} faltante")
                
            except ImportError:
                self._record_test("CONFIG_TOML", False, "Módulo toml no disponible")
            except Exception as e:
                self._record_test("CONFIG_PARSE", False, f"Error parseando configuración: {e}")
        else:
            self._record_test("CONFIG_FILE", False, "Archivo de configuración no encontrado")
    
    def _test_integration(self):
        """Prueba la integración entre componentes"""
        print("\n🔗 PRUEBAS DE INTEGRACIÓN")
        print("-" * 30)
        
        try:
            from antivirus.core.engine import AntiKeyloggerEngine
            
            # Test 1: Inicialización del motor
            engine = AntiKeyloggerEngine()
            self._record_test("ENGINE_INIT", True, "Motor principal inicializado")
            
            # Test 2: Verificar componentes cargados
            if hasattr(engine, 'ml_detector') and engine.ml_detector:
                self._record_test("ENGINE_ML", True, "ML Detector integrado en motor")
            else:
                self._record_test("ENGINE_ML", False, "ML Detector no integrado")
            
            # Test 3: Verificar monitores
            monitor_count = 0
            if hasattr(engine, 'network_monitor'): monitor_count += 1
            if hasattr(engine, 'process_monitor'): monitor_count += 1
            if hasattr(engine, 'file_monitor'): monitor_count += 1
            
            if monitor_count >= 3:
                self._record_test("ENGINE_MONITORS", True, f"{monitor_count} monitores integrados")
            else:
                self._record_test("ENGINE_MONITORS", False, f"Solo {monitor_count} monitores integrados")
            
        except Exception as e:
            self._record_test("ENGINE_ERROR", False, f"Error en motor principal: {e}")
    
    def _test_performance(self):
        """Prueba el rendimiento básico"""
        print("\n⚡ PRUEBAS DE RENDIMIENTO")
        print("-" * 30)
        
        try:
            from antivirus.detectors.ml_detector import MLKeyloggerDetector
            
            detector = MLKeyloggerDetector()
            
            if detector.is_loaded():
                # Test de velocidad de predicción
                test_data = {
                    'connections_count': 5,
                    'data_sent_kb': 10.5,
                    'data_received_kb': 2.3,
                    'unique_destinations': 3,
                    'connection_duration_avg': 45.2
                }
                
                start_time = time.time()
                predictions = 0
                
                # Ejecutar predicciones por 1 segundo
                while time.time() - start_time < 1.0:
                    detector.predict_keylogger(test_data)
                    predictions += 1
                
                if predictions > 10:  # Al menos 10 predicciones por segundo
                    self._record_test("PERF_ML_SPEED", True, f"{predictions} predicciones/segundo")
                else:
                    self._record_test("PERF_ML_SPEED", False, f"Solo {predictions} predicciones/segundo")
            else:
                self._record_test("PERF_ML_SPEED", False, "No se pueden hacer pruebas de rendimiento sin modelos")
                
        except Exception as e:
            self._record_test("PERF_ERROR", False, f"Error en pruebas de rendimiento: {e}")
    
    def _record_test(self, test_name, passed, description):
        """Registra el resultado de una prueba"""
        self.results['total_tests'] += 1
        
        if passed:
            self.results['passed'] += 1
            status = "[OK]"
        else:
            self.results['failed'] += 1
            status = "[ERROR]"
        
        self.results['details'].append({
            'name': test_name,
            'passed': passed,
            'description': description
        })
        
        print(f"{status} {description}")
    
    def _show_results(self):
        """Muestra el resumen de resultados"""
        duration = (self.results['end_time'] - self.results['start_time']).total_seconds()
        
        print("\n" + "=" * 50)
        print("[DATA] RESUMEN DE PRUEBAS")
        print("=" * 50)
        
        print(f"Total de pruebas: {self.results['total_tests']}")
        print(f"Exitosas: {self.results['passed']} [OK]")
        print(f"Fallidas: {self.results['failed']} [ERROR]")
        print(f"Duración: {duration:.2f} segundos")
        
        # Porcentaje de éxito
        if self.results['total_tests'] > 0:
            success_rate = (self.results['passed'] / self.results['total_tests']) * 100
            print(f"Tasa de éxito: {success_rate:.1f}%")
        
        # Estado general
        if self.results['failed'] == 0:
            print("\n[SUCCESS] TODAS LAS PRUEBAS PASARON")
            exit_code = 0
        elif self.results['passed'] > self.results['failed']:
            print("\n[WARNING] ALGUNAS PRUEBAS FALLARON")
            exit_code = 1
        else:
            print("\n[ERROR] MUCHAS PRUEBAS FALLARON")
            exit_code = 2
        
        # Guardar resultados
        self._save_results()
        
        # Recomendar siguientes pasos
        if self.results['failed'] > 0:
            print("\n[FIX] SIGUIENTES PASOS:")
            print("1. Revisar errores específicos arriba")
            print("2. Verificar instalación de dependencias")
            print("3. Ejecutar entrenamiento de modelos si faltan")
            print("4. Re-ejecutar pruebas")
        
        sys.exit(exit_code)
    
    def _save_results(self):
        """Guarda los resultados en un archivo JSON"""
        try:
            results_dir = self.root_dir / "logs"
            results_dir.mkdir(exist_ok=True)
            
            results_file = results_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Convertir datetime a string para JSON
            results_copy = self.results.copy()
            results_copy['start_time'] = self.results['start_time'].isoformat()
            results_copy['end_time'] = self.results['end_time'].isoformat()
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results_copy, f, indent=2, ensure_ascii=False)
            
            print(f"\n[SAVE] Resultados guardados en: {results_file}")
            
        except Exception as e:
            print(f"\n[WARNING] No se pudieron guardar resultados: {e}")


def main():
    """Función principal"""
    test_suite = AntivirusTestSuite()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()