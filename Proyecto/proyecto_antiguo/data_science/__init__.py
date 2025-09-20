# Data Science Module
# ===================

"""
Módulo de ciencia de datos para el pipeline de ML.
Contiene herramientas de preprocesamiento y análisis.
"""

__version__ = "1.0.0"
__author__ = "Data Science Team"

# Importaciones principales
try:
    from .data_preprocessing import DataPreprocessor
    
    __all__ = ["DataPreprocessor"]
    
except ImportError as e:
    print(f"Warning: No se pudo importar algunos módulos: {e}")
    __all__ = []