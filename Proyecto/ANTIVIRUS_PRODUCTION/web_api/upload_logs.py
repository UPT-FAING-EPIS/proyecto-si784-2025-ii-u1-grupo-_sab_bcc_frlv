#!/usr/bin/env python3
"""
Script para subir logs automáticamente a Railway
================================================
"""

import requests
import json
import time
from pathlib import Path
import threading

class LogUploader:
    def __init__(self, railway_url="https://tu-app.railway.app"):
        self.railway_url = railway_url
        self.upload_endpoint = f"{railway_url}/api/upload-logs"
        
    def upload_logs(self):
        """Subir logs actuales a Railway"""
        try:
            # Leer logs locales
            security_log = Path("../security_events.log")
            antivirus_log = Path("../antivirus.log")
            
            logs_data = {
                "security_events": [],
                "antivirus": [],
                "timestamp": time.time()
            }
            
            # Leer security_events.log
            if security_log.exists():
                with open(security_log, 'r', encoding='utf-8', errors='ignore') as f:
                    logs_data["security_events"] = f.readlines()
            
            # Leer antivirus.log
            if antivirus_log.exists():
                with open(antivirus_log, 'r', encoding='utf-8', errors='ignore') as f:
                    logs_data["antivirus"] = f.readlines()
            
            # Enviar a Railway
            response = requests.post(
                self.upload_endpoint,
                json=logs_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Logs subidos exitosamente - {len(logs_data['security_events'])} eventos")
                return True
            else:
                print(f"❌ Error subiendo logs: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def auto_upload_daemon(self, interval=300):  # 5 minutos
        """Daemon que sube logs automáticamente cada X segundos"""
        while True:
            print(f"🔄 Subiendo logs automáticamente...")
            self.upload_logs()
            time.sleep(interval)

def main():
    uploader = LogUploader()
    
    # Subida manual
    print("📤 Subiendo logs manualmente...")
    uploader.upload_logs()
    
    # Opción para daemon automático
    auto = input("\n¿Activar subida automática cada 5 minutos? (y/n): ")
    if auto.lower() == 'y':
        print("🔄 Iniciando daemon de subida automática...")
        uploader.auto_upload_daemon()

if __name__ == "__main__":
    main()