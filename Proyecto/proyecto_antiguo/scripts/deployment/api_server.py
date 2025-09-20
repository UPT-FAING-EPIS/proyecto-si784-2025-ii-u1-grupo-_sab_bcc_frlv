"""
API REST para Modelo Anti-Keylogger
===================================

Servidor FastAPI para servir predicciones del modelo entrenado.
"""

import pickle
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Modelos de entrada
class SinglePredictionInput(BaseModel):
    features: List[float]
    feature_names: List[str] = []

class BatchPredictionInput(BaseModel):
    batch_features: List[List[float]]
    feature_names: List[str] = []

class PredictionResponse(BaseModel):
    prediction: int
    prediction_label: str
    confidence: float
    probabilities: List[float]
    timestamp: str

# Cargar modelo al iniciar
def load_model():
    """Carga el modelo más reciente"""
    # Obtener el directorio base del proyecto (dos niveles arriba)
    base_dir = Path(__file__).parent.parent.parent
    models_dir = base_dir / "models" / "development"
    
    model_files = list(models_dir.glob("rf_model_*.pkl"))
    if not model_files:
        raise Exception("No se encontraron modelos entrenados")
    
    latest_model_file = max(model_files, key=lambda x: x.stat().st_mtime)
    
    with open(latest_model_file, 'rb') as f:
        model = pickle.load(f)
    
    # Cargar metadatos
    metadata_file = models_dir / latest_model_file.name.replace('rf_model_', 'rf_metadata_').replace('.pkl', '.json')
    metadata = {}
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    
    return model, metadata, str(latest_model_file)

# Inicializar FastAPI
app = FastAPI(
    title="Anti-Keylogger ML API",
    description="API para detectar keyloggers usando Machine Learning",
    version="1.0.0"
)

# Cargar modelo globalmente
try:
    MODEL, METADATA, MODEL_PATH = load_model()
    FEATURE_NAMES = METADATA.get('features', [])
    print(f"[OK] Modelo cargado: {Path(MODEL_PATH).name}")
    print(f"[DATA] Accuracy: {METADATA.get('test_accuracy', 'N/A')}")
    print(f"[DATA] Features: {len(FEATURE_NAMES)}")
except Exception as e:
    print(f"[ERROR] Error cargando modelo: {e}")
    MODEL = None

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Anti-Keylogger ML API",
        "status": "running",
        "model_loaded": MODEL is not None,
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check del servicio"""
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    return {
        "status": "healthy",
        "model_path": MODEL_PATH,
        "model_accuracy": METADATA.get('test_accuracy', 'N/A'),
        "features_count": len(FEATURE_NAMES),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/model/info")
async def model_info():
    """Información detallada del modelo"""
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    return {
        "model_path": MODEL_PATH,
        "model_type": "RandomForestClassifier",
        "features": FEATURE_NAMES,
        "metadata": METADATA,
        "classes": ["Benign", "Keylogger"]
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_single(input_data: SinglePredictionInput):
    """Predicción individual"""
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        # Convertir a numpy array
        features = np.array(input_data.features).reshape(1, -1)
        
        # Validar dimensiones
        if features.shape[1] != len(FEATURE_NAMES):
            raise HTTPException(
                status_code=400, 
                detail=f"Número incorrecto de features. Esperado: {len(FEATURE_NAMES)}, Recibido: {features.shape[1]}"
            )
        
        # Hacer predicción
        prediction = MODEL.predict(features)[0]
        probabilities = MODEL.predict_proba(features)[0]
        
        response = PredictionResponse(
            prediction=int(prediction),
            prediction_label="Keylogger" if prediction == 1 else "Benign",
            confidence=float(np.max(probabilities)),
            probabilities=probabilities.tolist(),
            timestamp=datetime.now().isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en predicción: {str(e)}")

@app.post("/predict/batch")
async def predict_batch(input_data: BatchPredictionInput):
    """Predicción en lote"""
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        # Convertir a numpy array
        features = np.array(input_data.batch_features)
        
        # Validar dimensiones
        if features.shape[1] != len(FEATURE_NAMES):
            raise HTTPException(
                status_code=400, 
                detail=f"Número incorrecto de features. Esperado: {len(FEATURE_NAMES)}, Recibido: {features.shape[1]}"
            )
        
        # Hacer predicciones
        predictions = MODEL.predict(features)
        probabilities = MODEL.predict_proba(features)
        
        results = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            result = {
                "sample_index": i,
                "prediction": int(pred),
                "prediction_label": "Keylogger" if pred == 1 else "Benign",
                "confidence": float(np.max(prob)),
                "probabilities": prob.tolist()
            }
            results.append(result)
        
        return {
            "predictions": results,
            "total_samples": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en predicción batch: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Estadísticas del modelo"""
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    return {
        "model_stats": METADATA,
        "api_info": {
            "total_features": len(FEATURE_NAMES),
            "model_type": "RandomForestClassifier",
            "supported_formats": ["single", "batch"],
            "max_batch_size": 1000
        },
        "timestamp": datetime.now().isoformat()
    }

def main():
    """Ejecuta el servidor"""
    print("[START] Iniciando API REST para Anti-Keylogger ML...")
    print("=" * 50)
    
    if MODEL is None:
        print("[ERROR] No se puede iniciar: modelo no cargado")
        return
    
    print(f"[ML] Modelo: {Path(MODEL_PATH).name}")
    print(f"[DATA] Accuracy: {METADATA.get('test_accuracy', 'N/A'):.4f}")
    print(f"[NET] Servidor: http://localhost:8000")
    print(f"📖 Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()