#!/usr/bin/env python3
"""
Script de Despliegue del Sistema Anti-Keylogger
==============================================

Automatiza el proceso completo de instalación, configuración
y puesta en marcha del sistema antivirus con ML.
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime


class AntivirusDeployment:
    """Automatizador de despliegue del sistema antivirus"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.deployment_log = []
        self.errors = []
        self.warnings = []
    
    def deploy(self, mode='complete'):
        """Ejecuta el despliegue completo"""
        print("[START] DESPLIEGUE DEL SISTEMA ANTI-KEYLOGGER")
        print("=" * 50)
        print(f"Modo: {mode.upper()}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            if mode == 'complete':
                self._complete_deployment()
            elif mode == 'install':
                self._install_only()
            elif mode == 'train':
                self._train_models_only()
            elif mode == 'test':
                self._test_only()
            elif mode == 'quick':
                self._quick_deployment()
            else:
                raise ValueError(f"Modo desconocido: {mode}")
            
            self._show_deployment_summary()
            
        except KeyboardInterrupt:
            print("\n🛑 Despliegue cancelado por usuario")
            sys.exit(1)
        except Exception as e:
            print(f"\n[ERROR] Error durante despliegue: {e}")
            self._log_step("DEPLOYMENT_ERROR", False, f"Error fatal: {e}")
            sys.exit(1)
    
    def _complete_deployment(self):
        """Despliegue completo paso a paso"""
        print("[SYNC] DESPLIEGUE COMPLETO")
        print("-" * 25)
        
        # Paso 1: Verificar requisitos
        self._verify_prerequisites()
        
        # Paso 2: Ejecutar instalación
        self._run_installation()
        
        # Paso 3: Entrenar modelos ML
        self._train_ml_models()
        
        # Paso 4: Ejecutar pruebas
        self._run_tests()
        
        # Paso 5: Configurar servicios
        self._configure_services()
        
        # Paso 6: Mantenimiento inicial
        self._initial_maintenance()
        
        # Paso 7: Verificación final
        self._final_verification()
    
    def _quick_deployment(self):
        """Despliegue rápido sin entrenamiento"""
        print("⚡ DESPLIEGUE RÁPIDO")
        print("-" * 22)
        
        self._verify_prerequisites()
        self._run_installation()
        self._run_tests()
        self._final_verification()
    
    def _install_only(self):
        """Solo instalación"""
        print("[PACKAGE] SOLO INSTALACIÓN")
        print("-" * 20)
        
        self._run_installation()
    
    def _train_models_only(self):
        """Solo entrenamiento de modelos"""
        print("[ML] SOLO ENTRENAMIENTO")
        print("-" * 22)
        
        self._train_ml_models()
    
    def _test_only(self):
        """Solo pruebas"""
        print("🧪 SOLO PRUEBAS")
        print("-" * 15)
        
        self._run_tests()
    
    def _verify_prerequisites(self):
        """Verifica prerequisitos del sistema"""
        print("\n1️⃣ Verificando prerequisitos...")
        
        # Verificar Python
        python_version = sys.version_info
        if python_version >= (3, 8):
            self._log_step("PYTHON_VERSION", True, f"Python {python_version.major}.{python_version.minor}")
        else:
            self._log_step("PYTHON_VERSION", False, f"Python {python_version.major}.{python_version.minor} < 3.8")
            return
        
        # Verificar pip
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True, check=True)
            self._log_step("PIP_AVAILABLE", True, "pip disponible")
        except subprocess.CalledProcessError:
            self._log_step("PIP_AVAILABLE", False, "pip no disponible")
            return
        
        # Verificar estructura de proyecto
        required_files = [
            "requirements.txt",
            "requirements_antivirus.txt",
            "antivirus/core/engine.py",
            "install_antivirus.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.root_dir / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self._log_step("PROJECT_STRUCTURE", False, f"Archivos faltantes: {missing_files}")
        else:
            self._log_step("PROJECT_STRUCTURE", True, "Estructura de proyecto correcta")
    
    def _run_installation(self):
        """Ejecuta el script de instalación"""
        print("\n2️⃣ Ejecutando instalación...")
        
        install_script = self.root_dir / "install_antivirus.py"
        
        if not install_script.exists():
            self._log_step("INSTALL_SCRIPT", False, "Script de instalación no encontrado")
            return
        
        try:
            print("   [IN] Ejecutando install_antivirus.py...")
            result = subprocess.run([sys.executable, str(install_script)], 
                                  capture_output=False, text=True, check=True,
                                  cwd=self.root_dir)
            
            self._log_step("INSTALLATION", True, "Instalación completada")
            
        except subprocess.CalledProcessError as e:
            self._log_step("INSTALLATION", False, f"Error en instalación: {e}")
            print("   [WARNING] Instalación falló, continuando con despliegue...")
    
    def _train_ml_models(self):
        """Entrena los modelos de Machine Learning"""
        print("\n3️⃣ Entrenando modelos ML...")
        
        # Verificar si ya existen modelos
        models_dir = self.root_dir / "models" / "development"
        pkl_model = models_dir / "modelo_keylogger_from_datos.pkl"
        onnx_model = models_dir / "modelo_keylogger_from_datos.onnx"
        
        if pkl_model.exists() and onnx_model.exists():
            print("   ℹ️ Modelos ya existen, omitiendo entrenamiento")
            self._log_step("ML_TRAINING", True, "Modelos existentes encontrados")
            return
        
        # Verificar datos de entrenamiento
        data_file = self.root_dir / "DATOS" / "Keylogger_Detection_Dataset.csv"
        if not data_file.exists():
            self._log_step("TRAINING_DATA", False, "Archivo de datos no encontrado")
            print("   [WARNING] Sin datos de entrenamiento, omitiendo modelos ML")
            return
        
        # Ejecutar entrenamiento
        train_script = self.root_dir / "scripts" / "train_from_datos.py"
        if train_script.exists():
            try:
                print("   [ML] Ejecutando entrenamiento...")
                result = subprocess.run([sys.executable, str(train_script)], 
                                      capture_output=False, text=True, check=True,
                                      cwd=self.root_dir)
                
                self._log_step("ML_TRAINING", True, "Entrenamiento completado")
                
                # Verificar conversión a ONNX
                convert_script = self.root_dir / "scripts" / "convert_pkl_to_onnx.py"
                if convert_script.exists():
                    print("   [SYNC] Convirtiendo a ONNX...")
                    subprocess.run([sys.executable, str(convert_script)], 
                                 capture_output=False, text=True, check=True,
                                 cwd=self.root_dir)
                    self._log_step("ONNX_CONVERSION", True, "Conversión ONNX completada")
                
            except subprocess.CalledProcessError as e:
                self._log_step("ML_TRAINING", False, f"Error en entrenamiento: {e}")
        else:
            self._log_step("TRAIN_SCRIPT", False, "Script de entrenamiento no encontrado")
    
    def _run_tests(self):
        """Ejecuta las pruebas del sistema"""
        print("\n4️⃣ Ejecutando pruebas...")
        
        test_script = self.root_dir / "test_antivirus.py"
        
        if not test_script.exists():
            self._log_step("TEST_SCRIPT", False, "Script de pruebas no encontrado")
            return
        
        try:
            print("   🧪 Ejecutando test_antivirus.py...")
            result = subprocess.run([sys.executable, str(test_script)], 
                                  capture_output=True, text=True,
                                  cwd=self.root_dir)
            
            # Las pruebas pueden fallar con exit code != 0 pero seguir siendo útiles
            if result.returncode == 0:
                self._log_step("SYSTEM_TESTS", True, "Todas las pruebas pasaron")
            else:
                self._log_step("SYSTEM_TESTS", False, "Algunas pruebas fallaron")
                print("   [WARNING] Revise los resultados de las pruebas arriba")
            
        except Exception as e:
            self._log_step("SYSTEM_TESTS", False, f"Error ejecutando pruebas: {e}")
    
    def _configure_services(self):
        """Configura servicios y configuración inicial"""
        print("\n5️⃣ Configurando servicios...")
        
        # Verificar archivo de configuración
        config_file = self.root_dir / "antivirus" / "config.toml"
        if config_file.exists():
            self._log_step("CONFIG_FILE", True, "Archivo de configuración encontrado")
        else:
            self._log_step("CONFIG_FILE", False, "Archivo de configuración no encontrado")
        
        # Crear directorios necesarios
        required_dirs = ["logs", "quarantine", "temp", "data/exports", "data/backups"]
        
        for dir_name in required_dirs:
            dir_path = self.root_dir / dir_name
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                self._log_step(f"DIR_{dir_name.upper()}", True, f"Directorio {dir_name} configurado")
            except Exception as e:
                self._log_step(f"DIR_{dir_name.upper()}", False, f"Error creando {dir_name}: {e}")
    
    def _initial_maintenance(self):
        """Ejecuta mantenimiento inicial"""
        print("\n6️⃣ Mantenimiento inicial...")
        
        maintenance_script = self.root_dir / "maintenance.py"
        
        if maintenance_script.exists():
            try:
                print("   [CLEAN] Ejecutando mantenimiento...")
                result = subprocess.run([sys.executable, str(maintenance_script), "standard"], 
                                      capture_output=True, text=True, check=True,
                                      cwd=self.root_dir)
                
                self._log_step("MAINTENANCE", True, "Mantenimiento inicial completado")
                
            except subprocess.CalledProcessError as e:
                self._log_step("MAINTENANCE", False, f"Error en mantenimiento: {e}")
        else:
            self._log_step("MAINTENANCE_SCRIPT", False, "Script de mantenimiento no encontrado")
    
    def _final_verification(self):
        """Verificación final del sistema"""
        print("\n7️⃣ Verificación final...")
        
        # Verificar launcher
        launcher = self.root_dir / "antivirus_launcher.py"
        if launcher.exists():
            try:
                # Ejecutar con --info para verificar
                result = subprocess.run([sys.executable, str(launcher), "--info"], 
                                      capture_output=True, text=True, check=True,
                                      cwd=self.root_dir)
                
                self._log_step("LAUNCHER_TEST", True, "Launcher funciona correctamente")
                
            except subprocess.CalledProcessError as e:
                self._log_step("LAUNCHER_TEST", False, f"Error en launcher: {e}")
        else:
            self._log_step("LAUNCHER_FILE", False, "Launcher no encontrado")
        
        # Verificar importación de módulos principales
        try:
            sys.path.insert(0, str(self.root_dir))
            from antivirus.core.engine import AntiKeyloggerEngine
            self._log_step("MODULE_IMPORT", True, "Módulos principales importables")
        except ImportError as e:
            self._log_step("MODULE_IMPORT", False, f"Error importando módulos: {e}")
    
    def _log_step(self, step_name, success, description):
        """Registra un paso del despliegue"""
        status = "[OK]" if success else "[ERROR]"
        message = f"   {status} {description}"
        print(message)
        
        self.deployment_log.append({
            'step': step_name,
            'success': success,
            'description': description,
            'timestamp': datetime.now().isoformat()
        })
        
        if not success:
            self.errors.append(description)
    
    def _show_deployment_summary(self):
        """Muestra resumen del despliegue"""
        total_steps = len(self.deployment_log)
        successful_steps = len([step for step in self.deployment_log if step['success']])
        failed_steps = total_steps - successful_steps
        
        print("\n" + "=" * 50)
        print("[DATA] RESUMEN DE DESPLIEGUE")
        print("=" * 50)
        
        print(f"Total de pasos: {total_steps}")
        print(f"Exitosos: {successful_steps} [OK]")
        print(f"Fallidos: {failed_steps} [ERROR]")
        
        if failed_steps == 0:
            print(f"\n[SUCCESS] DESPLIEGUE COMPLETADO EXITOSAMENTE")
            exit_code = 0
        elif successful_steps > failed_steps:
            print(f"\n[WARNING] DESPLIEGUE COMPLETADO CON ERRORES MENORES")
            exit_code = 1
        else:
            print(f"\n[ERROR] DESPLIEGUE FALLÓ")
            exit_code = 2
        
        # Mostrar errores
        if self.errors:
            print(f"\n[ERROR] ERRORES ENCONTRADOS:")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        # Siguientes pasos
        print(f"\n[START] SIGUIENTES PASOS:")
        
        if exit_code == 0:
            print("   1. El sistema está listo para usar")
            print("   2. Ejecutar: python antivirus_launcher.py --test")
            print("   3. Iniciar protección: python antivirus_launcher.py")
            
        elif exit_code == 1:
            print("   1. Revisar errores menores arriba")
            print("   2. Probar funcionalidad básica: python antivirus_launcher.py --info")
            print("   3. Contactar soporte si es necesario")
            
        else:
            print("   1. Revisar todos los errores mostrados")
            print("   2. Re-ejecutar instalación manual")
            print("   3. Verificar prerequisitos del sistema")
        
        # Información útil
        print(f"\n[DOC] ARCHIVOS IMPORTANTES:")
        print(f"   Launcher: python antivirus_launcher.py")
        print(f"   Pruebas: python test_antivirus.py")
        print(f"   Mantenimiento: python maintenance.py")
        print(f"   Configuración: antivirus/config.toml")
        print(f"   Logs: logs/")
        
        # Guardar log de despliegue
        self._save_deployment_log()
        
        sys.exit(exit_code)
    
    def _save_deployment_log(self):
        """Guarda el log del despliegue"""
        try:
            logs_dir = self.root_dir / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            log_file = logs_dir / f"deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(self.deployment_log, f, indent=2, ensure_ascii=False)
            
            print(f"\n[SAVE] Log de despliegue guardado en: {log_file}")
            
        except Exception as e:
            print(f"\n[WARNING] No se pudo guardar log de despliegue: {e}")
    
    def show_usage(self):
        """Muestra información de uso"""
        print("[START] SISTEMA DE DESPLIEGUE DEL ANTI-KEYLOGGER")
        print("=" * 50)
        print()
        print("Uso: python deploy.py [modo]")
        print()
        print("Modos disponibles:")
        print("  complete  - Despliegue completo (por defecto)")
        print("  quick     - Despliegue rápido sin entrenamiento")
        print("  install   - Solo instalación de dependencias")
        print("  train     - Solo entrenamiento de modelos ML")
        print("  test      - Solo ejecutar pruebas")
        print()
        print("Ejemplos:")
        print("  python deploy.py")
        print("  python deploy.py complete")
        print("  python deploy.py quick")
        print()
        print("Nota: El despliegue completo puede tomar varios minutos")
        print("      dependiendo de la velocidad de red y CPU.")


def main():
    """Función principal"""
    deployment = AntivirusDeployment()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode in ['complete', 'quick', 'install', 'train', 'test']:
            deployment.deploy(mode)
        elif mode in ['help', '--help', '-h']:
            deployment.show_usage()
        else:
            print(f"[ERROR] Modo desconocido: {mode}")
            deployment.show_usage()
            sys.exit(1)
    else:
        deployment.deploy('complete')


if __name__ == "__main__":
    main()