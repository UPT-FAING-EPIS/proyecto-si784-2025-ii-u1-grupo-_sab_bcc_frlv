"""
Entrenar con Dataset Grande
===========================

Entrena un modelo más robusto con el dataset grande procesado.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
import pickle
import json

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def train_large_model():
    """Entrena modelo con dataset grande"""
    logger.info("[START] Entrenando modelo con dataset grande...")
    
    # Cargar datos grandes
    # Obtener el directorio base del proyecto (dos niveles arriba)
    base_dir = Path(__file__).parent.parent.parent
    data_file = base_dir / "data" / "processed" / "dataset_large_sample.parquet"
    if not data_file.exists():
        logger.error("[ERROR] No se encontró dataset grande procesado")
        return False
    
    df = pd.read_parquet(data_file)
    logger.info(f"[DATA] Datos cargados: {len(df):,} filas, {df.shape[1]} columnas")
    
    # Preparar datos
    X = df.drop(columns=['Class'])
    y = df['Class']
    
    # Codificar target
    if y.dtype == 'object':
        le = LabelEncoder()
        y = le.fit_transform(y)
        logger.info(f"   Target codificado: {list(le.classes_)}")
    
    # Solo columnas numéricas
    X_numeric = X.select_dtypes(include=[np.number])
    logger.info(f"   Features numéricas: {X_numeric.shape[1]}")
    
    # Split datos
    X_train, X_test, y_train, y_test = train_test_split(
        X_numeric, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"   Train: {len(X_train):,}, Test: {len(X_test):,}")
    
    # Distribución de clases
    unique, counts = np.unique(y_train, return_counts=True)
    logger.info(f"   Distribución train: {dict(zip(unique, counts))}")
    
    # Entrenar modelo más robusto
    logger.info("   [SYNC] Entrenando Random Forest robusto...")
    model = RandomForestClassifier(
        n_estimators=200,  # Más árboles
        max_depth=20,      # Más profundidad
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluar
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    y_pred = model.predict(X_test)
    
    logger.info(f"   [STATS] Accuracy Train: {train_score:.4f}")
    logger.info(f"   [STATS] Accuracy Test: {test_score:.4f}")
    
    # Métricas detalladas
    report = classification_report(y_test, y_pred, output_dict=True)
    f1_score = report['weighted avg']['f1-score']
    precision = report['weighted avg']['precision']
    recall = report['weighted avg']['recall']
    
    logger.info(f"   [STATS] F1-Score: {f1_score:.4f}")
    logger.info(f"   [STATS] Precision: {precision:.4f}")
    logger.info(f"   [STATS] Recall: {recall:.4f}")
    
    # Matriz de confusión
    cm = confusion_matrix(y_test, y_pred)
    logger.info(f"   [DATA] Matriz confusión:\n{cm}")
    
    # Feature importance top 10
    feature_importance = model.feature_importances_
    feature_names = X_numeric.columns
    
    # Top 10 features
    top_indices = np.argsort(feature_importance)[-10:][::-1]
    logger.info("   🔝 Top 10 Features más importantes:")
    for i, idx in enumerate(top_indices):
        logger.info(f"      {i+1:2d}. {feature_names[idx]}: {feature_importance[idx]:.4f}")
    
    # Guardar modelo
    # Obtener el directorio base del proyecto (dos niveles arriba)
    base_dir = Path(__file__).parent.parent.parent
    models_dir = base_dir / "models" / "development"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_file = models_dir / f"rf_large_model_{timestamp}.pkl"
    
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)
    
    # Guardar metadatos extendidos
    metadata = {
        'model_type': 'RandomForestClassifier_Large',
        'features': list(X_numeric.columns),
        'target_column': 'Class',
        'train_accuracy': train_score,
        'test_accuracy': test_score,
        'f1_score': f1_score,
        'precision': precision,
        'recall': recall,
        'confusion_matrix': cm.tolist(),
        'feature_importance': dict(zip(feature_names, feature_importance)),
        'top_features': [(feature_names[idx], float(feature_importance[idx])) for idx in top_indices],
        'model_params': {
            'n_estimators': 200,
            'max_depth': 20,
            'min_samples_split': 5,
            'min_samples_leaf': 2
        },
        'data_info': {
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'total_features': X_numeric.shape[1],
            'original_shape': df.shape
        },
        'timestamp': timestamp
    }
    
    metadata_file = models_dir / f"rf_large_metadata_{timestamp}.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    logger.info(f"   [OK] Modelo grande guardado: {model_file}")
    logger.info(f"   [OK] Metadatos guardados: {metadata_file}")
    
    return True, model_file, metadata

if __name__ == "__main__":
    success, model_path, metadata = train_large_model()
    
    if success:
        print("\n" + "="*60)
        print("🏆 MODELO GRANDE ENTRENADO EXITOSAMENTE")
        print("="*60)
        print(f"[DATA] Dataset: {metadata['data_info']['train_samples'] + metadata['data_info']['test_samples']:,} muestras")
        print(f"[STATS] Accuracy: {metadata['test_accuracy']:.4f}")
        print(f"[STATS] F1-Score: {metadata['f1_score']:.4f}")
        print(f"🔝 Mejor feature: {metadata['top_features'][0][0]}")
        print(f"📂 Modelo guardado: {model_path}")
        print("="*60)