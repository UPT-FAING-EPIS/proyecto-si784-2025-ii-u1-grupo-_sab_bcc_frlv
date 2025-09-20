import pickle
import json
import pandas as pd
from pathlib import Path

# Rutas relativas desde antivirus_monitor_py
MODELO_PATH = Path('modelo_datasets/modelo_keylogger_from_datos.pkl')
FEATURES_PATH = Path('modelo_datasets/modelo_keylogger_from_datos_features.json')
LABELS_PATH = Path('modelo_datasets/label_classes.json')

def clean_colname(name):
    return name.strip().replace(' ', '_').replace('/', '_slash_').replace('.', '_dot_')

def main():
    # Cargar modelo
    with open(MODELO_PATH, 'rb') as f:
        clf = pickle.load(f)
    # Cargar features
    with open(FEATURES_PATH, encoding='utf-8') as f:
        feats = [clean_colname(c) for c in json.load(f)]
    # Cargar clases
    try:
        with open(LABELS_PATH, encoding='utf-8') as f:
            classes = json.load(f)
    except Exception:
        classes = None
    # Pedir CSV o datos por consola
    print('Introduce la ruta de un CSV para predecir (o ENTER para usar datasets/Keylogger_Detection.csv):')
    ruta = input().strip() or 'modelo_datasets/datasets/Keylogger_Detection.csv'
    df = pd.read_csv(ruta)
    df.columns = [clean_colname(c) for c in df.columns]
    # Chequeo de columnas no numéricas
    non_numeric = {}
    X = pd.DataFrame()
    for col in feats:
        if col in df.columns:
            vals = df[col].dropna().astype(str)
            bad_vals = vals[~vals.str.replace('.', '', 1).str.replace('-', '', 1).str.isnumeric()]
            if not bad_vals.empty:
                non_numeric[col] = bad_vals.unique()[:5]
                # Rellenar con 0 si hay valores no numéricos
                X[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                X[col] = df[col].fillna(0)
        else:
            # Columna faltante, rellenar con 0
            X[col] = 0
    if non_numeric:
        print('¡Advertencia! Se detectaron columnas/features no numéricas en el CSV y serán rellenadas con 0:')
        for col, vals in non_numeric.items():
            print(f" - {col}: ejemplos de valores no numéricos: {list(vals)}")
        print(f"Se usará el set completo de features, rellenando problemáticas/faltantes con 0.")
    X = X[feats].astype('float32')
    # Predecir
    y_pred = clf.predict(X)
    y_proba = clf.predict_proba(X)
    print('Predicciones:')
    if classes:
        print([classes[i] for i in y_pred])
    else:
        print(y_pred)
    print('Probabilidades (primeras 5 filas):')
    print(y_proba[:5])

if __name__ == '__main__':
    main()
