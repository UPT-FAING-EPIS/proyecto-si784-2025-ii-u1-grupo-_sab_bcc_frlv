#!/usr/bin/env python3
"""
Limpieza del Workspace - Eliminar duplicados y organizar archivos
================================================================

Basado en la auditoría, este script:
1. Elimina archivos duplicados identificados
2. Organiza scripts por funcionalidad 
3. Mueve archivos obsoletos a backup
4. Crea estructura limpia del workspace
"""

import os
import shutil
from pathlib import Path

class WorkspaceCleaner:
    def __init__(self, workspace_path="."):
        self.workspace_path = Path(workspace_path)
        self.removed_files = []
        self.moved_files = []
        
    def remove_duplicates(self):
        """Elimina archivos duplicados identificados en la auditoría"""
        print("[CLEAN] ELIMINANDO ARCHIVOS DUPLICADOS")
        print("=" * 50)
        
        # Duplicados identificados por la auditoría
        duplicates_to_remove = [
            # Mantener scripts/ y eliminar de backup/scripts/
            "backup/scripts/train_from_datos.py",  # Duplicado de scripts/train_from_datos.py
            
            # Eliminar duplicados de predecir_keylogger en backup/
            "backup/tools/antivirus_control.py",  # Mantener solo uno
            "backup/workbench/antivirus_cli_interactivo/predecir_keylogger.py",  # Duplicado
            "backup/workbench/antivirus_monitor_py/modelo_datasets/predecir_keylogger.py"  # Duplicado
        ]
        
        for file_path in duplicates_to_remove:
            full_path = self.workspace_path / file_path
            if full_path.exists():
                try:
                    full_path.unlink()
                    self.removed_files.append(file_path)
                    print(f"   [DELETE] Eliminado: {file_path}")
                except Exception as e:
                    print(f"   [ERROR] Error eliminando {file_path}: {e}")
            else:
                print(f"   [WARNING] No encontrado: {file_path}")
        
        print(f"\n[DATA] Archivos duplicados eliminados: {len(self.removed_files)}")
    
    def organize_root_scripts(self):
        """Organiza scripts en el directorio raíz"""
        print("\n[FILE] ORGANIZANDO SCRIPTS DEL DIRECTORIO RAÍZ")
        print("=" * 50)
        
        # Crear directorio tools/ si no existe
        tools_dir = self.workspace_path / "tools"
        tools_dir.mkdir(exist_ok=True)
        
        # Scripts principales que deben permanecer en raíz
        keep_in_root = {
            "simple_launcher.py",     # Launcher principal
            "install_antivirus.py",   # Instalador
            "test_antivirus.py"       # Test principal
        }
        
        # Scripts para mover a tools/
        move_to_tools = {
            "test_ml_detection.py",   # Test específico ML
            "fix_windows_logging.py", # Utilidad de arreglo
            "audit_workspace.py",     # Auditoría
            "inspect_onnx_quick.py",  # Inspección ONNX
            "maintenance.py",         # Mantenimiento
            "deploy.py",              # Deployment
            "antivirus_launcher.py"   # Launcher alternativo
        }
        
        print("   📌 MANTENIENDO EN RAÍZ:")
        for script in keep_in_root:
            script_path = self.workspace_path / script
            if script_path.exists():
                print(f"      [OK] {script}")
            else:
                print(f"      [ERROR] {script} (no encontrado)")
        
        print("\n   [PACKAGE] MOVIENDO A tools/:")
        for script in move_to_tools:
            src_path = self.workspace_path / script
            dst_path = tools_dir / script
            
            if src_path.exists():
                try:
                    shutil.move(str(src_path), str(dst_path))
                    self.moved_files.append((script, f"tools/{script}"))
                    print(f"      [MOVE] {script} → tools/{script}")
                except Exception as e:
                    print(f"      [ERROR] Error moviendo {script}: {e}")
            else:
                print(f"      [WARNING] {script} (no encontrado)")
    
    def clean_empty_directories(self):
        """Limpia directorios vacíos"""
        print("\n[FOLDER] LIMPIANDO DIRECTORIOS VACÍOS")
        print("=" * 50)
        
        removed_dirs = []
        
        # Buscar directorios vacíos en backup/
        backup_dir = self.workspace_path / "backup"
        if backup_dir.exists():
            for root, dirs, files in os.walk(backup_dir, topdown=False):
                root_path = Path(root)
                if not any(root_path.iterdir()):  # Directorio vacío
                    try:
                        root_path.rmdir()
                        removed_dirs.append(str(root_path.relative_to(self.workspace_path)))
                        print(f"   [DELETE] Directorio vacío eliminado: {root_path.relative_to(self.workspace_path)}")
                    except Exception as e:
                        print(f"   [ERROR] Error eliminando directorio {root_path}: {e}")
        
        if not removed_dirs:
            print("   [OK] No se encontraron directorios vacíos")
    
    def create_readme_organization(self):
        """Crea README con la nueva organización"""
        print("\n[INFO] CREANDO DOCUMENTACIÓN DE ORGANIZACIÓN")
        print("=" * 50)
        
        readme_content = """# Organización del Workspace - Sistema Anti-Keylogger

## [FILE] Estructura Principal

### [START] Scripts Principales (Directorio Raíz)
- `simple_launcher.py` - **Launcher principal del sistema antivirus**
- `install_antivirus.py` - **Instalador de dependencias y configuración**  
- `test_antivirus.py` - **Suite de pruebas principal**

### [TOOL] Herramientas (tools/)
- `test_ml_detection.py` - Pruebas específicas del detector ML
- `fix_windows_logging.py` - Corrección de problemas de encoding en Windows
- `audit_workspace.py` - Auditoría y análisis del workspace
- `inspect_onnx_quick.py` - Inspección de modelos ONNX
- `maintenance.py` - Herramientas de mantenimiento
- `deploy.py` - Scripts de deployment
- `antivirus_launcher.py` - Launcher alternativo

### [ML] Sistema Antivirus (antivirus/)
- `core/` - Motor principal del antivirus
- `detectors/` - Detectores (ML, comportamiento, red)
- `monitors/` - Monitores (red, procesos, archivos)
- `utils/` - Utilidades compartidas

### 🧠 Pipeline ML (ml_pipeline/, scripts/)
- `training/` - Entrenamiento de modelos
- `evaluation/` - Evaluación y métricas
- `deployment/` - Deployment de modelos
- `utils/` - Utilidades ML

### [DATA] Modelos (models/)
- `development/` - Modelos entrenados (ONNX, PKL)
- `metadata.json` - Metadatos de modelos
- `label_classes.json` - Clases de predicción

### [SAVE] Datos (DATOS/)
- `Keylogger_Detection_Dataset.csv` - Dataset principal
- `Keylogger_Detection.csv` - Dataset procesado

### 🗄️ Backup (backup/)
- Versiones anteriores y archivos históricos
- **Nota**: Se eliminaron duplicados durante la limpieza

## [START] Uso Rápido

```bash
# Instalación y configuración
python install_antivirus.py

# Prueba básica del sistema
python simple_launcher.py --test

# Pruebas completas
python test_antivirus.py

# Monitoreo en tiempo real
python simple_launcher.py --monitor
```

## [CLEAN] Limpieza Realizada

### Archivos Duplicados Eliminados:
- `backup/scripts/train_from_datos.py` (duplicado de scripts/)
- `backup/tools/antivirus_control.py` (múltiples duplicados)
- Varios duplicados de `predecir_keylogger.py` en backup/

### Organización Aplicada:
- Scripts utilitarios movidos a `tools/`
- Mantenidos en raíz solo los scripts principales
- Estructura clara por funcionalidad

---
**Generado automáticamente por workspace_cleaner.py**
"""
        
        readme_path = self.workspace_path / "WORKSPACE_ORGANIZATION.md"
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print(f"   [DOC] Creado: {readme_path}")
        except Exception as e:
            print(f"   [ERROR] Error creando README: {e}")
    
    def generate_cleanup_report(self):
        """Genera reporte de la limpieza realizada"""
        print("\n" + "=" * 70)
        print("[INFO] REPORTE DE LIMPIEZA DEL WORKSPACE")
        print("=" * 70)
        
        print(f"\n[DELETE] ARCHIVOS ELIMINADOS ({len(self.removed_files)}):")
        for file in self.removed_files:
            print(f"   [ERROR] {file}")
        
        print(f"\n[PACKAGE] ARCHIVOS MOVIDOS ({len(self.moved_files)}):")
        for src, dst in self.moved_files:
            print(f"   [MOVE] {src} → {dst}")
        
        print(f"\n[OK] LIMPIEZA COMPLETADA")
        print(f"   - Duplicados eliminados: {len(self.removed_files)}")
        print(f"   - Archivos reorganizados: {len(self.moved_files)}")
        print(f"   - Estructura optimizada")
        
        return {
            'removed_files': len(self.removed_files),
            'moved_files': len(self.moved_files)
        }

def main():
    """Función principal de limpieza"""
    print("[CLEAN] INICIANDO LIMPIEZA DEL WORKSPACE")
    print("=" * 70)
    
    cleaner = WorkspaceCleaner()
    
    # Ejecutar limpieza paso a paso
    cleaner.remove_duplicates()
    cleaner.organize_root_scripts()
    cleaner.clean_empty_directories()
    cleaner.create_readme_organization()
    
    # Generar reporte final
    results = cleaner.generate_cleanup_report()
    
    return results

if __name__ == "__main__":
    results = main()
    exit(0)