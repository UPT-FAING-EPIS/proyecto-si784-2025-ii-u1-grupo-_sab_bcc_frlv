# Copia del script de inferencia principal
# Puedes adaptarlo para integrarlo con el nuevo CLI interactivo

import argparse
import json
import pickle
from pathlib import Path
import pandas as pd

def load_features(path):
    with open(path, 'r', encoding='utf-8') as f:
        feats = json.load(f)
    return [s.strip() for s in feats]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pkl', help='ruta a modelo .pkl')
    ap.add_argument('--onnx', help='ruta a modelo .onnx')
    ap.add_argument('--features', help='ruta a features.json', default=None)
    ap.add_argument('--input', help='csv de entrada', required=True)
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent
    modelos = repo

    feats_path = args.features
    if not feats_path:
        feats_path = next(modelos.glob('*features*_clean.json'), None) or next(modelos.glob('*features*.json'), None)
    feats_path = Path(feats_path)
    feats = load_features(feats_path)

    df = pd.read_csv(args.input, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    X = df[feats].fillna(0).astype(float)

    if args.onnx:
        import onnxruntime as ort
        sess = ort.InferenceSession(str(args.onnx), providers=['CPUExecutionProvider'])
        input_name = sess.get_inputs()[0].name
        outs = sess.run(None, {input_name: X.values.astype('float32')})
        labels = None
        labels_path = repo / 'label_classes.json'
        if labels_path.exists():
            with open(labels_path, 'r', encoding='utf-8') as f:
                labels = json.load(f)
        out_names = [o.name for o in sess.get_outputs()]
        name_to_out = dict(zip(out_names, outs))
        print('ONNX outputs:', [(o.name, o.shape, o.type) for o in sess.get_outputs()])
        label_arr = None
        prob_obj = None
        if 'output_label' in name_to_out:
            label_arr = name_to_out['output_label']
        else:
            candidate = outs[0]
            try:
                if getattr(candidate, 'dtype', None) is not None and 'int' in str(candidate.dtype):
                    label_arr = candidate
            except Exception:
                pass
        if 'output_probability' in name_to_out:
            prob_obj = name_to_out['output_probability']
        else:
            for o in outs:
                try:
                    if getattr(o, 'dtype', None) is not None and 'float' in str(o.dtype):
                        prob_obj = o
                        break
                except Exception:
                    continue
        probs = None
        try:
            if isinstance(prob_obj, list) and len(prob_obj) > 0 and isinstance(prob_obj[0], dict):
                cls_keys = sorted({k for d in prob_obj for k in d.keys()})
                import numpy as _np
                probs = _np.zeros((len(prob_obj), len(cls_keys)), dtype=float)
                for i, d in enumerate(prob_obj):
                    for j, k in enumerate(cls_keys):
                        probs[i, j] = float(d.get(k, 0.0))
        except Exception:
            probs = None
        if label_arr is not None:
            print('Labels (primeras 5):', label_arr[:5])
            if labels:
                mapped = [labels[int(v)] if 0 <= int(v) < len(labels) else str(v) for v in label_arr[:5]]
                print('Labels mapeadas (primeras 5):', mapped)
        if probs is not None:
            print('Probabilidades (primeras 5 filas):')
            print(probs[:5])
        elif prob_obj is not None:
            print('Probabilidad (formato ZipMap o no-tensor) primer elemento:', str(prob_obj[0])[:200])
        return
    pkl_path = args.pkl
    if not pkl_path:
        default = next(modelos.glob('*.pkl'), None)
        if default:
            pkl_path = str(default)
        else:
            raise SystemExit('No pkl provided and none found in modelos/')
    with open(pkl_path, 'rb') as f:
        model = pickle.load(f)
    if hasattr(model, 'predict_proba'):
        print(model.predict_proba(X.values)[:5])
    else:
        print(model.predict(X.values)[:5])

if __name__ == '__main__':
    main()
