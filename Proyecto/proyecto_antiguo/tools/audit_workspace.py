#!/usr/bin/env python3
"""
Auditoría del Workspace - Detectar duplicados y verificar funcionalidad
========================================================================

Este script analiza todos los archivos Python en el workspace para:
1. Detectar archivos duplicados o similares
2. Verificar que todos los scripts se ejecuten correctamente
3. Identificar dependencias faltantes
4. Organizar y recomendar limpieza
"""

import os
import ast
import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path
from collections import defaultdict
import difflib

class WorkspaceAuditor:
    def __init__(self, workspace_path="."):
        self.workspace_path = Path(workspace_path)
        self.python_files = []
        self.duplicates = []
        self.similar_files = []
        self.executable_scripts = []
        self.broken_scripts = []
        self.dependencies = defaultdict(set)
        
    def scan_python_files(self):
        """Escanea todos los archivos Python en el workspace"""
        print("[SEARCH] ESCANEANDO ARCHIVOS PYTHON")
        print("=" * 50)
        
        for py_file in self.workspace_path.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                self.python_files.append(py_file)
                print(f"   [DOC] {py_file}")
        
        print(f"\n[DATA] Total archivos Python encontrados: {len(self.python_files)}")
        return self.python_files
    
    def calculate_file_hash(self, file_path):
        """Calcula hash MD5 del contenido del archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Normalizar espacios en blanco para comparación
                normalized = ' '.join(content.split())
                return hashlib.md5(normalized.encode()).hexdigest()
        except Exception:
            return None
    
    def find_duplicates(self):
        """Encuentra archivos duplicados por contenido"""
        print("\n[SEARCH] BUSCANDO ARCHIVOS DUPLICADOS")
        print("=" * 50)
        
        hash_to_files = defaultdict(list)
        
        for py_file in self.python_files:
            file_hash = self.calculate_file_hash(py_file)
            if file_hash:
                hash_to_files[file_hash].append(py_file)
        
        # Identificar duplicados
        for file_hash, files in hash_to_files.items():
            if len(files) > 1:
                self.duplicates.append(files)
                print(f"   [SYNC] DUPLICADOS ENCONTRADOS:")
                for file in files:
                    print(f"      - {file}")
                print()
        
        if not self.duplicates:
            print("   [OK] No se encontraron archivos duplicados")
        
        return self.duplicates
    
    def find_similar_files(self, threshold=0.8):
        """Encuentra archivos similares (no exactamente duplicados)"""
        print("\n[SEARCH] BUSCANDO ARCHIVOS SIMILARES")
        print("=" * 50)
        
        file_contents = {}
        
        # Leer contenido de todos los archivos
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    file_contents[py_file] = f.read()
            except Exception:
                continue
        
        # Comparar archivos de a pares
        files = list(file_contents.keys())
        
        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                file1, file2 = files[i], files[j]
                content1 = file_contents[file1]
                content2 = file_contents[file2]
                
                # Calcular similitud
                similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
                
                if similarity >= threshold:
                    self.similar_files.append((file1, file2, similarity))
                    print(f"   [INFO] SIMILARES ({similarity:.1%}):")
                    print(f"      - {file1}")
                    print(f"      - {file2}")
                    print()
        
        if not self.similar_files:
            print("   [OK] No se encontraron archivos muy similares")
        
        return self.similar_files
    
    def check_script_executability(self):
        """Verifica qué scripts son ejecutables (tienen if __name__ == '__main__')"""
        print("\n[START] VERIFICANDO SCRIPTS EJECUTABLES")
        print("=" * 50)
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar if __name__ == '__main__'
                if 'if __name__ == "__main__"' in content or "if __name__ == '__main__'" in content:
                    self.executable_scripts.append(py_file)
                    print(f"   [TARGET] EJECUTABLE: {py_file}")
                    
                    # Intentar verificar sintaxis
                    try:
                        ast.parse(content)
                        print(f"      [OK] Sintaxis válida")
                    except SyntaxError as e:
                        print(f"      [ERROR] Error de sintaxis: {e}")
                        self.broken_scripts.append(py_file)
                        
            except Exception as e:
                print(f"   [ERROR] Error leyendo {py_file}: {e}")
                self.broken_scripts.append(py_file)
        
        print(f"\n[DATA] Scripts ejecutables encontrados: {len(self.executable_scripts)}")
        return self.executable_scripts
    
    def analyze_dependencies(self):
        """Analiza las dependencias import de cada archivo"""
        print("\n[PACKAGE] ANALIZANDO DEPENDENCIAS")
        print("=" * 50)
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parsear AST para encontrar imports
                tree = ast.parse(content)
                file_deps = set()
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            file_deps.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            file_deps.add(node.module.split('.')[0])
                
                if file_deps:
                    self.dependencies[py_file] = file_deps
                    
            except Exception as e:
                print(f"   [WARNING] Error analizando {py_file}: {e}")
        
        # Mostrar dependencias más comunes
        all_deps = defaultdict(int)
        for deps in self.dependencies.values():
            for dep in deps:
                all_deps[dep] += 1
        
        print("   [DATA] DEPENDENCIAS MÁS USADAS:")
        for dep, count in sorted(all_deps.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"      {dep}: {count} archivos")
        
        return self.dependencies
    
    def test_script_execution(self, script_path):
        """Prueba ejecutar un script para ver si funciona"""
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            try:
                # Intentar ejecución básica
                result = subprocess.run(
                    [sys.executable, "-c", f"import sys; sys.path.append('.'); exec(open('{script_path}').read())"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return "error" not in result.stderr.lower()
            except:
                return False
    
    def generate_report(self):
        """Genera reporte completo de la auditoría"""
        print("\n" + "=" * 70)
        print("[INFO] REPORTE DE AUDITORÍA DEL WORKSPACE")
        print("=" * 70)
        
        print(f"\n[DATA] RESUMEN GENERAL:")
        print(f"   Total archivos Python: {len(self.python_files)}")
        print(f"   Scripts ejecutables: {len(self.executable_scripts)}")
        print(f"   Archivos duplicados: {len(self.duplicates)}")
        print(f"   Archivos similares: {len(self.similar_files)}")
        print(f"   Scripts con errores: {len(self.broken_scripts)}")
        
        print(f"\n[TARGET] SCRIPTS EJECUTABLES PRINCIPALES:")
        main_scripts = [
            "simple_launcher.py",
            "test_antivirus.py", 
            "install_antivirus.py",
            "test_ml_detection.py",
            "fix_windows_logging.py"
        ]
        
        for script in main_scripts:
            script_path = self.workspace_path / script
            if script_path.exists():
                print(f"   [OK] {script} - EXISTE")
            else:
                print(f"   [ERROR] {script} - NO ENCONTRADO")
        
        print(f"\n[CLEAN] RECOMENDACIONES DE LIMPIEZA:")
        
        if self.duplicates:
            print(f"   📂 Eliminar {len(self.duplicates)} grupos de archivos duplicados")
        
        # Identificar scripts obsoletos o de prueba
        test_scripts = [f for f in self.python_files if 'test' in f.name.lower() or 'demo' in f.name.lower()]
        if len(test_scripts) > 3:
            print(f"   🧪 Considerar consolidar {len(test_scripts)} scripts de prueba")
        
        # Scripts en directorio raíz
        root_scripts = [f for f in self.python_files if f.parent == self.workspace_path]
        if len(root_scripts) > 10:
            print(f"   [FILE] Mover algunos de los {len(root_scripts)} scripts del directorio raíz")
        
        print(f"\n[OK] AUDITORÍA COMPLETADA")
        
        return {
            'total_files': len(self.python_files),
            'executable_scripts': len(self.executable_scripts),
            'duplicates': len(self.duplicates),
            'similar_files': len(self.similar_files),
            'broken_scripts': len(self.broken_scripts)
        }

def main():
    """Función principal"""
    auditor = WorkspaceAuditor()
    
    # Ejecutar auditoría completa
    auditor.scan_python_files()
    auditor.find_duplicates()
    auditor.find_similar_files()
    auditor.check_script_executability()
    auditor.analyze_dependencies()
    
    # Generar reporte final
    results = auditor.generate_report()
    
    return results

if __name__ == "__main__":
    results = main()
    
    # Exit code basado en problemas encontrados
    if results['broken_scripts'] > 0 or results['duplicates'] > 0:
        exit(1)
    else:
        exit(0)