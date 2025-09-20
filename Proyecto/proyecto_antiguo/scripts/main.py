#!/usr/bin/env python3
"""
Sistema Anti-Keylogger con Machine Learning
===========================================

Sistema de detección de keyloggers usando técnicas de Machine Learning.
Implementa Clean Architecture para una base de código mantenible y escalable.

Uso:
    python main.py [comando] [opciones]

Comandos disponibles:
    scan-once       - Escanear directorio una vez
    monitor         - Monitoreo continuo
    analyze-file    - Analizar archivo específico
    scan-processes  - Escanear procesos en ejecución
    generate-config - Generar archivo de configuración

Ejemplos:
    python main.py scan-once --directory ~/Downloads
    python main.py monitor --interval 30 --duration 3600
    python main.py analyze-file malware_sample.exe
    python main.py scan-processes
    python main.py generate-config --environment production

Para más información:
    python main.py --help
    python main.py [comando] --help
"""

import sys
from pathlib import Path

# Agregar el directorio src al path para imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ui.cli import main

if __name__ == "__main__":
    main()