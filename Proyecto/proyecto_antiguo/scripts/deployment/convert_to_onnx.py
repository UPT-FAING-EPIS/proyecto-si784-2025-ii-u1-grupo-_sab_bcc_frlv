"""
Conversión de Modelo a ONNX
============================

Convierte el modelo entrenado a formato ONNX para deployment optimizado.
"""

import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
import logging
from datetime import datetime

# ONNX dependencies
try:
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
    import onnxruntime as ort
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_model_to_onnx():
    """Convierte el modelo más reciente a ONNX"""
    if not HAS_ONNX:
        logger.error("[ERROR] ONNX no disponible. Instala con: pip install skl2onnx onnxruntime")
        return False
    
    logger.info("[SYNC] Iniciando conversión a ONNX...")
    
    # Buscar modelo más reciente
    # Obtener el directorio base del proyecto (dos niveles arriba)
    base_dir = Path(__file__).parent.parent.parent
    models_dir = base_dir / "models" / "development"
    large_models = list(models_dir.glob("rf_large_model_*.pkl"))
    regular_models = list(models_dir.glob("rf_model_*.pkl"))
    
    if large_models:
        model_files = large_models
        model_type = "large"
    elif regular_models:
        model_files = regular_models
        model_type = "regular"
    else:
        logger.error("[ERROR] No se encontraron modelos")
        return False
    
    latest_model_file = max(model_files, key=lambda x: x.stat().st_mtime)
    logger.info(f"[PACKAGE] Convirtiendo: {latest_model_file.name}")
    
    # Cargar modelo
    with open(latest_model_file, 'rb') as f:
        model = pickle.load(f)
    
    # Cargar metadatos para obtener información de features
    if model_type == "large":
        metadata_file = models_dir / latest_model_file.name.replace('rf_large_model_', 'rf_large_metadata_').replace('.pkl', '.json')
    else:
        metadata_file = models_dir / latest_model_file.name.replace('rf_model_', 'rf_metadata_').replace('.pkl', '.json')
    
    metadata = {}
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    
    # Obtener número de features
    if 'features' in metadata:
        n_features = len(metadata['features'])
        feature_names = metadata['features']
    else:
        # Cargar datos para inferir
        data_file = Path("data/processed") / ("dataset_large_sample.parquet" if model_type == "large" else "dataset_small_clean.parquet")
        if data_file.exists():
            df = pd.read_parquet(data_file)
            X = df.drop(columns=['Class'])
            X_numeric = X.select_dtypes(include=[np.number])
            n_features = X_numeric.shape[1]
            feature_names = list(X_numeric.columns)
        else:
            logger.error("[ERROR] No se pudo determinar el número de features")
            return False
    
    logger.info(f"[DATA] Features: {n_features}")
    
    try:
        # Definir tipo de entrada
        initial_type = [('float_input', FloatTensorType([None, n_features]))]
        
        # Convertir a ONNX
        logger.info("[SYNC] Convirtiendo a ONNX...")
        onnx_model = convert_sklearn(model, initial_types=initial_type)
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        onnx_filename = f"keylogger_model_{model_type}_{timestamp}.onnx"
        onnx_path = models_dir / onnx_filename
        
        # Guardar modelo ONNX
        with open(onnx_path, "wb") as f:
            f.write(onnx_model.SerializeToString())
        
        logger.info(f"[OK] Modelo ONNX guardado: {onnx_path}")
        
        # Verificar el modelo ONNX
        logger.info("[SEARCH] Verificando modelo ONNX...")
        ort_session = ort.InferenceSession(str(onnx_path))
        
        # Información del modelo
        input_info = ort_session.get_inputs()[0]
        output_info = ort_session.get_outputs()
        
        logger.info(f"   Input: {input_info.name}, Shape: {input_info.shape}, Type: {input_info.type}")
        logger.info(f"   Outputs: {len(output_info)}")
        for i, output in enumerate(output_info):
            logger.info(f"     Output {i}: {output.name}, Shape: {output.shape}, Type: {output.type}")
        
        # Prueba con datos sintéticos
        logger.info("🧪 Probando con datos sintéticos...")
        test_input = np.random.rand(1, n_features).astype(np.float32)
        
        try:
            onnx_results = ort_session.run(None, {input_info.name: test_input})
            
            # Comparar con modelo original
            sklearn_pred = model.predict(test_input)
            sklearn_proba = model.predict_proba(test_input)
            
            onnx_pred = onnx_results[0]
            onnx_proba = onnx_results[1] if len(onnx_results) > 1 else None
            
            pred_match = np.array_equal(sklearn_pred, onnx_pred.flatten())
            logger.info(f"   Predicciones coinciden: {'[OK]' if pred_match else '[ERROR]'}")
            
            if onnx_proba is not None:
                proba_close = np.allclose(sklearn_proba, onnx_proba, rtol=1e-4)
                logger.info(f"   Probabilidades coinciden: {'[OK]' if proba_close else '[ERROR]'}")
            
        except Exception as e:
            logger.warning(f"[WARNING]  Error en prueba: {e}")
        
        # Guardar metadatos del modelo ONNX
        onnx_metadata = {
            'original_model': str(latest_model_file),
            'onnx_model': str(onnx_path),
            'conversion_timestamp': timestamp,
            'model_type': model_type,
            'n_features': n_features,
            'feature_names': feature_names,
            'input_shape': [None, n_features],
            'input_name': input_info.name,
            'output_names': [output.name for output in output_info],
            'onnx_runtime_version': ort.__version__,
            'original_metadata': metadata
        }
        
        onnx_metadata_file = models_dir / f"onnx_metadata_{model_type}_{timestamp}.json"
        with open(onnx_metadata_file, 'w') as f:
            json.dump(onnx_metadata, f, indent=2, default=str)
        
        logger.info(f"[OK] Metadatos ONNX guardados: {onnx_metadata_file}")
        
        # Resumen final
        logger.info("[INFO] Conversión ONNX completada:")
        logger.info(f"   [PACKAGE] Modelo original: {latest_model_file.name}")
        logger.info(f"   [FIX] Modelo ONNX: {onnx_filename}")
        logger.info(f"   [DATA] Features: {n_features}")
        logger.info(f"   [FILE] Ubicación: {onnx_path}")
        
        return True, onnx_path, onnx_metadata
        
    except Exception as e:
        logger.error(f"[ERROR] Error en conversión ONNX: {e}")
        return False, None, None

def test_onnx_performance():
    """Prueba el rendimiento del modelo ONNX vs sklearn"""
    logger.info("⚡ Comparando rendimiento ONNX vs sklearn...")
    
    # Buscar modelo ONNX más reciente
    # Obtener el directorio base del proyecto (dos niveles arriba)
    base_dir = Path(__file__).parent.parent.parent
    models_dir = base_dir / "models" / "development"
    onnx_files = list(models_dir.glob("keylogger_model_*.onnx"))
    
    if not onnx_files:
        logger.error("[ERROR] No se encontraron modelos ONNX")
        return
    
    latest_onnx = max(onnx_files, key=lambda x: x.stat().st_mtime)
    
    # Buscar modelo sklearn correspondiente
    if "large" in latest_onnx.name:
        pkl_files = list(models_dir.glob("rf_large_model_*.pkl"))
    else:
        pkl_files = list(models_dir.glob("rf_model_*.pkl"))
    
    if not pkl_files:
        logger.error("[ERROR] No se encontró modelo sklearn correspondiente")
        return
    
    latest_pkl = max(pkl_files, key=lambda x: x.stat().st_mtime)
    
    # Cargar modelos
    with open(latest_pkl, 'rb') as f:
        sklearn_model = pickle.load(f)
    
    ort_session = ort.InferenceSession(str(latest_onnx))
    input_name = ort_session.get_inputs()[0].name
    
    # Generar datos de prueba
    n_samples = 1000
    n_features = ort_session.get_inputs()[0].shape[1]
    test_data = np.random.rand(n_samples, n_features).astype(np.float32)
    
    # Medir tiempo sklearn
    import time
    
    start_time = time.time()
    sklearn_predictions = sklearn_model.predict(test_data)
    sklearn_time = time.time() - start_time
    
    # Medir tiempo ONNX
    start_time = time.time()
    onnx_results = ort_session.run(None, {input_name: test_data})
    onnx_predictions = onnx_results[0].flatten()
    onnx_time = time.time() - start_time
    
    # Comparar resultados
    accuracy_match = np.mean(sklearn_predictions == onnx_predictions)
    speedup = sklearn_time / onnx_time
    
    logger.info(f"[DATA] Resultados de rendimiento:")
    logger.info(f"   Muestras: {n_samples:,}")
    logger.info(f"   Tiempo sklearn: {sklearn_time:.4f}s")
    logger.info(f"   Tiempo ONNX: {onnx_time:.4f}s")
    logger.info(f"   Speedup: {speedup:.2f}x")
    logger.info(f"   Precisión: {accuracy_match:.2%}")

def main():
    """Función principal"""
    print("[FIX] CONVERSIÓN A ONNX")
    print("=" * 40)
    
    # Convertir modelo
    success, onnx_path, metadata = convert_model_to_onnx()
    
    if success:
        print(f"\n[OK] Conversión exitosa!")
        print(f"[PACKAGE] Modelo ONNX: {onnx_path}")
        
        # Probar rendimiento
        test_onnx_performance()
        
        print(f"\n[INFO] Para usar el modelo ONNX:")
        print(f"   import onnxruntime as ort")
        print(f"   session = ort.InferenceSession('{onnx_path}')")
        print(f"   result = session.run(None, {{'float_input': your_data}})")
    else:
        print("[ERROR] Error en conversión")

if __name__ == "__main__":
    main()