"""
Sistema de Inferencia y Deployment - Anti-Keylogger
===================================================

Este módulo proporciona capacidades de inferencia para modelos entrenados:
- Predicción en tiempo real
- Batch prediction
- API de predicción
- Monitoreo de rendimiento
- Validación de entrada
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
import logging
import json
import pickle
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ONNX runtime
try:
    import onnxruntime as ort
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False

# FastAPI para crear API de predicción
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelPredictor:
    """Predictor para modelos de detección de keyloggers."""
    
    def __init__(self, model_path: Path, metadata_path: Optional[Path] = None):
        self.model_path = Path(model_path)
        self.model = None
        self.model_type = None
        self.feature_names = []
        self.metadata = {}
        
        # Cargar modelo
        self._load_model()
        
        # Cargar metadata si está disponible
        if metadata_path:
            self._load_metadata(metadata_path)
        
        # Estadísticas de uso
        self.prediction_count = 0
        self.batch_count = 0
        self.error_count = 0
        
    def _load_model(self):
        """Carga el modelo desde archivo."""
        if self.model_path.suffix == '.pkl':
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            self.model_type = 'sklearn'
        elif self.model_path.suffix == '.onnx' and HAS_ONNX:
            self.model = ort.InferenceSession(str(self.model_path))
            self.model_type = 'onnx'
        else:
            raise ValueError(f"Formato de modelo no soportado: {self.model_path.suffix}")
        
        logger.info(f"Modelo cargado: {self.model_path.name} (tipo: {self.model_type})")
    
    def _load_metadata(self, metadata_path: Path):
        """Carga metadatos del modelo."""
        try:
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
            
            self.feature_names = self.metadata.get('feature_names', [])
            logger.info(f"Metadatos cargados: {len(self.feature_names)} features")
        except Exception as e:
            logger.warning(f"Error cargando metadatos: {e}")
    
    def validate_input(self, X: np.ndarray) -> Tuple[bool, str]:
        """Valida que la entrada tenga el formato correcto."""
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Verificar dimensiones
        if self.feature_names and X.shape[1] != len(self.feature_names):
            return False, f"Número incorrecto de features. Esperado: {len(self.feature_names)}, Recibido: {X.shape[1]}"
        
        # Verificar valores faltantes
        if np.isnan(X).any():
            return False, "La entrada contiene valores NaN"
        
        # Verificar valores infinitos
        if np.isinf(X).any():
            return False, "La entrada contiene valores infinitos"
        
        return True, "OK"
    
    def predict_single(self, X: np.ndarray) -> Dict[str, Any]:
        """Realiza predicción para una sola muestra."""
        try:
            # Validar entrada
            is_valid, error_msg = self.validate_input(X)
            if not is_valid:
                self.error_count += 1
                return {'error': error_msg}
            
            # Asegurar formato correcto
            if X.ndim == 1:
                X = X.reshape(1, -1)
            
            # Realizar predicción según tipo de modelo
            if self.model_type == 'sklearn':
                prediction = self.model.predict(X)[0]
                probabilities = self.model.predict_proba(X)[0] if hasattr(self.model, 'predict_proba') else None
            elif self.model_type == 'onnx':
                input_name = self.model.get_inputs()[0].name
                result = self.model.run(None, {input_name: X.astype(np.float32)})
                prediction = result[0][0]
                probabilities = result[1][0] if len(result) > 1 else None
            else:
                self.error_count += 1
                return {'error': f'Tipo de modelo no soportado: {self.model_type}'}
            
            self.prediction_count += 1
            
            # Formatear resultado
            result = {
                'prediction': int(prediction),
                'prediction_label': 'Keylogger' if prediction == 1 else 'Benign',
                'confidence': float(np.max(probabilities)) if probabilities is not None else None,
                'probabilities': probabilities.tolist() if probabilities is not None else None,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error en predicción: {e}")
            return {'error': str(e)}
    
    def predict_batch(self, X: np.ndarray) -> List[Dict[str, Any]]:
        """Realiza predicciones para múltiples muestras."""
        try:
            # Validar entrada
            is_valid, error_msg = self.validate_input(X)
            if not is_valid:
                self.error_count += 1
                return [{'error': error_msg}] * len(X)
            
            # Realizar predicciones según tipo de modelo
            if self.model_type == 'sklearn':
                predictions = self.model.predict(X)
                probabilities = self.model.predict_proba(X) if hasattr(self.model, 'predict_proba') else None
            elif self.model_type == 'onnx':
                input_name = self.model.get_inputs()[0].name
                result = self.model.run(None, {input_name: X.astype(np.float32)})
                predictions = result[0]
                probabilities = result[1] if len(result) > 1 else None
            else:
                self.error_count += 1
                return [{'error': f'Tipo de modelo no soportado: {self.model_type}'}] * len(X)
            
            self.prediction_count += len(X)
            self.batch_count += 1
            
            # Formatear resultados
            results = []
            for i, prediction in enumerate(predictions):
                prob = probabilities[i] if probabilities is not None else None
                result = {
                    'prediction': int(prediction),
                    'prediction_label': 'Keylogger' if prediction == 1 else 'Benign',
                    'confidence': float(np.max(prob)) if prob is not None else None,
                    'probabilities': prob.tolist() if prob is not None else None,
                    'sample_index': i
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error en predicción batch: {e}")
            return [{'error': str(e)}] * len(X)
    
    def predict_from_dataframe(self, df: pd.DataFrame, target_column: Optional[str] = None) -> pd.DataFrame:
        """Realiza predicciones desde un DataFrame."""
        try:
            # Preparar datos
            if target_column and target_column in df.columns:
                X = df.drop(columns=[target_column]).values
            else:
                X = df.values
            
            # Realizar predicciones batch
            results = self.predict_batch(X)
            
            # Convertir a DataFrame
            predictions_df = pd.DataFrame(results)
            
            # Agregar al DataFrame original
            result_df = df.copy()
            result_df['predicted_class'] = predictions_df['prediction']
            result_df['predicted_label'] = predictions_df['prediction_label']
            result_df['prediction_confidence'] = predictions_df['confidence']
            
            return result_df
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error en predicción desde DataFrame: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de uso del predictor."""
        return {
            'model_info': {
                'model_path': str(self.model_path),
                'model_type': self.model_type,
                'num_features': len(self.feature_names)
            },
            'usage_stats': {
                'total_predictions': self.prediction_count,
                'batch_operations': self.batch_count,
                'error_count': self.error_count,
                'success_rate': (self.prediction_count / (self.prediction_count + self.error_count)) if (self.prediction_count + self.error_count) > 0 else 0
            },
            'timestamp': datetime.now().isoformat()
        }


class ModelAPI:
    """API REST para servir modelos de machine learning."""
    
    def __init__(self, predictor: ModelPredictor):
        if not HAS_FASTAPI:
            raise ImportError("FastAPI no está disponible. Instala con: pip install fastapi uvicorn")
        
        self.predictor = predictor
        self.app = FastAPI(title="Anti-Keylogger ML API", version="1.0.0")
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura las rutas de la API."""
        
        # Modelo para entrada de predicción
        class PredictionInput(BaseModel):
            features: List[float]
        
        class BatchPredictionInput(BaseModel):
            batch_features: List[List[float]]
        
        @self.app.get("/")
        async def root():
            return {"message": "Anti-Keylogger ML API", "status": "running"}
        
        @self.app.get("/health")
        async def health_check():
            stats = self.predictor.get_stats()
            return {"status": "healthy", "stats": stats}
        
        @self.app.post("/predict")
        async def predict(input_data: PredictionInput):
            try:
                X = np.array(input_data.features)
                result = self.predictor.predict_single(X)
                return result
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/predict/batch")
        async def predict_batch(input_data: BatchPredictionInput):
            try:
                X = np.array(input_data.batch_features)
                results = self.predictor.predict_batch(X)
                return {"predictions": results}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/model/info")
        async def model_info():
            return {
                "model_path": str(self.predictor.model_path),
                "model_type": self.predictor.model_type,
                "feature_names": self.predictor.feature_names,
                "metadata": self.predictor.metadata
            }
        
        @self.app.get("/stats")
        async def get_stats():
            return self.predictor.get_stats()
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
        """Ejecuta el servidor de la API."""
        uvicorn.run(self.app, host=host, port=port, reload=reload)


class BatchProcessor:
    """Procesador batch para grandes volúmenes de datos."""
    
    def __init__(self, predictor: ModelPredictor, output_dir: Path = Path("../models/predictions")):
        self.predictor = predictor
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def process_csv_file(self, 
                        input_path: Path, 
                        output_path: Optional[Path] = None,
                        target_column: Optional[str] = None,
                        chunk_size: int = 10000) -> Path:
        """Procesa un archivo CSV en chunks para manejar archivos grandes."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"predictions_{timestamp}.csv"
        
        logger.info(f"Procesando archivo: {input_path}")
        logger.info(f"Tamaño de chunk: {chunk_size:,} filas")
        
        # Procesar en chunks
        first_chunk = True
        total_processed = 0
        
        for chunk_df in pd.read_csv(input_path, chunksize=chunk_size):
            logger.info(f"Procesando chunk: {total_processed:,} - {total_processed + len(chunk_df):,}")
            
            # Realizar predicciones
            result_df = self.predictor.predict_from_dataframe(chunk_df, target_column)
            
            # Guardar resultados
            mode = 'w' if first_chunk else 'a'
            header = first_chunk
            result_df.to_csv(output_path, mode=mode, header=header, index=False)
            
            total_processed += len(chunk_df)
            first_chunk = False
        
        logger.info(f"[OK] Procesamiento completado. Total: {total_processed:,} filas")
        logger.info(f"Resultados guardados en: {output_path}")
        
        return output_path
    
    def process_parquet_file(self, 
                           input_path: Path, 
                           output_path: Optional[Path] = None,
                           target_column: Optional[str] = None) -> Path:
        """Procesa un archivo Parquet."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"predictions_{timestamp}.parquet"
        
        logger.info(f"Procesando archivo Parquet: {input_path}")
        
        # Cargar datos
        df = pd.read_parquet(input_path)
        logger.info(f"Datos cargados: {len(df):,} filas")
        
        # Realizar predicciones
        result_df = self.predictor.predict_from_dataframe(df, target_column)
        
        # Guardar resultados
        result_df.to_parquet(output_path, index=False)
        
        logger.info(f"[OK] Procesamiento completado")
        logger.info(f"Resultados guardados en: {output_path}")
        
        return output_path


def main():
    """Función principal para demostrar el uso del sistema de inferencia."""
    # Buscar modelo más reciente
    models_dir = Path("../models/development")
    model_files = list(models_dir.glob("*.pkl"))
    
    if not model_files:
        logger.error("No se encontraron modelos. Entrena un modelo primero.")
        return
    
    # Usar el modelo más reciente
    latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
    logger.info(f"Usando modelo: {latest_model.name}")
    
    # Buscar archivo de metadatos correspondiente
    metadata_files = list(models_dir.glob(f"{latest_model.stem}*metadata*.json"))
    metadata_path = metadata_files[0] if metadata_files else None
    
    # Crear predictor
    predictor = ModelPredictor(latest_model, metadata_path)
    
    # Mostrar estadísticas del modelo
    stats = predictor.get_stats()
    print("[DATA] Información del Modelo:")
    print(f"Tipo: {stats['model_info']['model_type']}")
    print(f"Features: {stats['model_info']['num_features']}")
    
    # Buscar datos para predicción
    test_data_dir = Path("../data/processed")
    test_files = list(test_data_dir.glob("*.parquet"))
    
    if test_files:
        test_file = test_files[0]
        print(f"\n[SEARCH] Realizando predicciones de prueba con: {test_file.name}")
        
        # Crear procesador batch
        batch_processor = BatchProcessor(predictor)
        
        # Procesar archivo
        result_path = batch_processor.process_parquet_file(
            test_file, 
            target_column="class"  # Ajustar según sea necesario
        )
        
        print(f"[OK] Predicciones guardadas en: {result_path}")
        
        # Mostrar estadísticas finales
        final_stats = predictor.get_stats()
        print(f"\n[STATS] Estadísticas de Uso:")
        print(f"Total predicciones: {final_stats['usage_stats']['total_predictions']:,}")
        print(f"Tasa de éxito: {final_stats['usage_stats']['success_rate']:.2%}")
    
    # Opción para ejecutar API
    print(f"\n[START] Para ejecutar la API REST:")
    print(f"   python -c \"from {__name__} import ModelPredictor, ModelAPI; api = ModelAPI(ModelPredictor(Path('{latest_model}'))); api.run()\"")


if __name__ == "__main__":
    main()