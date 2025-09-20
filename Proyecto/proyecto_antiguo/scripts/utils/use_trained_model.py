"""
Usar Modelo Entrenado - Predicciones Individuales
=================================================

Script para hacer predicciones con el modelo entrenado.
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import json

def load_trained_model():
    """Carga el modelo más reciente"""
    # Obtener el directorio base del proyecto (dos niveles arriba)
    base_dir = Path(__file__).parent.parent.parent
    models_dir = base_dir / "models" / "development"
    
    # Buscar modelo más reciente
    model_files = list(models_dir.glob("rf_model_*.pkl"))
    if not model_files:
        print("[ERROR] No se encontraron modelos entrenados")
        return None, None
    
    latest_model_file = max(model_files, key=lambda x: x.stat().st_mtime)
    
    # Cargar modelo
    with open(latest_model_file, 'rb') as f:
        model = pickle.load(f)
    
    # Cargar metadatos
    metadata_file = models_dir / latest_model_file.name.replace('rf_model_', 'rf_metadata_').replace('.pkl', '.json')
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = {}
    
    print(f"[OK] Modelo cargado: {latest_model_file.name}")
    if metadata:
        print(f"[DATA] Accuracy: {metadata.get('test_accuracy', 'N/A'):.4f}")
        print(f"[DATA] F1-Score: {metadata.get('f1_score', 'N/A'):.4f}")
    
    return model, metadata

def predict_sample_data(model, metadata):
    """Hacer predicciones con datos de muestra"""
    # Cargar datos procesados
    processed_dir = Path("data/processed")
    data_file = processed_dir / "dataset_small_clean.parquet"
    
    if not data_file.exists():
        print("[ERROR] No se encontraron datos procesados")
        return
    
    df = pd.read_parquet(data_file)
    
    # Preparar features (solo numéricas)
    X = df.drop(columns=['Class'])
    X_numeric = X.select_dtypes(include=[np.number])
    
    # Tomar una muestra pequeña
    sample_size = 10
    X_sample = X_numeric.head(sample_size)
    y_true = df['Class'].head(sample_size)
    
    # Hacer predicciones
    predictions = model.predict(X_sample)
    probabilities = model.predict_proba(X_sample)
    
    print(f"\n[TARGET] Predicciones de muestra ({sample_size} casos):")
    print("-" * 50)
    
    for i in range(sample_size):
        pred_class = "Keylogger" if predictions[i] == 1 else "Benign"
        true_class = y_true.iloc[i]
        confidence = np.max(probabilities[i])
        correct = "[OK]" if pred_class == true_class else "[ERROR]"
        
        print(f"{i+1:2d}. Real: {true_class:9s} | Pred: {pred_class:9s} | Conf: {confidence:.3f} {correct}")

def main():
    print("[ML] USAR MODELO ENTRENADO")
    print("=" * 40)
    
    # Cargar modelo
    model, metadata = load_trained_model()
    
    if model is not None:
        # Hacer predicciones de ejemplo
        predict_sample_data(model, metadata)
        
        print(f"\n[INFO] Para usar el modelo en tu código:")
        print(f"   import pickle")
        print(f"   with open('models/development/rf_model_XXXXXX.pkl', 'rb') as f:")
        print(f"       model = pickle.load(f)")
        print(f"   predictions = model.predict(tu_data)")

if __name__ == "__main__":
    main()