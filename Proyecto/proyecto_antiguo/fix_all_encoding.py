#!/usr/bin/env python3
"""
Fix Windows Encoding - Remover todos los emojis de todos los archivos Python
"""

import os
import re
from pathlib import Path

def fix_all_python_files():
    """Remueve emojis de TODOS los archivos Python"""
    
    # Mapeo más completo de emojis a texto
    emoji_replacements = {
        '[OK]': '[OK]',
        '[ERROR]': '[ERROR]',
        '[WARNING]': '[WARNING]',
        '[ML]': '[ML]',
        '[NET]': '[NET]',
        '[PROC]': '[PROC]',
        '[DATA]': '[DATA]',
        '[INFO]': '[INFO]',
        '[LABEL]': '[LABEL]',
        '[SEARCH]': '[SEARCH]',
        '[FILE]': '[FILE]',
        '[SHIELD]': '[SHIELD]',
        '[FIRE]': '[FIRE]',
        '[SAVE]': '[SAVE]',
        '[START]': '[START]',
        '[TIME]': '[TIME]',
        '[TARGET]': '[TARGET]',
        '[LOCK]': '[LOCK]',
        '[STATS]': '[STATS]',
        '[SYNC]': '[SYNC]',
        '[SYS]': '[SYS]',
        '[SUCCESS]': '[SUCCESS]',
        '[TEST]': '[TEST]',
        '[OUT]': '[OUT]',
        '[IN]': '[IN]',
        '[GREEN]': '[GREEN]',
        '[RED]': '[RED]',
        '[YELLOW]': '[YELLOW]',
        '[BLUE]': '[BLUE]',
        '[CLEAN]': '[CLEAN]',
        '[DELETE]': '[DELETE]',
        '[PACKAGE]': '[PACKAGE]',
        '[DOC]': '[DOC]',
        '[EDIT]': '[EDIT]',
        '[SKIP]': '[SKIP]',
        '[MOVE]': '[MOVE]',
        '[FOLDER]': '[FOLDER]',
        '[TOOL]': '[TOOL]',
        '[FIX]': '[FIX]'
    }
    
    workspace_path = Path(".")
    fixed_count = 0
    total_files = 0
    
    print("[CLEAN] ARREGLANDO ENCODING PARA WINDOWS")
    print("=" * 50)
    
    # Buscar TODOS los archivos Python
    for py_file in workspace_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
            
        total_files += 1
        print(f"   [EDIT] Procesando {py_file}...")
        
        try:
            # Leer archivo
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Reemplazar emojis
            for emoji, replacement in emoji_replacements.items():
                content = content.replace(emoji, replacement)
            
            # Solo escribir si hubo cambios
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_count += 1
                print(f"       [OK] Arreglado: {py_file}")
            else:
                print(f"       [SKIP] Sin cambios: {py_file}")
                
        except Exception as e:
            print(f"       [ERROR] Error en {py_file}: {e}")
    
    print(f"\n[DATA] RESUMEN:")
    print(f"   Archivos procesados: {total_files}")
    print(f"   Archivos arreglados: {fixed_count}")
    
    if fixed_count > 0:
        print(f"\n[OK] ENCODING ARREGLADO PARA WINDOWS")
        print("   Los archivos ahora son compatibles con Windows")
    else:
        print(f"\n[INFO] NO HABIA EMOJIS QUE ARREGLAR")
    
    return fixed_count > 0

if __name__ == "__main__":
    success = fix_all_python_files()
    exit(0 if success else 1)