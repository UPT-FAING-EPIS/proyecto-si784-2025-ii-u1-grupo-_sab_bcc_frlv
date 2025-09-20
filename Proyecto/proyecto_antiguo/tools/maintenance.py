#!/usr/bin/env python3
"""
Sistema de Mantenimiento del Anti-Keylogger
==========================================

Herramientas de mantenimiento, limpieza y optimización
del sistema antivirus y archivos asociados.
"""

import os
import sys
import shutil
import time
import json
from pathlib import Path
from datetime import datetime, timedelta


class AntivirusMaintenance:
    """Sistema de mantenimiento del antivirus"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.stats = {
            'files_cleaned': 0,
            'space_freed_mb': 0,
            'logs_rotated': 0,
            'backups_created': 0,
            'errors_found': 0
        }
    
    def run_maintenance(self, mode='standard'):
        """Ejecuta rutina de mantenimiento"""
        print("[CLEAN] SISTEMA DE MANTENIMIENTO DEL ANTI-KEYLOGGER")
        print("=" * 55)
        print(f"Modo: {mode.upper()}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            if mode == 'full':
                self._full_maintenance()
            elif mode == 'logs':
                self._clean_logs_only()
            elif mode == 'cache':
                self._clean_cache_only()
            elif mode == 'backup':
                self._backup_only()
            else:  # standard
                self._standard_maintenance()
            
            self._show_maintenance_summary()
            
        except Exception as e:
            print(f"[ERROR] Error durante mantenimiento: {e}")
            sys.exit(1)
    
    def _standard_maintenance(self):
        """Mantenimiento estándar"""
        print("[FIX] MANTENIMIENTO ESTÁNDAR")
        print("-" * 30)
        
        self._clean_old_logs()
        self._clean_temp_files()
        self._clean_quarantine()
        self._verify_directory_structure()
        self._check_disk_space()
    
    def _full_maintenance(self):
        """Mantenimiento completo"""
        print("[FIX] MANTENIMIENTO COMPLETO")
        print("-" * 30)
        
        self._backup_important_files()
        self._clean_old_logs()
        self._clean_temp_files()
        self._clean_quarantine()
        self._clean_cache_files()
        self._clean_old_models()
        self._verify_directory_structure()
        self._optimize_databases()
        self._check_disk_space()
        self._verify_file_integrity()
    
    def _clean_logs_only(self):
        """Solo limpieza de logs"""
        print("[EDIT] LIMPIEZA DE LOGS")
        print("-" * 20)
        self._clean_old_logs()
    
    def _clean_cache_only(self):
        """Solo limpieza de cache"""
        print("[SAVE] LIMPIEZA DE CACHE")
        print("-" * 22)
        self._clean_cache_files()
    
    def _backup_only(self):
        """Solo backup"""
        print("💿 BACKUP DE ARCHIVOS")
        print("-" * 22)
        self._backup_important_files()
    
    def _clean_old_logs(self):
        """Limpia logs antiguos"""
        print("[FOLDER] Limpiando logs antiguos...")
        
        logs_dir = self.root_dir / "logs"
        if not logs_dir.exists():
            print("   ℹ️ Directorio de logs no existe")
            return
        
        # Configuración: mantener logs de últimos 30 días
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for log_file in logs_dir.glob("*.log"):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    file_size_mb = log_file.stat().st_size / (1024 * 1024)
                    log_file.unlink()
                    self.stats['files_cleaned'] += 1
                    self.stats['space_freed_mb'] += file_size_mb
                    print(f"   [DELETE] Eliminado: {log_file.name} ({file_size_mb:.1f}MB)")
            except Exception as e:
                print(f"   [WARNING] Error procesando {log_file.name}: {e}")
                self.stats['errors_found'] += 1
        
        # Rotar logs grandes (>100MB)
        for log_file in logs_dir.glob("*.log"):
            try:
                if log_file.stat().st_size > 100 * 1024 * 1024:  # 100MB
                    backup_name = f"{log_file.stem}_{datetime.now().strftime('%Y%m%d')}.log"
                    backup_path = logs_dir / backup_name
                    shutil.move(log_file, backup_path)
                    log_file.touch()  # Crear nuevo archivo vacío
                    self.stats['logs_rotated'] += 1
                    print(f"   [SYNC] Rotado: {log_file.name} -> {backup_name}")
            except Exception as e:
                print(f"   [WARNING] Error rotando {log_file.name}: {e}")
                self.stats['errors_found'] += 1
    
    def _clean_temp_files(self):
        """Limpia archivos temporales"""
        print("🗃️ Limpiando archivos temporales...")
        
        temp_dir = self.root_dir / "temp"
        if not temp_dir.exists():
            print("   ℹ️ Directorio temp no existe")
            return
        
        for temp_file in temp_dir.iterdir():
            try:
                if temp_file.is_file():
                    file_size_mb = temp_file.stat().st_size / (1024 * 1024)
                    temp_file.unlink()
                    self.stats['files_cleaned'] += 1
                    self.stats['space_freed_mb'] += file_size_mb
                    print(f"   [DELETE] Eliminado: {temp_file.name} ({file_size_mb:.1f}MB)")
                elif temp_file.is_dir():
                    shutil.rmtree(temp_file)
                    print(f"   [FILE] Directorio eliminado: {temp_file.name}")
            except Exception as e:
                print(f"   [WARNING] Error procesando {temp_file.name}: {e}")
                self.stats['errors_found'] += 1
    
    def _clean_quarantine(self):
        """Limpia archivos en cuarentena antiguos"""
        print("[LOCK] Limpiando cuarentena...")
        
        quarantine_dir = self.root_dir / "quarantine"
        if not quarantine_dir.exists():
            print("   ℹ️ Directorio de cuarentena no existe")
            return
        
        # Configuración: mantener cuarentena de últimos 60 días
        cutoff_date = datetime.now() - timedelta(days=60)
        
        for quarantine_file in quarantine_dir.iterdir():
            try:
                file_time = datetime.fromtimestamp(quarantine_file.stat().st_mtime)
                if file_time < cutoff_date:
                    if quarantine_file.is_file():
                        file_size_mb = quarantine_file.stat().st_size / (1024 * 1024)
                        quarantine_file.unlink()
                        self.stats['files_cleaned'] += 1
                        self.stats['space_freed_mb'] += file_size_mb
                        print(f"   [DELETE] Eliminado de cuarentena: {quarantine_file.name} ({file_size_mb:.1f}MB)")
                    elif quarantine_file.is_dir():
                        shutil.rmtree(quarantine_file)
                        print(f"   [FILE] Directorio de cuarentena eliminado: {quarantine_file.name}")
            except Exception as e:
                print(f"   [WARNING] Error procesando {quarantine_file.name}: {e}")
                self.stats['errors_found'] += 1
    
    def _clean_cache_files(self):
        """Limpia archivos de caché"""
        print("[SAVE] Limpiando archivos de caché...")
        
        # Limpiar __pycache__
        for pycache_dir in self.root_dir.rglob("__pycache__"):
            try:
                shutil.rmtree(pycache_dir)
                print(f"   [DELETE] Eliminado: {pycache_dir.relative_to(self.root_dir)}")
                self.stats['files_cleaned'] += 1
            except Exception as e:
                print(f"   [WARNING] Error eliminando {pycache_dir}: {e}")
                self.stats['errors_found'] += 1
        
        # Limpiar archivos .pyc
        for pyc_file in self.root_dir.rglob("*.pyc"):
            try:
                file_size_mb = pyc_file.stat().st_size / (1024 * 1024)
                pyc_file.unlink()
                self.stats['files_cleaned'] += 1
                self.stats['space_freed_mb'] += file_size_mb
                print(f"   [DELETE] Eliminado: {pyc_file.relative_to(self.root_dir)}")
            except Exception as e:
                print(f"   [WARNING] Error eliminando {pyc_file}: {e}")
                self.stats['errors_found'] += 1
    
    def _clean_old_models(self):
        """Limpia modelos antiguos o temporales"""
        print("[ML] Limpiando modelos antiguos...")
        
        models_dir = self.root_dir / "models" / "development"
        if not models_dir.exists():
            print("   ℹ️ Directorio de modelos no existe")
            return
        
        # Buscar archivos temporales de modelos
        temp_patterns = ["*.tmp", "*.temp", "*_backup_*", "*_old_*"]
        
        for pattern in temp_patterns:
            for temp_file in models_dir.glob(pattern):
                try:
                    file_size_mb = temp_file.stat().st_size / (1024 * 1024)
                    temp_file.unlink()
                    self.stats['files_cleaned'] += 1
                    self.stats['space_freed_mb'] += file_size_mb
                    print(f"   [DELETE] Eliminado: {temp_file.name} ({file_size_mb:.1f}MB)")
                except Exception as e:
                    print(f"   [WARNING] Error eliminando {temp_file.name}: {e}")
                    self.stats['errors_found'] += 1
    
    def _verify_directory_structure(self):
        """Verifica y corrige estructura de directorios"""
        print("[FILE] Verificando estructura de directorios...")
        
        required_dirs = [
            "logs",
            "quarantine", 
            "temp",
            "data/exports",
            "data/backups",
            "models/development"
        ]
        
        for dir_path in required_dirs:
            full_path = self.root_dir / dir_path
            if not full_path.exists():
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    print(f"   [OK] Creado: {dir_path}")
                except Exception as e:
                    print(f"   [ERROR] Error creando {dir_path}: {e}")
                    self.stats['errors_found'] += 1
            else:
                print(f"   [OK] Existe: {dir_path}")
    
    def _backup_important_files(self):
        """Crea backup de archivos importantes"""
        print("💿 Creando backup de archivos importantes...")
        
        backup_dir = self.root_dir / "data" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Archivos importantes para backup
        important_files = [
            "antivirus/config.toml",
            "models/development/metadata.json",
            "models/development/label_classes.json"
        ]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for file_path in important_files:
            source = self.root_dir / file_path
            if source.exists():
                try:
                    backup_name = f"{source.stem}_{timestamp}{source.suffix}"
                    backup_path = backup_dir / backup_name
                    shutil.copy2(source, backup_path)
                    self.stats['backups_created'] += 1
                    print(f"   [SAVE] Backup: {file_path} -> {backup_name}")
                except Exception as e:
                    print(f"   [WARNING] Error en backup de {file_path}: {e}")
                    self.stats['errors_found'] += 1
            else:
                print(f"   ℹ️ No encontrado: {file_path}")
    
    def _optimize_databases(self):
        """Optimiza bases de datos si existen"""
        print("🗄️ Optimizando bases de datos...")
        
        # Buscar archivos de base de datos
        db_patterns = ["*.db", "*.sqlite", "*.sqlite3"]
        
        found_dbs = False
        for pattern in db_patterns:
            for db_file in self.root_dir.rglob(pattern):
                found_dbs = True
                try:
                    # Aquí podrían ir comandos VACUUM u otras optimizaciones
                    print(f"   [FIX] Encontrada DB: {db_file.relative_to(self.root_dir)}")
                except Exception as e:
                    print(f"   [WARNING] Error optimizando {db_file}: {e}")
                    self.stats['errors_found'] += 1
        
        if not found_dbs:
            print("   ℹ️ No se encontraron bases de datos para optimizar")
    
    def _check_disk_space(self):
        """Verifica espacio en disco"""
        print("💽 Verificando espacio en disco...")
        
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.root_dir)
            
            total_gb = total / (1024**3)
            used_gb = used / (1024**3)
            free_gb = free / (1024**3)
            usage_percent = (used / total) * 100
            
            print(f"   Total: {total_gb:.1f}GB")
            print(f"   Usado: {used_gb:.1f}GB ({usage_percent:.1f}%)")
            print(f"   Libre: {free_gb:.1f}GB")
            
            if free_gb < 1.0:  # Menos de 1GB libre
                print("   [WARNING] ADVERTENCIA: Poco espacio libre en disco")
                self.stats['errors_found'] += 1
            elif usage_percent > 90:
                print("   [WARNING] ADVERTENCIA: Disco casi lleno")
            else:
                print("   [OK] Espacio en disco adecuado")
                
        except Exception as e:
            print(f"   [WARNING] Error verificando espacio: {e}")
            self.stats['errors_found'] += 1
    
    def _verify_file_integrity(self):
        """Verifica integridad de archivos críticos"""
        print("[SEARCH] Verificando integridad de archivos...")
        
        critical_files = [
            "antivirus/core/engine.py",
            "antivirus/detectors/ml_detector.py",
            "antivirus_launcher.py",
            "install_antivirus.py"
        ]
        
        for file_path in critical_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                try:
                    # Verificar que el archivo se puede leer
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read(100)  # Leer primeros 100 caracteres
                    
                    if len(content) > 0:
                        print(f"   [OK] {file_path}")
                    else:
                        print(f"   [WARNING] {file_path} - archivo vacío")
                        self.stats['errors_found'] += 1
                        
                except Exception as e:
                    print(f"   [ERROR] {file_path} - error: {e}")
                    self.stats['errors_found'] += 1
            else:
                print(f"   [ERROR] {file_path} - NO ENCONTRADO")
                self.stats['errors_found'] += 1
    
    def _show_maintenance_summary(self):
        """Muestra resumen del mantenimiento"""
        print("\n" + "=" * 50)
        print("[DATA] RESUMEN DE MANTENIMIENTO")
        print("=" * 50)
        
        print(f"Archivos limpiados: {self.stats['files_cleaned']}")
        print(f"Espacio liberado: {self.stats['space_freed_mb']:.1f} MB")
        print(f"Logs rotados: {self.stats['logs_rotated']}")
        print(f"Backups creados: {self.stats['backups_created']}")
        print(f"Errores encontrados: {self.stats['errors_found']}")
        
        if self.stats['errors_found'] == 0:
            print("\n[OK] MANTENIMIENTO COMPLETADO SIN ERRORES")
        else:
            print(f"\n[WARNING] MANTENIMIENTO COMPLETADO CON {self.stats['errors_found']} ERRORES")
        
        # Recomendaciones
        print("\n💡 RECOMENDACIONES:")
        
        if self.stats['space_freed_mb'] > 100:
            print("   - Considere ejecutar mantenimiento más frecuentemente")
        
        if self.stats['errors_found'] > 0:
            print("   - Revisar errores específicos mostrados arriba")
            print("   - Verificar permisos de archivos y directorios")
        
        if self.stats['logs_rotated'] > 0:
            print("   - Considere configurar rotación automática de logs")
        
        print("   - Ejecutar mantenimiento semanalmente")
        print("   - Verificar backups regularmente")
    
    def show_usage(self):
        """Muestra información de uso"""
        print("[CLEAN] SISTEMA DE MANTENIMIENTO DEL ANTI-KEYLOGGER")
        print("=" * 55)
        print()
        print("Uso: python maintenance.py [modo]")
        print()
        print("Modos disponibles:")
        print("  standard  - Mantenimiento estándar (por defecto)")
        print("  full      - Mantenimiento completo con backup")
        print("  logs      - Solo limpieza de logs")
        print("  cache     - Solo limpieza de cache")
        print("  backup    - Solo crear backups")
        print()
        print("Ejemplos:")
        print("  python maintenance.py")
        print("  python maintenance.py full")
        print("  python maintenance.py logs")


def main():
    """Función principal"""
    maintenance = AntivirusMaintenance()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode in ['standard', 'full', 'logs', 'cache', 'backup']:
            maintenance.run_maintenance(mode)
        elif mode in ['help', '--help', '-h']:
            maintenance.show_usage()
        else:
            print(f"[ERROR] Modo desconocido: {mode}")
            maintenance.show_usage()
            sys.exit(1)
    else:
        maintenance.run_maintenance('standard')


if __name__ == "__main__":
    main()