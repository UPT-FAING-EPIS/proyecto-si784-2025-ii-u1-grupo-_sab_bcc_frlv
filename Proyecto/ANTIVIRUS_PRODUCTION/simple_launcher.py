#!/usr/bin/env python3
"""
Launcher Simple del Sistema Anti-Keylogger
==========================================

Versión simplificada para pruebas iniciales.
"""

import sys
import time
from pathlib import Path

def test_basic_system():
    """Prueba básica del sistema"""
    print("=== SISTEMA ANTI-KEYLOGGER - PRUEBA BÁSICA ===")
    print()
    
    try:
        # Test 1: Importar módulos básicos
        print("1. Probando imports básicos...")
        from antivirus.monitors.network_monitor import NetworkTrafficMonitor
        from antivirus.monitors.process_monitor import ProcessBehaviorMonitor
        from antivirus.detectors.ml_detector import MLKeyloggerDetector
        print("   [OK] Imports exitosos")
        
        # Test 2: Inicializar componentes
        print("\n2. Inicializando componentes...")
        
        # ML Detector
        ml_detector = MLKeyloggerDetector()
        print(f"   [OK] ML Detector: {'Cargado' if ml_detector.is_loaded() else 'Sin modelos'}")
        
        # Network Monitor
        net_monitor = NetworkTrafficMonitor()
        print("   [OK] Network Monitor inicializado")
        
        # Process Monitor
        proc_monitor = ProcessBehaviorMonitor()
        print("   [OK] Process Monitor inicializado")
        
        # Test 3: Estadísticas básicas
        print("\n3. Obteniendo estadísticas del sistema...")
        
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        print(f"   CPU: {cpu_percent}%")
        print(f"   RAM: {memory.percent}% usado")
        print(f"   Conexiones activas: {len(psutil.net_connections())}")
        
        # Test 4: Estadísticas del ML
        if ml_detector.is_loaded():
            stats = ml_detector.get_stats()
            print(f"\n4. Estadísticas ML:")
            print(f"   Predicciones realizadas: {stats.get('predictions_made', 0)}")
            print(f"   Tiempo promedio: {stats.get('avg_prediction_time', 0):.4f}s")
            print(f"   Threshold confianza: {stats.get('confidence_threshold', 0)}")
            print(f"   Tipo de modelo: {stats.get('model_type', 'N/A')}")
            print(f"   Features disponibles: {stats.get('feature_count', 0)}")
            print(f"   Clases: {stats.get('label_classes', [])}")
        
        print("\n[OK] SISTEMA FUNCIONANDO CORRECTAMENTE")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Error de import: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        return False

def show_info():
    """Muestra información del sistema"""
    print("=== INFORMACIÓN DEL SISTEMA ANTI-KEYLOGGER ===")
    print()
    
    print("[FILE] Estructura del proyecto:")
    base_path = Path(".")
    
    key_paths = [
        "antivirus/core/engine.py",
        "antivirus/detectors/ml_detector.py", 
        "antivirus/monitors/network_monitor.py",
        "models/development/modelo_keylogger_from_datos.pkl",
        "models/development/modelo_keylogger_from_datos.onnx",
        "logs/",
        "quarantine/",
        "antivirus/config.toml"
    ]
    
    for path_str in key_paths:
        path = base_path / path_str
        if path.exists():
            if path.is_file():
                size = path.stat().st_size / 1024
                print(f"   [OK] {path_str} ({size:.1f} KB)")
            else:
                print(f"   [OK] {path_str} (directorio)")
        else:
            print(f"   [ERROR] {path_str} (faltante)")
    
    print("\n[FIX] Dependencias críticas:")
    critical_deps = ['psutil', 'numpy', 'scikit-learn', 'onnxruntime', 'joblib', 'toml']
    
    for dep in critical_deps:
        try:
            __import__(dep)
            print(f"   [OK] {dep}")
        except ImportError:
            print(f"   [ERROR] {dep}")
    
    print("\n[ML] Estado de modelos ML:")
    try:
        from antivirus.detectors.ml_detector import MLKeyloggerDetector
        detector = MLKeyloggerDetector()
        
        if detector.is_loaded():
            print("   [OK] Modelos ML cargados correctamente")
            stats = detector.get_stats()
            for key, value in stats.items():
                print(f"      {key}: {value}")
        else:
            print("   [WARNING] Modelos ML no disponibles")
            
    except Exception as e:
        print(f"   [ERROR] Error cargando ML: {e}")

def monitor_basic():
    """Monitoreo básico por 30 segundos"""
    print("=== MONITOREO BÁSICO (30 segundos) ===")
    print("Presiona Ctrl+C para detener")
    print()
    
    try:
        from antivirus.monitors.network_monitor import NetworkTrafficMonitor
        import psutil
        
        start_time = time.time()
        
        while time.time() - start_time < 30:
            # Estadísticas básicas cada 5 segundos
            connections = len(psutil.net_connections())
            processes = len(psutil.pids())
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            
            print(f"[{time.strftime('%H:%M:%S')}] Conexiones: {connections}, Procesos: {processes}, CPU: {cpu}%, RAM: {memory}%")
            
            time.sleep(4)  # Ya dormimos 1 segundo en cpu_percent
        
        print("\n[OK] Monitoreo completado")
        
    except KeyboardInterrupt:
        print("\n🛑 Monitoreo detenido por usuario")
    except Exception as e:
        print(f"\n[ERROR] Error en monitoreo: {e}")

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "--test":
            success = test_basic_system()
            sys.exit(0 if success else 1)
            
        elif command == "--info":
            show_info()
            
        elif command == "--monitor":
            monitor_basic()
            
        elif command == "--help":
            print("Sistema Anti-Keylogger - Launcher Simple")
            print()
            print("Uso: python simple_launcher.py [comando]")
            print()
            print("Comandos disponibles:")
            print("  --test      Ejecuta pruebas básicas del sistema")
            print("  --info      Muestra información del sistema")
            print("  --monitor   Inicia monitoreo básico por 30 segundos")
            print("  --help      Muestra esta ayuda")
            print()
            print("Sin argumentos: ejecuta prueba básica")
            
        else:
            print(f"[ERROR] Comando desconocido: {command}")
            print("Use --help para ver comandos disponibles")
            sys.exit(1)
    else:
        # Sin argumentos, ejecutar prueba básica
        success = test_basic_system()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()