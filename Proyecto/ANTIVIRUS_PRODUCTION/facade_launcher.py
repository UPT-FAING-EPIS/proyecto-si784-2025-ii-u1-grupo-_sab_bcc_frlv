#!/usr/bin/env python3
"""
Launcher Simplificado con Facade Pattern
========================================

Interfaz super simple para usar el antivirus.
"""

import sys
import time
from pathlib import Path

# Importar el Facade
try:
    from antivirus.facade import create_antivirus
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)


def simple_threat_handler(threat):
    """Manejador simple de amenazas"""
    print(f"\n[THREAT DETECTED]:")
    print(f"   Tipo: {threat.get('type', 'Desconocido')}")
    print(f"   Confianza: {threat.get('confidence', 0):.2%}")
    print(f"   Fuente: {threat.get('source', 'N/A')}")
    print(f"   Detalles: {threat.get('details', 'N/A')}\n")


def main():
    print("[ANTIVIRUS] ANTI-KEYLOGGER - LAUNCHER FACADE")
    print("=" * 50)
    
    # Crear antivirus con Facade (super simple)
    print("\n1. Inicializando sistema...")
    antivirus = create_antivirus()
    
    # Configurar
    print("2. Configurando sistema...")
    antivirus.set_sensitivity('medium')
    antivirus.add_alert_handler(simple_threat_handler)
    
    # Mostrar estado inicial
    print("3. Estado inicial:")
    status = antivirus.get_status()
    print(f"   Monitoreando: {status['is_monitoring']}")
    print(f"   Amenazas detectadas: {status['threats_detected']}")
    
    # Iniciar protección
    print("\n4. Iniciando protección...")
    if antivirus.start():
        print("   [OK] Protección activa")
        
        try:
            # Monitoreo por 30 segundos
            print("\n5. Monitoreando por 30 segundos...")
            for i in range(30):
                time.sleep(1)
                print(f"   [MONITOR] Monitoreando... {i+1}/30s", end="\r")
            
            print("\n\n6. Estado final:")
            final_status = antivirus.get_status()
            print(f"   Tiempo activo: {final_status.get('uptime', 'N/A')}")
            print(f"   Amenazas: {final_status['threats_detected']}")
            
        except KeyboardInterrupt:
            print("\n\n[STOP] Detenido por usuario")
        
        finally:
            # Detener sistema
            print("7. Deteniendo sistema...")
            antivirus.stop()
            print("   [STOP] Sistema detenido")
    
    else:
        print("   [ERROR] Error iniciando protección")
        return 1
    
    print("\n[OK] Prueba completada")
    return 0


if __name__ == "__main__":
    sys.exit(main())