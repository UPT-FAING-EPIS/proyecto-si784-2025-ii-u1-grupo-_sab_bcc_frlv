#!/usr/bin/env python
"""
Convierte un modelo sklearn guardado en .pkl a ONNX usando skl2onnx.
Por defecto usa:
  modelos/modelo_keylogger_from_datos.pkl -> modelos/modelo_keylogger_from_datos.onnx
y `modelos/modelo_keylogger_from_datos_features.json` para el número de features.

Uso:
  python scripts/convert_pkl_to_onnx.py --pkl modelos/modelo_keylogger_from_datos.pkl --features modelos/modelo_keylogger_from_datos_features.json --out modelos/modelo_keylogger_from_datos.onnx

Si skl2onnx no está instalado, instalar: pip install skl2onnx
"""
import argparse
import pickle
import json
from pathlib import Path
import sys

DEFAULT_PKL = Path(__file__).resolve().parents[1] / 'modelos' / 'modelo_keylogger_from_datos.pkl'
DEFAULT_FEATURES = Path(__file__).resolve().parents[1] / 'modelos' / 'modelo_keylogger_from_datos_features.json'
DEFAULT_OUT = Path(__file__).resolve().parents[1] / 'modelos' / 'modelo_keylogger_from_datos.onnx'


def main():
    parser = argparse.ArgumentParser(description='Convert sklearn .pkl model to ONNX')
    parser.add_argument('--pkl', type=Path, default=DEFAULT_PKL, help='Path to .pkl model')
    parser.add_argument('--features', type=Path, default=DEFAULT_FEATURES, help='Path to features json (list)')
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT, help='Output ONNX path')
    args = parser.parse_args()

    if not args.pkl.exists():
        print(f"Error: no se encontró el .pkl en {args.pkl}")
        sys.exit(1)
    if not args.features.exists():
        print(f"Error: no se encontró el features.json en {args.features}")
        sys.exit(2)

    print(f"Cargando modelo desde {args.pkl}...")
    with open(args.pkl, 'rb') as fh:
        clf = pickle.load(fh)

    print(f"Cargando features desde {args.features}...")
    with open(args.features, 'r', encoding='utf-8') as fh:
        features = json.load(fh)

    try:
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType
    except Exception as e:
        print("skl2onnx no está instalado. Instálalo con: pip install skl2onnx")
        print("Error:", e)
        sys.exit(3)

    n_features = len(features)
    initial_type = [("float_input", FloatTensorType([None, n_features]))]
    print(f"Convirtiendo modelo a ONNX (n_features={n_features})...")
    try:
        onnx_model = convert_sklearn(clf, initial_types=initial_type)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, 'wb') as fh:
            fh.write(onnx_model.SerializeToString())
        print(f"Guardado ONNX en {args.out}")
    except Exception as e:
        print("Falló la conversión a ONNX:")
        print(e)
        sys.exit(4)

if __name__ == '__main__':
    main()
