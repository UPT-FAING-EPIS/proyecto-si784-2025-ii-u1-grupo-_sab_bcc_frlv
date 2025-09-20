import argparse
import json
import pickle
from pathlib import Path

import pandas as pd


def load_features(path):
    with open(path, 'r', encoding='utf-8') as f:
        feats = json.load(f)
    return [s.strip() for s in feats]


def find_default_pkl():
    p = Path(__file__).resolve().parents[1] / 'modelos'
    res = list(p.glob('modelo_keylogger*.pkl'))
    return res[0] if res else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pkl', help='ruta a modelo .pkl')
    ap.add_argument('--onnx', help='ruta a modelo .onnx')
    ap.add_argument('--features', help='ruta a features.json', default=None)
    ap.add_argument('--input', help='csv de entrada', required=True)
    args = ap.parse_args()

    repo = Path(__file__).resolve().parents[1]
    modelos = repo / 'modelos'

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

        # Heurística: si el modelo exportó dos outputs, buscar uno con tipo int (label)
        # y otro ZipMap con probabilidades.
        labels = None
        labels_path = Path(__file__).resolve().parents[1] / 'modelos' / 'label_classes.json'
        if labels_path.exists():
            with open(labels_path, 'r', encoding='utf-8') as f:
                labels = json.load(f)

        # Map outputs by type/name from session metadata
        out_names = [o.name for o in sess.get_outputs()]
        name_to_out = dict(zip(out_names, outs))

        # print available outputs
        print('ONNX outputs:', [(o.name, o.shape, o.type) for o in sess.get_outputs()])

        # Try to find 'output_label' and 'output_probability'
        label_arr = None
        prob_obj = None
        if 'output_label' in name_to_out:
            label_arr = name_to_out['output_label']
        else:
            # fallback: first output if int
            candidate = outs[0]
            try:
                if getattr(candidate, 'dtype', None) is not None and 'int' in str(candidate.dtype):
                    label_arr = candidate
            except Exception:
                pass

        if 'output_probability' in name_to_out:
            prob_obj = name_to_out['output_probability']
        else:
            # try to find a non-int output
            for o in outs:
                try:
                    if getattr(o, 'dtype', None) is not None and 'float' in str(o.dtype):
                        prob_obj = o
                        break
                except Exception:
                    continue

        # If prob_obj is a ZipMap (list of dicts), convert to 2D array
        probs = None
        try:
            # ZipMap from onnxruntime may come as a list of dicts
            if isinstance(prob_obj, list) and len(prob_obj) > 0 and isinstance(prob_obj[0], dict):
                # determine label order
                cls_keys = sorted({k for d in prob_obj for k in d.keys()})
                import numpy as _np
                probs = _np.zeros((len(prob_obj), len(cls_keys)), dtype=float)
                for i, d in enumerate(prob_obj):
                    for j, k in enumerate(cls_keys):
                        probs[i, j] = float(d.get(k, 0.0))
                # if labels provided, try reorder to labels order
                if labels and [str(i) for i in range(len(labels))] == cls_keys:
                    pass
        except Exception:
            probs = None

        # Print human friendly outputs
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
        default = find_default_pkl()
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
