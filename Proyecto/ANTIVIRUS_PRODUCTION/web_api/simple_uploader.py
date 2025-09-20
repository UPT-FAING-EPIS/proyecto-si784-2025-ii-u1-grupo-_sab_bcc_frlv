#!/usr/bin/env python3
"""
Script simple para subir logs a Railway
======================================
"""

import requests
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# CONFIGURACIÓN
RAILWAY_URL = "https://proyecto-anti-keylogger-production.up.railway.app"  # ⚠️ CAMBIAR POR TU URL DE RAILWAY
UPLOAD_ENDPOINT = f"{RAILWAY_URL}/api/upload-logs"

def upload_logs_to_railway():
    """Subir logs actuales a Railway"""
    try:
        print(f"📤 {datetime.now().strftime('%H:%M:%S')} - Subiendo logs a Railway...")
        
        # Buscar archivos de logs
        security_log = Path("../security_events.log")
        antivirus_log = Path("../antivirus.log")
        
        logs_data = {
            "security_events": [],
            "antivirus": [],
            "timestamp": time.time(),
            "upload_source": "manual_script"
        }
        
        # Leer logs
        events_count = 0
        if security_log.exists():
            with open(security_log, 'r', encoding='utf-8', errors='ignore') as f:
                logs_data["security_events"] = f.readlines()
                events_count = len(logs_data["security_events"])
        
        if antivirus_log.exists():
            with open(antivirus_log, 'r', encoding='utf-8', errors='ignore') as f:
                logs_data["antivirus"] = f.readlines()
        
        # Enviar a Railway
        response = requests.post(
            UPLOAD_ENDPOINT,
            json=logs_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ Logs subidos exitosamente!")
            print(f"   📊 {events_count} eventos de seguridad")
            print(f"   🌐 URL: {RAILWAY_URL}/dashboard")
            return True
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_antivirus_and_upload():
    """Ejecutar antivirus y luego subir logs"""
    try:
        print("🔍 Ejecutando demo del antivirus...")
        
        # Ejecutar antivirus (con timeout)
        result = subprocess.run([
            "python", "../demo_launcher.py"
        ], timeout=60, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Antivirus ejecutado exitosamente")
            
            # Esperar un poco para que se escriban los logs
            time.sleep(3)
            
            # Subir logs
            return upload_logs_to_railway()
        else:
            print(f"❌ Error en antivirus: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout del antivirus - subiendo logs existentes...")
        return upload_logs_to_railway()
    except Exception as e:
        print(f"❌ Error ejecutando antivirus: {e}")
        return False

def main():
    print("🛡️  UPLOADER DE LOGS DEL ANTIVIRUS")
    print("=" * 40)
    print(f"🎯 Destino: {RAILWAY_URL}")
    print()
    
    # Verificar configuración
    if "tu-app.railway.app" in RAILWAY_URL:
        print("⚠️  IMPORTANTE: Debes cambiar RAILWAY_URL por tu URL real")
        print("   Edita este archivo y cambia la línea 11")
        return
    
    print("📋 OPCIONES:")
    print("1. Subir logs actuales")
    print("2. Ejecutar antivirus + subir logs")
    print("3. Loop automático cada 5 minutos")
    
    option = input("\n🔢 Elige una opción (1-3): ").strip()
    
    if option == "1":
        upload_logs_to_railway()
        
    elif option == "2":
        run_antivirus_and_upload()
        
    elif option == "3":
        print("🔄 Iniciando loop automático cada 5 minutos...")
        print("⚡ Presiona Ctrl+C para detener")
        
        try:
            while True:
                run_antivirus_and_upload()
                print(f"😴 Esperando 5 minutos... (próximo: {datetime.now().strftime('%H:%M:%S')})")
                time.sleep(300)  # 5 minutos
        except KeyboardInterrupt:
            print("\n🛑 Detenido por el usuario")
    
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    main()