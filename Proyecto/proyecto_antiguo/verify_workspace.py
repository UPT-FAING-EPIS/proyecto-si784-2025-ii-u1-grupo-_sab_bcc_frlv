#!/usr/bin/env python3
"""
Verificación Final del Workspace - Comprobar que todo funciona
============================================================

Script final para verificar que todos los componentes principales
funcionan correctamente después de la limpieza y organización.
"""

import sys
import os
from pathlib import Path
import subprocess

class WorkspaceVerifier:
    def __init__(self):
        self.workspace_path = Path(".")
        self.passed_tests = 0
        self.failed_tests = 0
        
    def test_main_scripts(self):
        """Verifica los scripts principales en el directorio raíz"""
        print("[START] VERIFICANDO SCRIPTS PRINCIPALES")
        print("=" * 50)
        
        main_scripts = [
            ("simple_launcher.py", ["--help"]),
            ("install_antivirus.py", ["--help"]),
            ("test_antivirus.py", ["--help"])
        ]
        
        for script, args in main_scripts:
            script_path = self.workspace_path / script
            if script_path.exists():
                try:
                    result = subprocess.run(
                        [sys.executable, str(script_path)] + args,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        print(f"   [OK] {script}: FUNCIONA")
                        self.passed_tests += 1
                    else:
                        print(f"   [ERROR] {script}: ERROR ({result.returncode})")
                        self.failed_tests += 1
                except Exception as e:
                    print(f"   [ERROR] {script}: EXCEPCIÓN ({e})")
                    self.failed_tests += 1
            else:
                print(f"   [ERROR] {script}: NO ENCONTRADO")
                self.failed_tests += 1
    
    def test_tools_scripts(self):
        """Verifica los scripts en tools/"""
        print("\n[TOOL] VERIFICANDO HERRAMIENTAS")
        print("=" * 50)
        
        tools_scripts = [
            "test_ml_detection.py",
            "fix_windows_logging.py",
            "audit_workspace.py",
            "inspect_onnx_quick.py"
        ]
        
        for script in tools_scripts:
            script_path = self.workspace_path / "tools" / script
            if script_path.exists():
                try:
                    # Verificar sintaxis básica
                    result = subprocess.run(
                        [sys.executable, "-m", "py_compile", str(script_path)],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print(f"   [OK] tools/{script}: SINTAXIS OK")
                        self.passed_tests += 1
                    else:
                        print(f"   [ERROR] tools/{script}: ERROR DE SINTAXIS")
                        self.failed_tests += 1
                except Exception as e:
                    print(f"   [ERROR] tools/{script}: EXCEPCIÓN ({e})")
                    self.failed_tests += 1
            else:
                print(f"   [ERROR] tools/{script}: NO ENCONTRADO")
                self.failed_tests += 1
    
    def test_antivirus_system(self):
        """Verifica que el sistema antivirus se puede inicializar"""
        print("\n[SHIELD] VERIFICANDO SISTEMA ANTIVIRUS")
        print("=" * 50)
        
        try:
            # Ejecutar test básico del sistema
            result = subprocess.run(
                [sys.executable, "simple_launcher.py", "--test"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and "SISTEMA FUNCIONANDO CORRECTAMENTE" in result.stdout:
                print("   [OK] Sistema antivirus: FUNCIONAL")
                self.passed_tests += 1
            else:
                print("   [ERROR] Sistema antivirus: ERROR")
                print(f"      Código de salida: {result.returncode}")
                if result.stderr:
                    print(f"      Error: {result.stderr[:200]}...")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"   [ERROR] Sistema antivirus: EXCEPCIÓN ({e})")
            self.failed_tests += 1
    
    def test_ml_detector(self):
        """Verifica que el detector ML funciona"""
        print("\n[ML] VERIFICANDO DETECTOR ML")
        print("=" * 50)
        
        try:
            # Ejecutar test específico ML
            result = subprocess.run(
                [sys.executable, "tools/test_ml_detection.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and "TODAS LAS PRUEBAS PASARON" in result.stdout:
                print("   [OK] Detector ML: FUNCIONAL")
                self.passed_tests += 1
            else:
                print("   [ERROR] Detector ML: ERROR")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"   [ERROR] Detector ML: EXCEPCIÓN ({e})")
            self.failed_tests += 1
    
    def verify_file_structure(self):
        """Verifica la estructura de archivos"""
        print("\n[FILE] VERIFICANDO ESTRUCTURA DE ARCHIVOS")
        print("=" * 50)
        
        required_structure = {
            "antivirus/": ["core/", "detectors/", "monitors/", "utils/"],
            "models/": ["development/"],
            "tools/": ["test_ml_detection.py", "fix_windows_logging.py"],
            "scripts/": ["training/", "evaluation/", "deployment/"],
            ".": ["simple_launcher.py", "install_antivirus.py", "test_antivirus.py"]
        }
        
        for base_path, required_items in required_structure.items():
            base_dir = self.workspace_path / base_path if base_path != "." else self.workspace_path
            
            for item in required_items:
                item_path = base_dir / item
                if item_path.exists():
                    print(f"   [OK] {base_path}{item}: EXISTE")
                    self.passed_tests += 1
                else:
                    print(f"   [ERROR] {base_path}{item}: NO ENCONTRADO")
                    self.failed_tests += 1
    
    def generate_final_report(self):
        """Genera reporte final de verificación"""
        print("\n" + "=" * 70)
        print("[INFO] REPORTE FINAL DE VERIFICACIÓN")
        print("=" * 70)
        
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n[DATA] RESULTADOS:")
        print(f"   Total pruebas: {total_tests}")
        print(f"   Pruebas exitosas: {self.passed_tests}")
        print(f"   Pruebas fallidas: {self.failed_tests}")
        print(f"   Tasa de éxito: {success_rate:.1f}%")
        
        if self.failed_tests == 0:
            print(f"\n[SUCCESS] VERIFICACIÓN COMPLETADA CON ÉXITO")
            print(f"   [OK] Workspace completamente funcional")
            print(f"   [OK] Todos los scripts principales operativos")
            print(f"   [OK] Sistema antivirus funcional")
            print(f"   [OK] Detector ML operativo")
            status = "SUCCESS"
        else:
            print(f"\n[WARNING] VERIFICACIÓN CON PROBLEMAS")
            print(f"   [ERROR] {self.failed_tests} componentes requieren atención")
            status = "WARNINGS"
        
        print(f"\n[START] COMANDOS DE INICIO RÁPIDO:")
        print(f"   # Instalación: python install_antivirus.py")
        print(f"   # Prueba básica: python simple_launcher.py --test")
        print(f"   # Monitoreo: python simple_launcher.py --monitor")
        print(f"   # Pruebas ML: python tools/test_ml_detection.py")
        
        return {
            'status': status,
            'passed': self.passed_tests,
            'failed': self.failed_tests,
            'success_rate': success_rate
        }

def main():
    """Función principal de verificación"""
    print("[SEARCH] INICIANDO VERIFICACIÓN FINAL DEL WORKSPACE")
    print("=" * 70)
    
    verifier = WorkspaceVerifier()
    
    # Ejecutar todas las verificaciones
    verifier.test_main_scripts()
    verifier.test_tools_scripts()
    verifier.verify_file_structure()
    verifier.test_antivirus_system()
    verifier.test_ml_detector()
    
    # Generar reporte final
    results = verifier.generate_final_report()
    
    return results

if __name__ == "__main__":
    results = main()
    
    # Exit code basado en resultados
    if results['status'] == 'SUCCESS':
        exit(0)
    else:
        exit(1)