import pickle
import pandas as pd
import json

def clean_colname(name):
    return name.strip().replace(" ", "_").replace("/", "_slash_").replace(".", "_dot_")

# Carga el modelo
with open('modelo_keylogger_from_datos.pkl', 'rb') as f:
    clf = pickle.load(f)

# Carga las features y limpia espacios
with open('modelo_keylogger_from_datos_features.json', encoding='utf-8') as f:
    feats = [clean_colname(c) for c in json.load(f)]

# Carga un CSV de prueba
df = pd.read_csv('datasets/Keylogger_Detection.csv', nrows=5)
df.columns = [clean_colname(c) for c in df.columns]
X = df[feats].fillna(0).astype('float32')

# Haz predicción
print(clf.predict(X))
print(clf.predict_proba(X))