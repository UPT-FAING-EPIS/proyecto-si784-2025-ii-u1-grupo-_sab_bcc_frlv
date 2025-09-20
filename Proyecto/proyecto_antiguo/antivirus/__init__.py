"""
Sistema Anti-Keylogger con Machine Learning
==========================================

Módulo principal del sistema antivirus que detecta keyloggers en tiempo real
utilizando técnicas de machine learning y análisis heurístico.

Componentes principales:
- Motor de detección (core/engine.py)
- Monitores de sistema (monitors/)
- Detectores especializados (detectors/)
- Utilidades (utils/)
"""

__version__ = "1.0.0"
__author__ = "Anti-Keylogger Team"
__description__ = "Sistema antivirus especializado en detección de keyloggers con ML"

from .core.engine import AntiKeyloggerEngine

__all__ = [
    'AntiKeyloggerEngine'
]