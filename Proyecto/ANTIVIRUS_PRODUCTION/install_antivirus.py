#!/usr/bin/env python3
"""
Instalador Simple del Anti-Keylogger
===================================

Instalador fácil de usar para el sistema Anti-Keylogger.
Ejecuta: python install_antivirus.py

Funciones:
- Instala dependencias automáticamente
- Configura directorios necesarios
- Crea acceso directo en escritorio
- Verifica instalación
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import json
import tempfile
import zipfile
from datetime import datetime

class AntiKeyloggerInstaller:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.install_dir = Path.home() / "AntiKeylogger"
        self.desktop = Path.home() / "Desktop"
        self.python_exe = sys.executable
        self.platform = platform.system()
        
        # Colores para consola
        self.GREEN = '\033[92m'
        self.RED = '\033[91m'
        self.YELLOW = '\033[93m'
        self.BLUE = '\033[94m'
        self.END = '\033[0m'
        
        print(f"{self.BLUE}🛡️  INSTALADOR ANTI-KEYLOGGER{self.END}")
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
    
    def check_admin_rights(self):
        """Verifica si se ejecuta como administrador (opcional)"""
        try:
            if self.platform == "Windows":
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                if not is_admin:
                    self.warning("No se ejecuta como administrador")
                    self.warning("Algunas funciones pueden estar limitadas")
                    return False
            return True
        except:
            return False
    
    def check_python_version(self):
        """Verifica versión de Python"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.error(f"Python 3.8+ requerido. Actual: {version.major}.{version.minor}")
            return False
        
        self.success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
        return True
    
    def install_pip_packages(self):
        """Instala dependencias Python"""
        self.info("Instalando dependencias Python...")
        
        # Intentar usar requirements.txt si existe
        requirements_file = self.script_dir / "requirements.txt"
        
        if requirements_file.exists():
            self.info("Usando requirements.txt...")
            try:
                result = subprocess.run([
                    self.python_exe, "-m", "pip", "install", "-r", str(requirements_file)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.success("Dependencias instaladas desde requirements.txt")
                    return True
                else:
                    self.warning(f"Error con requirements.txt: {result.stderr}")
                    self.info("Intentando instalación manual...")
            except Exception as e:
                self.warning(f"Error usando requirements.txt: {e}")
                self.info("Intentando instalación manual...")
        
        # Instalación manual de paquetes críticos
        requirements = [
            "psutil",
            "watchdog", 
            "scikit-learn",
            "joblib",
            "numpy",
            "pefile",
            "onnxruntime",
            "fastapi",
            "uvicorn",
            "python-multipart",
            "python-magic-bin",  # Para Windows
            "requests",
            "toml",
            "colorama",  # Para colores en Windows
            "packaging"
        ]
        
        try:
            # Actualizar pip primero
            self.info("Actualizando pip...")
            subprocess.run([
                self.python_exe, "-m", "pip", "install", "--upgrade", "pip"
            ], capture_output=True, text=True)
            
            failed_packages = []
            
            for package in requirements:
                self.info(f"Instalando {package}...")
                result = subprocess.run([
                    self.python_exe, "-m", "pip", "install", package
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.success(f"{package} instalado")
                else:
                    self.error(f"Error instalando {package}: {result.stderr}")
                    failed_packages.append(package)
            
            if failed_packages:
                self.warning(f"Paquetes que fallaron: {', '.join(failed_packages)}")
                self.info("Intentando instalar paquetes críticos...")
                
                # Intentar instalar solo los más críticos
                critical = ["psutil", "watchdog", "numpy", "python-magic-bin"]
                for package in critical:
                    if package in failed_packages:
                        result = subprocess.run([
                            self.python_exe, "-m", "pip", "install", package, "--no-deps"
                        ], capture_output=True, text=True)
                        if result.returncode == 0:
                            self.success(f"{package} instalado (sin dependencias)")
                
                # No fallar la instalación por dependencias opcionales
                optional_packages = ["onnxruntime", "fastapi", "uvicorn"]
                failed_critical = [p for p in failed_packages if p not in optional_packages]
                
                if failed_critical:
                    self.error("Falló la instalación de paquetes críticos")
                    return False
                else:
                    self.warning("Algunas dependencias opcionales fallaron, pero se puede continuar")
            
            return True
            
        except Exception as e:
            self.error(f"Error instalando dependencias: {e}")
            return False
    
    def create_directories(self):
        """Crea estructura de directorios"""
        self.info("Creando directorios...")
        
        directories = [
            self.install_dir,
            self.install_dir / "logs",
            self.install_dir / "config", 
            self.install_dir / "models",
            self.install_dir / "temp"
        ]
        
        try:
            for dir_path in directories:
                dir_path.mkdir(parents=True, exist_ok=True)
                self.success(f"Directorio: {dir_path}")
            return True
        except Exception as e:
            self.error(f"Error creando directorios: {e}")
            return False
    
    def copy_files(self):
        """Copia archivos necesarios"""
        self.info("Copiando archivos del antivirus...")
        
        files_to_copy = [
            # Archivos principales
            ("antivirus_launcher.py", "antivirus_launcher.py"),
            ("simple_launcher.py", "simple_launcher.py"),
            ("facade_launcher.py", "facade_launcher.py"),
            ("config.toml", "config/config.toml"),
            
            # Directorio antivirus completo
            ("antivirus/", "antivirus/"),
            
            # Modelos ML
            ("models/", "models/"),
            
            # Configuración
            ("config/", "config/")
        ]
        
        try:
            for src, dst in files_to_copy:
                src_path = self.script_dir / src
                dst_path = self.install_dir / dst
                
                if src_path.exists():
                    if src_path.is_dir():
                        if dst_path.exists():
                            shutil.rmtree(dst_path)
                        shutil.copytree(src_path, dst_path)
                        self.success(f"Copiado directorio: {src}")
                    else:
                        dst_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        self.success(f"Copiado archivo: {src}")
                else:
                    self.warning(f"No encontrado: {src}")
            
            return True
        except Exception as e:
            self.error(f"Error copiando archivos: {e}")
            return False
    
    def create_desktop_shortcut(self):
        """Crea acceso directo en escritorio"""
        if self.platform != "Windows":
            self.info("Acceso directo solo disponible en Windows")
            return True
        
        self.info("Creando acceso directo en escritorio...")
        
        try:
            shortcut_path = self.desktop / "Anti-Keylogger.bat"
            
            bat_content = f"""@echo off
title Anti-Keylogger Protection
cd /d "{self.install_dir}"
"{self.python_exe}" antivirus_launcher.py
pause
"""
            
            with open(shortcut_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            
            self.success(f"Acceso directo creado: {shortcut_path}")
            return True
            
        except Exception as e:
            self.error(f"Error creando acceso directo: {e}")
            return False
    
    def create_launcher_script(self):
        """Crea script de inicio optimizado"""
        self.info("Creando script de inicio...")
        
        launcher_content = f'''#!/usr/bin/env python3
"""
Launcher del Anti-Keylogger
Punto de entrada principal
"""

import sys
import os
from pathlib import Path

# Añadir directorio de instalación al path
install_dir = Path(__file__).parent
sys.path.insert(0, str(install_dir))

try:
    # Importar y ejecutar el antivirus
    from antivirus_launcher import main
    
    if __name__ == "__main__":
        print("🛡️  Iniciando Anti-Keylogger Protection...")
        main()
        
except ImportError as e:
    print(f"❌ Error importando módulos: {{e}}")
    print("💡 Verifica que la instalación sea correcta")
    input("Presiona Enter para salir...")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error ejecutando antivirus: {{e}}")
    input("Presiona Enter para salir...")
    sys.exit(1)
'''
        
        try:
            launcher_path = self.install_dir / "start_antivirus.py"
            with open(launcher_path, 'w', encoding='utf-8') as f:
                f.write(launcher_content)
            
            self.success(f"Script de inicio: {launcher_path}")
            return True
        except Exception as e:
            self.error(f"Error creando launcher: {e}")
            return False
    
    def test_installation(self):
        """Prueba básica de la instalación"""
        self.info("Verificando instalación...")
        
        try:
            # Cambiar al directorio de instalación
            os.chdir(self.install_dir)
            
            # Probar importación básica
            sys.path.insert(0, str(self.install_dir))
            
            # Verificar archivos críticos
            critical_files = [
                "antivirus_launcher.py",
                "antivirus/__init__.py",
                "models/",
                "config/"
            ]
            
            for file_path in critical_files:
                full_path = self.install_dir / file_path
                if full_path.exists():
                    self.success(f"Verificado: {file_path}")
                else:
                    self.error(f"Falta archivo: {file_path}")
                    return False
            
            # Probar importación del antivirus
            try:
                import antivirus
                self.success("Módulo antivirus importado correctamente")
            except ImportError as e:
                self.error(f"Error importando antivirus: {e}")
                return False
            
            return True
            
        except Exception as e:
            self.error(f"Error en verificación: {e}")
            return False
    
    def show_completion_message(self):
        """Muestra mensaje de finalización"""
        print(f"\n{self.GREEN}" + "=" * 50)
        print("🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 50 + f"{self.END}")
        
        print(f"\n{self.BLUE}📍 Ubicación de instalación:{self.END}")
        print(f"   {self.install_dir}")
        
        print(f"\n{self.BLUE}🚀 Formas de ejecutar el antivirus:{self.END}")
        print(f"   1. Doble click en: {self.desktop / 'Anti-Keylogger.bat'}")
        print(f"   2. Ejecutar: python {self.install_dir / 'start_antivirus.py'}")
        print(f"   3. Desde consola: cd {self.install_dir} && python antivirus_launcher.py")
        
        print(f"\n{self.YELLOW}⚠️  Importante:{self.END}")
        print("   • Ejecuta como administrador para máxima protección")
        print("   • Los logs se guardan en: logs/")
        print("   • Configuración en: config/")
        
        print(f"\n{self.GREEN}¡Tu sistema está protegido contra keyloggers!{self.END}")
    
    def run_installation(self):
        """Ejecuta todo el proceso de instalación"""
        try:
            # Verificaciones previas
            if not self.check_python_version():
                return False
            
            self.check_admin_rights()
            
            # Instalación paso a paso
            steps = [
                ("Instalando dependencias Python", self.install_pip_packages),
                ("Creando directorios", self.create_directories),
                ("Copiando archivos", self.copy_files),
                ("Creando launcher", self.create_launcher_script),
                ("Creando acceso directo", self.create_desktop_shortcut),
                ("Verificando instalación", self.test_installation)
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
            self.error("Instalación cancelada por el usuario")
            return False
        except Exception as e:
            self.error(f"Error inesperado: {e}")
            return False

def main():
    """Punto de entrada principal"""
    installer = AntiKeyloggerInstaller()
    
    print("Este instalador configurará el Anti-Keylogger en tu PC")
    print("Presiona Ctrl+C para cancelar en cualquier momento\n")
    
    try:
        input("Presiona Enter para continuar...")
        print()
        
        success = installer.run_installation()
        
        if success:
            print(f"\n{installer.GREEN}✅ Instalación completada exitosamente{installer.END}")
        else:
            print(f"\n{installer.RED}❌ Instalación falló{installer.END}")
            print("Revisa los errores mostrados arriba")
        
        input("\nPresiona Enter para salir...")
        
    except KeyboardInterrupt:
        print(f"\n{installer.YELLOW}⚠️  Instalación cancelada{installer.END}")

if __name__ == "__main__":
    main()