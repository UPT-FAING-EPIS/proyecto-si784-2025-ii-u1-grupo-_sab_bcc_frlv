# Script para simular una alerta de keylogger
# Este archivo genera un CSV con features que activarán la alerta del monitor

import pandas as pd
from pathlib import Path

# Ruta de salida (carpeta Descargas del usuario)
out_path = Path.home() / 'Downloads' / 'alerta_keylogger.csv'

# Features: deben coincidir con los nombres esperados por el modelo
features = {
    'file_size': 9999999,
    'num_sections': 10,
    'has_imports': 1,
    'entropy': 8.0,
    'is_document': 0,
    'is_image': 0,
    'is_archive': 0,
    'is_media': 0
}

# Puedes agregar más features según tu modelo

# Generar el CSV
pd.DataFrame([features]).to_csv(out_path, index=False)
print(f"Archivo de prueba generado en: {out_path}")
print("Ejecuta el monitor para ver la alerta.")
