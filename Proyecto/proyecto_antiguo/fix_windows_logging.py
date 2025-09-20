#!/usr/bin/env python3
"""
Fix Windows Logging - Remover emojis para evitar errores de encoding
"""

import os
import re

def fix_logging_messages():
    """Remueve emojis de los mensajes de logging en todos los archivos"""
    
    # Mapeo de emojis a texto
    emoji_replacements = {
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⚠️': '[WARNING]',
        '🤖': '[ML]',
        '🌐': '[NET]',
        '⚙️': '[PROC]',
        '📊': '[DATA]',
        '📋': '[INFO]',
        '🏷️': '[LABEL]',
        '🔍': '[SEARCH]',
        '📁': '[FILE]',
        '🛡️': '[SHIELD]',
        '🔥': '[FIRE]',
        '💾': '[SAVE]',
        '🚀': '[START]',
        '⏱️': '[TIME]',
        '🎯': '[TARGET]',
        '🔒': '[LOCK]',
        '📈': '[STATS]',
        '🔄': '[SYNC]',
        '💻': '[SYS]',
        '🎉': '[SUCCESS]',
        '🔬': '[TEST]',
        '📤': '[OUT]',
        '📥': '[IN]',
        '🟢': '[GREEN]',
        '🔴': '[RED]',
        '🟡': '[YELLOW]',
        '🔵': '[BLUE]'
    }
    
    # Archivos a procesar
    files_to_fix = [
        'antivirus/detectors/ml_detector.py',
        'antivirus/monitors/network_monitor.py', 
        'antivirus/monitors/process_monitor.py',
        'antivirus/monitors/file_monitor.py',
        'antivirus/core/analyzer.py',
        'antivirus/core/quarantine.py',
        'antivirus/core/antivirus_engine.py'
    ]
    
    fixed_count = 0
    
    print("🔧 ARREGLANDO LOGGING PARA WINDOWS")
    print("=" * 50)
    
    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            print(f"   ⏭️ Saltando {file_path} (no existe)")
            continue
            
        print(f"   📝 Procesando {file_path}...")
        
        try:
            # Leer archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Reemplazar emojis
            for emoji, replacement in emoji_replacements.items():
                content = content.replace(emoji, replacement)
            
            # Solo escribir si hubo cambios
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_count += 1
                print(f"       ✅ Arreglado: {file_path}")
            else:
                print(f"       ⏭️ Sin cambios: {file_path}")
                
        except Exception as e:
            print(f"       ❌ Error en {file_path}: {e}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   Archivos procesados: {len(files_to_fix)}")
    print(f"   Archivos arreglados: {fixed_count}")
    
    if fixed_count > 0:
        print(f"\n✅ LOGGING ARREGLADO PARA WINDOWS")
        print("   Los mensajes de logging ahora son compatibles con Windows")
        print("   Ejecuta las pruebas de nuevo para ver la diferencia")
    else:
        print(f"\n📝 NO HABÍA EMOJIS QUE ARREGLAR")
    
    return fixed_count > 0

if __name__ == "__main__":
    success = fix_logging_messages()
    exit(0 if success else 1)