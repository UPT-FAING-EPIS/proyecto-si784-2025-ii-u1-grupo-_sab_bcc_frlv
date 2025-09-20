#!/usr/bin/env python3
"""Verify equivalence between sklearn .pkl and an ONNX model using sampled CSVs.

Optimizado: solo lee las primeras n filas del primer CSV compatible.
"""
import argparse
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import onnxruntime as ort

ROOT = Path(__file__).resolve().parent
DATOS_DIR = ROOT / "datasets"
MODELOS_DIR = ROOT

def load_features():
    f = next(MODELOS_DIR.glob("*features*_clean.json"), None)
    if not f:
        f = next(MODELOS_DIR.glob("*features*.json"), None)
    if not f:
        raise SystemExit("No features json found in modelos/")
    with open(f, "r", encoding="utf-8") as fh:
        feats = json.load(fh)
    return [s.strip() for s in feats]

def clean_colname(name):
    return name.strip().replace(" ", "_").replace("/", "_slash_").replace(".", "_dot_")

def sample_csv(feats, n):
    files = sorted(DATOS_DIR.glob("*.csv"))
    if not files:
        raise SystemExit("No CSV files found in datasets/")
    feats_clean = [clean_colname(f) for f in feats]
    for f in files:
        print(f"Intentando cargar: {f}")
        try:
            df = pd.read_csv(f, nrows=n, low_memory=False)
            df.columns = [clean_colname(c) for c in df.columns]
            # Verifica si todas las features están presentes
            if not all(feat in df.columns for feat in feats_clean):
                faltantes = [feat for feat in feats_clean if feat not in df.columns]
                print(f"Saltando {f}: faltan columnas {faltantes}")
                continue
            df = df[feats_clean]
            df = df.fillna(0).astype(np.float32)
            if len(df) == 0:
                print(f"Archivo {f} vacío tras filtrado de columnas.")
                continue
            print(f"Archivo {f} cargado con {len(df)} filas y columnas: {list(df.columns)}")
            return df
        except Exception as e:
            print(f"Saltando {f}: {e}")
            continue
    raise SystemExit("No CSV with required features found")

def get_session(onnx_path):
    so = ort.SessionOptions()
    try:
        sess = ort.InferenceSession(str(onnx_path), so, providers=["CPUExecutionProvider"])
    except Exception:
        sess = ort.InferenceSession(str(onnx_path))
    return sess

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--onnx", required=True)
    ap.add_argument("--pkl", required=True)
    ap.add_argument("--n-samples", type=int, default=100)
    args = ap.parse_args()

    feats = load_features()
    df = sample_csv(feats, args.n_samples)
    print(f"Shape de muestra cargada: {df.shape}")
    X = df.values.astype(np.float32)

    print("Cargando modelo sklearn...")
    clf = pickle.load(open(args.pkl, "rb"))

    try:
        proba_sklearn = clf.predict_proba(X)
    except Exception:
        proba_sklearn = None

    print("Cargando modelo ONNX...")
    sess = get_session(args.onnx)
    input_name = sess.get_inputs()[0].name
    ort_outs = sess.run(None, {input_name: X})

    onnx_shapes = [getattr(o, "shape", None) for o in ort_outs]
    print("ONNX outputs:", onnx_shapes)

    proba_onnx = None
    for o in ort_outs:
        if isinstance(o, np.ndarray):
            if o.ndim == 1:
                o2 = o.reshape(-1, 1)
            else:
                o2 = o
            if o2.ndim == 2:
                proba_onnx = o2
                break

    if proba_sklearn is None:
        print("sklearn model has no predict_proba; cannot compare numerically")
        return

    if proba_onnx is None:
        print("Could not find a 2D-like ONNX output to compare with predict_proba")
        return

    if proba_onnx.shape[1] == 1 and proba_sklearn.shape[1] == 2:
        skl_cmp = proba_sklearn[:, 1].reshape(-1, 1)
    else:
        skl_cmp = proba_sklearn[:, : proba_onnx.shape[1]]

    min_cols = min(skl_cmp.shape[1], proba_onnx.shape[1])
    diff = np.abs(skl_cmp[:, :min_cols] - proba_onnx[:, :min_cols])
    print("mean abs diff:", float(np.mean(diff)), "max diff:", float(np.max(diff)))

if __name__ == "__main__":
    main()