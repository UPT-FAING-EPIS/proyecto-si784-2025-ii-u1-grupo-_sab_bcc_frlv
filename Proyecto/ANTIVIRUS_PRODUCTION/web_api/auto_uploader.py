#!/usr/bin/env python3
"""
Auto-uploader de logs del Antivirus a Railway
===========================================
Este script ejecuta el antivirus, detecta nuevos logs y los sube automáticamente
"""

import requests
import json
import time
import subprocess
import threading
from pathlib import Path
import schedule
from datetime import datetime

class AntivirusAutoUploader:
    def __init__(self, railway_url="https://tu-app.railway.app"):
        self.railway_url = railway_url
        self.upload_endpoint = f"{railway_url}/api/upload-logs"
        self.antivirus_dir = Path("../")
        self.last_upload_time = 0
        
    def run_antivirus_scan(self):
        """Ejecutar un scan del antivirus"""
        try:
            print("🔍 Ejecutando scan del antivirus...")
            result = subprocess.run([
                "python", 
                str(self.antivirus_dir / "demo_launcher.py")
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ Scan completado exitosamente")
                return True
            else:
                print(f"❌ Error en scan: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Scan timeout - continuando con logs existentes")
            return True
        except Exception as e:
            print(f"❌ Error ejecutando antivirus: {e}")
            return False
    
    def check_for_new_logs(self):
        """Verificar si hay logs nuevos desde la última subida"""
        try:
            security_log = self.antivirus_dir / "security_events.log"
            
            if not security_log.exists():
                return False
                
            # Verificar timestamp del archivo
            file_time = security_log.stat().st_mtime
            return file_time > self.last_upload_time
            
        except Exception as e:
            print(f"❌ Error verificando logs: {e}")
            return False
    
    def upload_logs(self):
        """Subir logs actuales a Railway"""
        try:
            security_log = self.antivirus_dir / "security_events.log"
            antivirus_log = self.antivirus_dir / "antivirus.log"
            
            logs_data = {
                "security_events": [],
                "antivirus": [],
                "timestamp": time.time(),
                "upload_source": "auto_uploader",
                "upload_time": datetime.now().isoformat()
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
                events_count = len(logs_data['security_events'])
                print(f"✅ Logs subidos: {events_count} eventos a Railway")
                self.last_upload_time = time.time()
                return True
            else:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def scan_and_upload(self):
        """Proceso completo: scan + upload"""
        print(f"\n🚀 {datetime.now().strftime('%H:%M:%S')} - Iniciando proceso automático...")
        
        # 1. Ejecutar antivirus
        if self.run_antivirus_scan():
            # 2. Esperar un poco para que se escriban los logs
            time.sleep(5)
            
            # 3. Verificar si hay logs nuevos
            if self.check_for_new_logs():
                # 4. Subir logs
                if self.upload_logs():
                    print("✅ Proceso completado exitosamente")
                else:
                    print("❌ Error subiendo logs")
            else:
                print("ℹ️  No hay logs nuevos para subir")
        else:
            print("❌ Error en el scan del antivirus")
    
    def start_auto_mode(self, interval_minutes=10):
        """Iniciar modo automático con intervalos"""
        print(f"🔄 Iniciando modo automático cada {interval_minutes} minutos")
        print("⚡ Ctrl+C para detener")
        
        # Configurar horarios
        schedule.every(interval_minutes).minutes.do(self.scan_and_upload)
        
        # Ejecutar una vez inmediatamente
        self.scan_and_upload()
        
        # Loop principal
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Verificar cada 30 segundos
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo auto-uploader...")

def main():
    print("🛡️  ANTIVIRUS AUTO-UPLOADER PARA RAILWAY")
    print("=" * 50)
    
    # Obtener URL de Railway
    railway_url = input("📡 URL de Railway (enter para usar localhost): ").strip()
    if not railway_url:
        railway_url = "http://localhost:8000"
    
    uploader = AntivirusAutoUploader(railway_url)
    
    print("\n📋 OPCIONES:")
    print("1. Subir logs una sola vez")
    print("2. Ejecutar scan + subir logs")
    print("3. Modo automático (cada 10 minutos)")
    print("4. Modo automático personalizado")
    
    option = input("\n🔢 Selecciona una opción (1-4): ").strip()
    
    if option == "1":
        print("\n📤 Subiendo logs actuales...")
        uploader.upload_logs()
        
    elif option == "2":
        print("\n🔍 Ejecutando scan y subiendo logs...")
        uploader.scan_and_upload()
        
    elif option == "3":
        uploader.start_auto_mode(10)
        
    elif option == "4":
        try:
            minutes = int(input("⏱️  Intervalo en minutos: "))
            uploader.start_auto_mode(minutes)
        except ValueError:
            print("❌ Intervalo inválido")
    
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    # Instalar dependencias si no están disponibles
    try:
        import schedule
    except ImportError:
        print("📦 Instalando dependencia schedule...")
        subprocess.run(["pip", "install", "schedule"], check=True)
        import schedule
    
    main()