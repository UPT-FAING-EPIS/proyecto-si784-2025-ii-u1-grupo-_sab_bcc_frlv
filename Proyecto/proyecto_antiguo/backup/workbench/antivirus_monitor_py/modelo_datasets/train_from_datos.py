# --- Detección robusta de columna objetivo ---
def detect_label_from_files(files):
    candidates = [
        "label", "target", "class", "is_keylogger", "keylogger", "etiqueta", "y", "resultado", "Class"
    ]
    # intento heurístico usando cabeceras
    for f in files:
        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                header = fh.readline().strip().split(',')
                header = [clean_colname(h) for h in header]
                for c in candidates:
                    if clean_colname(c) in header:
                        return c
        except Exception:
            continue
    # fallback: comprobar la primera fila con pandas
    for f in files:
        try:
            h = pd.read_csv(f, nrows=1)
            h.columns = clean_colnames(h.columns)
            for c in candidates:
                if clean_colname(c) in h.columns:
                    return c
        except Exception:
            continue
    return None

# --- Lectura robusta de chunks numéricos ---
def iter_numeric_chunks(files, label_col, numeric_cols, max_rows=None, chunksize=100000, sample_frac=None):
    collected = 0
    parts = []
    clean_numeric_cols = clean_colnames(numeric_cols)
    clean_label_col = clean_colname(label_col)
    problematic_examples = {c: set() for c in clean_numeric_cols}
    for f in files:
        try:
            for chunk in pd.read_csv(f, chunksize=chunksize, low_memory=False):
                chunk.columns = clean_colnames(chunk.columns)
                cols_to_use = [c for c in chunk.columns if c in clean_numeric_cols or c == clean_label_col]
                chunk = chunk[cols_to_use]
                chunk = chunk.fillna(0)
                for c in clean_numeric_cols:
                    if c not in chunk.columns:
                        continue
                    coerced = pd.to_numeric(chunk[c], errors="coerce")
                    mask = coerced.isna() & chunk[c].notna()
                    if mask.any():
                        vals = chunk.loc[mask, c].astype(str).unique()[:5]
                        for v in vals:
                            if len(problematic_examples[c]) < 50:
                                problematic_examples[c].add(v)
                    chunk[c] = coerced.fillna(0).astype(np.float32)
                if sample_frac and sample_frac < 1.0:
                    chunk = chunk.sample(frac=sample_frac)
                parts.append(chunk)
                collected += len(chunk)
                if max_rows and max_rows > 0 and collected >= max_rows:
                    print(f"Collected ~{collected} rows (max_rows reached)")
                    dfret = pd.concat(parts, ignore_index=True)[:max_rows]
                    dfret._problematic_examples = {k: list(v) for k, v in problematic_examples.items() if v}
                    return dfret
        except Exception as e:
            print(f"Skipping file {f} due to read error: {e}")
            continue
    if parts:
        combined = pd.concat(parts, ignore_index=True)
        if max_rows and max_rows > 0 and len(combined) > max_rows:
            combined = combined[:max_rows]
        combined._problematic_examples = {k: list(v) for k, v in problematic_examples.items() if v}
        return combined
    return pd.DataFrame()

import glob
import json
import pickle
import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

ROOT = Path(__file__).resolve().parents[1]
DATOS_DIR = ROOT / "modelo_datasets" / "datasets"
MODELOS_DIR = ROOT / "modelo_datasets"
MODELOS_DIR.mkdir(parents=True, exist_ok=True)

# --- Utilidad para limpiar nombres de columnas/features ---
def clean_colname(name):
    return name.strip().replace(" ", "_").replace("/", "_slash_").replace(".", "_dot_")

def clean_colnames(cols):
    return [clean_colname(c) for c in cols]

# --- Definición de main() a nivel global y llamada en el if ---
def main():
    parser = argparse.ArgumentParser(description="Entrenar modelo a partir de CSVs en DATOS/")
    parser.add_argument("--max-rows", type=int, default=200000, help="max rows to load (use 0 for no limit)")
    parser.add_argument("--sample-frac", type=float, default=1.0, help="sample fraction to apply to chunks (0-1)")
    parser.add_argument("--incremental", action="store_true", help="use SGDClassifier with partial_fit instead of RandomForest")
    parser.add_argument("--onnx", action="store_true", help="attempt ONNX conversion if skl2onnx present")
    parser.add_argument("--inspect", action="store_true", help="inspect numeric columns for non-numeric examples and exit")
    parser.add_argument("--rf-n-estimators", type=int, default=200, help="n_estimators for RandomForest (when not --incremental)")
    parser.add_argument("--rf-class-weight", default="balanced", help="class_weight for RandomForest (None or 'balanced' or dict)")
    parser.add_argument("--chunksize", type=int, default=100000, help="chunk size for reading CSVs")
    args = parser.parse_args()

    files = sorted(glob.glob(str(DATOS_DIR / "*.csv")))
    if not files:
        print(f"No se encontraron archivos CSV en {DATOS_DIR}")
        sys.exit(1)

    print(f"Se encontraron {len(files)} archivos CSV")

    label_col = detect_label_from_files(files)
    if label_col is None:
        print("No se pudo detectar automáticamente la columna objetivo. Añade una columna 'Class' o 'label'.")
        sys.exit(2)
    print(f"Usando '{label_col}' como columna objetivo")

    numeric_cols = detect_numeric_columns(files, label_col)
    if not numeric_cols:
        print("No se detectaron columnas de características numéricas en las cabeceras de muestra. Saliendo.")
        sys.exit(3)
    print(f"Detectadas {len(numeric_cols)} columnas de features numéricas (detección con primeras filas)")

    if args.inspect:
        inspect_columns(files, label_col, numeric_cols, max_scan_rows=args.max_rows, chunksize=args.chunksize)
        sys.exit(0)

    # Limpiar nombres de columnas/features para uso consistente
    clean_numeric_cols = clean_colnames(numeric_cols)
    clean_label_col = clean_colname(label_col)

    # If dataset big, sample while reading chunks until max_rows
    df = iter_numeric_chunks(files, label_col, numeric_cols, max_rows=args.max_rows, chunksize=args.chunksize, sample_frac=(args.sample_frac if args.sample_frac>0 else None))
    if df.empty:
        print("No se recolectaron datos de los CSVs.")
        sys.exit(4)

    # separate X/y
    X = df[clean_numeric_cols].astype(np.float32).fillna(0)
    y_raw = df[clean_label_col].fillna("")

    le = LabelEncoder()
    y = le.fit_transform(y_raw)

    # save label encoder mapping
    labels_path = MODELOS_DIR / "label_classes.json"
    with open(labels_path, "w", encoding="utf-8") as fh:
        json.dump(list(le.classes_), fh, ensure_ascii=False, indent=2)
    print(f"Guardadas clases de etiqueta en {labels_path}")

    if args.incremental:
        # prepare classes for partial_fit by scanning a small sample of labels across files
        classes = list(le.classes_)
        clf = SGDClassifier(random_state=42)
        # partial_fit in one go using small batches from df
        batch_size = min(10000, len(X))
        for start in range(0, len(X), batch_size):
            end = start + batch_size
            Xb = X.iloc[start:end].values
            yb = y[start:end]
            if start == 0:
                clf.partial_fit(Xb, yb, classes=np.arange(len(classes)))
            else:
                clf.partial_fit(Xb, yb)
        # evaluate on held-out split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y if len(set(y))>1 else None)
        y_pred = clf.predict(X_test)
    else:
        # non-incremental: train/test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y if len(set(y))>1 else None)
        # configure RandomForest with provided params
        cw = None if args.rf_class_weight == "None" else args.rf_class_weight
        try:
            # allow dict-like strings? keep simple: 'balanced' or None
            clf = RandomForestClassifier(n_estimators=args.rf_n_estimators, class_weight=cw, random_state=42, n_jobs=-1)
        except Exception:
            clf = RandomForestClassifier(n_estimators=args.rf_n_estimators, class_weight="balanced", random_state=42, n_jobs=-1)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy en test: {acc:.4f}")
    print(classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0))

    # save model and features
    pkl_path = MODELOS_DIR / ("modelo_keylogger_from_datos_incremental.pkl" if args.incremental else "modelo_keylogger_from_datos.pkl")
    with open(pkl_path, "wb") as f:
        pickle.dump(clf, f)
    print(f"Guardado modelo en {pkl_path}")

    features_path = MODELOS_DIR / ("modelo_keylogger_from_datos_features.json")
    with open(features_path, "w", encoding="utf-8") as f:
        json.dump(clean_numeric_cols, f, ensure_ascii=False, indent=2)
    print(f"Guardada lista de features en {features_path}")

    if args.onnx:
        try:
            from skl2onnx import convert_sklearn
            from skl2onnx.common.data_types import FloatTensorType

            initial_type = [("float_input", FloatTensorType([None, len(clean_numeric_cols)]))]
            onnx_model = convert_sklearn(clf, initial_types=initial_type)
            onnx_path = MODELOS_DIR / ("modelo_keylogger_from_datos.onnx")
            with open(onnx_path, "wb") as f:
                f.write(onnx_model.SerializeToString())
            print(f"Guardado modelo ONNX en {onnx_path}")
        except Exception as e:
            print("Conversión ONNX omitida o fallida; instala 'skl2onnx' para habilitar la conversión.")
            print("Error de conversión:", e)



# --- Reparar función detect_numeric_columns ---
def detect_numeric_columns(files, label_col, nrows=1000):
    numeric = None
    clean_label = clean_colname(label_col)
    for f in files:
        try:
            sample = pd.read_csv(f, nrows=nrows, low_memory=False)
            sample.columns = clean_colnames(sample.columns)
            if clean_label not in sample.columns:
                continue
            numeric = [c for c in sample.columns if c != clean_label and pd.api.types.is_numeric_dtype(sample[c])]
            if numeric:
                return numeric
        except Exception:
            continue
    return []

if __name__ == "__main__":
    main()


def inspect_columns(files, label_col, numeric_cols, max_scan_rows=200000, chunksize=100000):
    """Escanea los CSVs e informa ejemplos no numéricos en columnas numéricas."""
    print("Inspeccionando columnas numéricas en busca de valores no numéricos...")
    problems = {c: set() for c in numeric_cols}
    scanned = 0
    for f in files:
        try:
            for chunk in pd.read_csv(f, usecols=numeric_cols + [label_col], chunksize=chunksize, low_memory=False):
                for c in numeric_cols:
                    coerced = pd.to_numeric(chunk[c], errors='coerce')
                    mask = coerced.isna() & chunk[c].notna()
                    if mask.any():
                        vals = chunk.loc[mask, c].astype(str).unique()[:20]
                        problems[c].update(vals.tolist())
                        # limit stored examples
                        if len(problems[c]) > 200:
                            problems[c] = set(list(problems[c])[:200])
                scanned += len(chunk)
                if scanned >= max_scan_rows:
                    print(f"Inspeccionadas ~{scanned} filas (max_scan_rows)")
                    break
        except Exception as e:
            print(f"Inspect read error for {f}: {e}")
            continue
    # summarize
    summary = {c: list(v) for c, v in problems.items() if v}
    if not summary:
        print("No se detectaron valores no numéricos problemáticos en columnas numéricas.")
    else:
        print("Columnas problemáticas y valores de ejemplo (truncado):")
        for c, vals in summary.items():
            print(f" - {c}: {len(vals)} ejemplos no numéricos distintos, muestra: {vals[:5]}")
    # save to modelos
    out_path = MODELOS_DIR / "problematic_columns.json"
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(f"Guardado informe de columnas problemáticas en {out_path}")
    return summary
