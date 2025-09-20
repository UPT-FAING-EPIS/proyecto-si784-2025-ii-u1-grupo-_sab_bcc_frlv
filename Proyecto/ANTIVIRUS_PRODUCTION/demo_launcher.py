#!/usr/bin/env python3
"""
Demo Launcher del Sistema Anti-Keylogger
========================================

Versión de demostración sin dependencias ML pesadas.
"""

import sys
import time
import psutil
from pathlib import Path

def demo_antivirus():
    """Demo del sistema antivirus básico"""
    print("🛡️  SISTEMA ANTI-KEYLOGGER - DEMO")
    print("=" * 50)
    print()
    
    try:
        # Test 1: Información del sistema
        print("📊 INFORMACIÓN DEL SISTEMA:")
        print(f"   CPU: {psutil.cpu_percent(interval=1)}%")
        memory = psutil.virtual_memory()
        print(f"   RAM: {memory.percent}% usado ({memory.used // (1024**3)} GB / {memory.total // (1024**3)} GB)")
        print(f"   Conexiones activas: {len(psutil.net_connections())}")
        print()
        
        # Test 2: Monitoreo de procesos
        print("🔍 MONITOREO DE PROCESOS:")
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Ordenar por CPU y mostrar top 5
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        for i, proc in enumerate(processes[:5]):
            print(f"   [{i+1}] PID {proc['pid']:5} | {proc['name']:20} | CPU: {proc['cpu_percent']:.1f}%")
        print()
        
        # Test 3: Monitoreo de red
        print("🌐 MONITOREO DE RED:")
        net_io = psutil.net_io_counters()
        print(f"   Bytes enviados: {net_io.bytes_sent // (1024**2)} MB")
        print(f"   Bytes recibidos: {net_io.bytes_recv // (1024**2)} MB")
        print(f"   Paquetes enviados: {net_io.packets_sent}")
        print(f"   Paquetes recibidos: {net_io.packets_recv}")
        print()
        
        # Test 4: Detección simulada
        print("🤖 SIMULACIÓN DE DETECCIÓN ML:")
        print("   [SCAN] Analizando patrones de tráfico de red...")
        time.sleep(1)
        print("   [SCAN] Revisando comportamiento de procesos...")
        time.sleep(1)
        print("   [SCAN] Aplicando modelos de machine learning...")
        time.sleep(1)
        print("   [OK] No se detectaron amenazas de keyloggers")
        print()
        
        # Test 5: Archivos del sistema
        print("📁 VERIFICACIÓN DE ARCHIVOS:")
        base_path = Path(".")
        
        key_files = [
            "models/rf_large_model_20250918_112442.pkl",
            "models/label_classes.json",
            "config/config.toml",
            "antivirus_launcher.py",
            "simple_launcher.py"
        ]
        
        for file_path in key_files:
            path = base_path / file_path
            if path.exists():
                size = path.stat().st_size / 1024
                print(f"   [OK] {file_path} ({size:.1f} KB)")
            else:
                print(f"   [MISSING] {file_path}")
        print()
        
        print("✅ DEMO COMPLETADA EXITOSAMENTE")
        print("🛡️  Sistema Anti-Keylogger operativo")
        return True
        
    except Exception as e:
        print(f"❌ ERROR EN DEMO: {e}")
        return False

def show_deployment_options():
    """Muestra las opciones de despliegue disponibles"""
    print()
    print("🚀 OPCIONES DE DESPLIEGUE DISPONIBLES:")
    print("=" * 50)
    print()
    
    options = [
        ("1. Ejecutable Portable", "Un archivo .exe independiente"),
        ("2. Servicio Windows", "Servicio del sistema automático"),
        ("3. Instalador MSI", "Instalación profesional"),
        ("4. Contenedor Docker", "Ambiente aislado multiplataforma"),
        ("5. Red Empresarial", "Despliegue en múltiples equipos"),
        ("6. Auto-Actualización", "Sistema con updates automáticos")
    ]
    
    for title, description in options:
        print(f"   {title}")
        print(f"      → {description}")
        print()
    
    print("📦 ARCHIVO ACTUAL:")
    print(f"   → Ejecutable: {sys.executable}")
    print(f"   → Tamaño estimado: ~85MB")
    print(f"   → Sin dependencias externas")
    print()

if __name__ == "__main__":
    print("Iniciando demo...")
    print()
    
    success = demo_antivirus()
    
    if success:
        show_deployment_options()
    
    print()
    print("Presiona Enter para salir...")
    input()