#!/usr/bin/env python3
"""
Desinstalador del Anti-Keylogger
==============================

Script para desinstalar completamente el Anti-Keylogger del sistema.
Ejecuta: python uninstall_antivirus.py
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess
from datetime import datetime

class AntiKeyloggerUninstaller:
    def __init__(self):
        self.install_dir = Path.home() / "AntiKeylogger"
        self.desktop = Path.home() / "Desktop"
        
        # Colores para consola
        self.GREEN = '\033[92m'
        self.RED = '\033[91m'
        self.YELLOW = '\033[93m'
        self.BLUE = '\033[94m'
        self.END = '\033[0m'
        
        print(f"{self.RED}🗑️  DESINSTALADOR ANTI-KEYLOGGER{self.END}")
        print("=" * 50)
    
    def log(self, message, color=""):
        """Imprime mensaje con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {message}{self.END}")
    
    def success(self, message):
        self.log(f"✅ {message}", self.GREEN)
    
    def error(self, message):
        self.log(f"❌ {message}", self.RED)
    
    def warning(self, message):
        self.log(f"⚠️  {message}", self.YELLOW)
    
    def info(self, message):
        self.log(f"ℹ️  {message}", self.BLUE)
    
    def check_installation(self):
        """Verifica si el antivirus está instalado"""
        if not self.install_dir.exists():
            self.error("Anti-Keylogger no está instalado")
            return False
        
        self.info(f"Instalación encontrada en: {self.install_dir}")
        return True
    
    def stop_processes(self):
        """Intenta detener procesos del antivirus"""
        self.info("Deteniendo procesos del antivirus...")
        
        process_names = [
            "antivirus_launcher.py",
            "simple_launcher.py", 
            "facade_launcher.py",
            "start_antivirus.py"
        ]
        
        try:
            import psutil
            killed_processes = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    
                    for process_name in process_names:
                        if process_name in cmdline:
                            self.warning(f"Deteniendo proceso: {proc.info['name']} (PID: {proc.info['pid']})")
                            proc.terminate()
                            killed_processes += 1
                            break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if killed_processes > 0:
                self.success(f"Detenidos {killed_processes} procesos")
            else:
                self.info("No se encontraron procesos ejecutándose")
                
            return True
            
        except ImportError:
            self.warning("psutil no disponible, saltando detención de procesos")
            return True
        except Exception as e:
            self.error(f"Error deteniendo procesos: {e}")
            return True  # No es crítico
    
    def remove_shortcuts(self):
        """Elimina accesos directos"""
        self.info("Eliminando accesos directos...")
        
        shortcuts = [
            self.desktop / "Anti-Keylogger.bat",
            self.desktop / "Anti-Keylogger.lnk",
            # Agregar más ubicaciones si es necesario
        ]
        
        removed_count = 0
        for shortcut in shortcuts:
            try:
                if shortcut.exists():
                    shortcut.unlink()
                    self.success(f"Eliminado: {shortcut.name}")
                    removed_count += 1
            except Exception as e:
                self.error(f"Error eliminando {shortcut}: {e}")
        
        if removed_count == 0:
            self.info("No se encontraron accesos directos")
        
        return True
    
    def backup_config(self):
        """Crea backup de configuración (opcional)"""
        config_dir = self.install_dir / "config"
        logs_dir = self.install_dir / "logs"
        
        if not config_dir.exists() and not logs_dir.exists():
            return True
        
        backup_dir = Path.home() / "AntiKeylogger_Backup"
        
        try:
            response = input("¿Crear backup de configuración y logs? (s/N): ").lower().strip()
            
            if response in ['s', 'si', 'sí', 'y', 'yes']:
                self.info("Creando backup...")
                backup_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_subdir = backup_dir / f"backup_{timestamp}"
                backup_subdir.mkdir()
                
                if config_dir.exists():
                    shutil.copytree(config_dir, backup_subdir / "config")
                    self.success("Configuración respaldada")
                
                if logs_dir.exists():
                    shutil.copytree(logs_dir, backup_subdir / "logs")
                    self.success("Logs respaldados")
                
                self.info(f"Backup guardado en: {backup_subdir}")
            
            return True
            
        except Exception as e:
            self.error(f"Error creando backup: {e}")
            return True  # No es crítico
    
    def remove_installation_directory(self):
        """Elimina directorio de instalación"""
        self.info("Eliminando directorio de instalación...")
        
        try:
            if self.install_dir.exists():
                # Intentar eliminar archivos individuales primero
                for root, dirs, files in os.walk(self.install_dir, topdown=False):
                    for file in files:
                        try:
                            file_path = Path(root) / file
                            file_path.unlink()
                        except Exception as e:
                            self.warning(f"No se pudo eliminar {file}: {e}")
                    
                    for dir_name in dirs:
                        try:
                            dir_path = Path(root) / dir_name
                            dir_path.rmdir()
                        except Exception as e:
                            self.warning(f"No se pudo eliminar directorio {dir_name}: {e}")
                
                # Eliminar directorio principal
                try:
                    self.install_dir.rmdir()
                    self.success("Directorio de instalación eliminado")
                except Exception as e:
                    # Usar shutil como fallback
                    shutil.rmtree(self.install_dir, ignore_errors=True)
                    if not self.install_dir.exists():
                        self.success("Directorio de instalación eliminado (con shutil)")
                    else:
                        self.error(f"No se pudo eliminar completamente: {e}")
                        return False
            else:
                self.info("Directorio de instalación no existe")
            
            return True
            
        except Exception as e:
            self.error(f"Error eliminando instalación: {e}")
            return False
    
    def cleanup_registry(self):
        """Limpia registros del sistema (Windows)"""
        # Por simplicidad, no implementamos limpieza de registro
        # En versiones futuras se podría agregar
        return True
    
    def show_completion_message(self):
        """Muestra mensaje de finalización"""
        print(f"\n{self.GREEN}" + "=" * 50)
        print("🗑️  DESINSTALACIÓN COMPLETADA")
        print("=" * 50 + f"{self.END}")
        
        print(f"\n{self.GREEN}✅ El Anti-Keylogger ha sido desinstalado exitosamente{self.END}")
        
        backup_dir = Path.home() / "AntiKeylogger_Backup"
        if backup_dir.exists():
            print(f"\n{self.BLUE}📦 Backups disponibles en:{self.END}")
            print(f"   {backup_dir}")
        
        print(f"\n{self.BLUE}🔄 Para reinstalar:{self.END}")
        print("   Ejecuta: python install_antivirus.py")
        
        print(f"\n{self.YELLOW}Gracias por usar Anti-Keylogger Protection!{self.END}")
    
    def run_uninstallation(self):
        """Ejecuta todo el proceso de desinstalación"""
        try:
            # Confirmación del usuario
            print("Este script eliminará completamente el Anti-Keylogger de tu PC")
            print("Todos los archivos de instalación serán eliminados")
            
            response = input("\n¿Estás seguro de que quieres continuar? (s/N): ").lower().strip()
            
            if response not in ['s', 'si', 'sí', 'y', 'yes']:
                self.info("Desinstalación cancelada por el usuario")
                return False
            
            print()
            
            # Verificar instalación
            if not self.check_installation():
                return False
            
            # Pasos de desinstalación
            steps = [
                ("Deteniendo procesos", self.stop_processes),
                ("Creando backup (opcional)", self.backup_config),
                ("Eliminando accesos directos", self.remove_shortcuts),
                ("Eliminando instalación", self.remove_installation_directory),
                ("Limpiando registros", self.cleanup_registry)
            ]
            
            for step_name, step_func in steps:
                self.info(f"Paso: {step_name}")
                if not step_func():
                    self.error(f"Falló: {step_name}")
                    return False
                print()  # Línea en blanco
            
            self.show_completion_message()
            return True
            
        except KeyboardInterrupt:
            self.error("Desinstalación cancelada por el usuario")
            return False
        except Exception as e:
            self.error(f"Error inesperado: {e}")
            return False

def main():
    """Punto de entrada principal"""
    uninstaller = AntiKeyloggerUninstaller()
    
    try:
        success = uninstaller.run_uninstallation()
        
        if success:
            print(f"\n{uninstaller.GREEN}✅ Desinstalación completada exitosamente{uninstaller.END}")
        else:
            print(f"\n{uninstaller.RED}❌ Desinstalación falló o fue cancelada{uninstaller.END}")
        
        input("\nPresiona Enter para salir...")
        
    except KeyboardInterrupt:
        print(f"\n{uninstaller.YELLOW}⚠️  Desinstalación cancelada{uninstaller.END}")

if __name__ == "__main__":
    main()