"""
Adaptador para modelos de Machine Learning.
Implementa la interfaz IMLModelAdapter para ONNX y Pickle.
"""

import json
import pickle
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import time

from ..core.use_cases import IMLModelAdapter
from ..core.domain import FileFeatures, DetectionResult, ThreatLevel

try:
    import onnxruntime as ort
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False
    ort = None


class MLModelAdapter(IMLModelAdapter):
    """Adaptador principal para modelos de ML."""
    
    def __init__(self, model_path: Path, features_path: Path, labels_path: Optional[Path] = None):
        self.model_path = model_path
        self.features_path = features_path
        self.labels_path = labels_path
        self.model = None
        self.feature_names: List[str] = []
        self.label_classes: Dict[int, str] = {}
        self.model_type = self._detect_model_type()
        self.model_version = "1.0.0"
        
    def _detect_model_type(self) -> str:
        """Detecta el tipo de modelo basado en la extensión."""
        ext = self.model_path.suffix.lower()
        if ext == '.onnx':
            return 'onnx'
        elif ext == '.pkl':
            return 'pickle'
        else:
            raise ValueError(f"Tipo de modelo no soportado: {ext}")
    
    def load_model(self, model_path: Path) -> bool:
        """Carga el modelo ML."""
        try:
            self.model_path = model_path
            
            # Cargar features esperadas
            if self.features_path.exists():
                with open(self.features_path, 'r', encoding='utf-8') as f:
                    features_data = json.load(f)
                    if isinstance(features_data, list):
                        self.feature_names = features_data
                    else:
                        self.feature_names = list(features_data.keys())
            
            # Cargar clases/labels
            if self.labels_path and self.labels_path.exists():
                with open(self.labels_path, 'r', encoding='utf-8') as f:
                    labels_data = json.load(f)
                    if isinstance(labels_data, list):
                        self.label_classes = {i: label for i, label in enumerate(labels_data)}
                    elif isinstance(labels_data, dict):
                        self.label_classes = {int(k): v for k, v in labels_data.items()}
            
            # Cargar modelo específico
            if self.model_type == 'onnx':
                return self._load_onnx_model()
            elif self.model_type == 'pickle':
                return self._load_pickle_model()
            
            return False
            
        except Exception as e:
            print(f"Error cargando modelo: {e}")
            return False
    
    def _load_onnx_model(self) -> bool:
        """Carga modelo ONNX."""
        if not HAS_ONNX:
            raise ImportError("onnxruntime no está disponible")
        
        try:
            self.model = ort.InferenceSession(
                str(self.model_path), 
                providers=['CPUExecutionProvider']
            )
            return True
        except Exception as e:
            print(f"Error cargando modelo ONNX: {e}")
            return False
    
    def _load_pickle_model(self) -> bool:
        """Carga modelo Pickle."""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            return True
        except Exception as e:
            print(f"Error cargando modelo Pickle: {e}")
            return False
    
    def predict(self, features: FileFeatures) -> DetectionResult:
        """Realiza predicción sobre las características."""
        if not self.model:
            raise RuntimeError("Modelo no cargado")
        
        try:
            # Preparar datos para el modelo
            feature_dict = self._prepare_features(features)
            
            # Realizar predicción
            if self.model_type == 'onnx':
                probabilities = self._predict_onnx(feature_dict)
            elif self.model_type == 'pickle':
                probabilities = self._predict_pickle(feature_dict)
            else:
                raise ValueError(f"Tipo de modelo no soportado: {self.model_type}")
            
            # Interpretar resultados
            return self._interpret_results(features, probabilities)
            
        except Exception as e:
            # En caso de error, retornar resultado neutro
            return DetectionResult(
                file_path=Path("unknown"),
                threat_level=ThreatLevel.BENIGN,
                confidence=0.0,
                features=features,
                timestamp=time.time(),
                model_version=self.model_version,
                details={"error": str(e)}
            )
    
    def _prepare_features(self, features: FileFeatures) -> Dict[str, float]:
        """Prepara las características para el modelo."""
        feature_dict = features.to_dict()
        
        # Asegurar que todas las features esperadas estén presentes
        prepared = {}
        for feature_name in self.feature_names:
            value = feature_dict.get(feature_name, 0)
            
            # Convertir a float si es posible
            try:
                prepared[feature_name] = float(value)
            except (ValueError, TypeError):
                prepared[feature_name] = 0.0
        
        return prepared
    
    def _predict_onnx(self, feature_dict: Dict[str, float]) -> List[float]:
        """Predicción usando modelo ONNX."""
        # Crear DataFrame para mantener orden de columnas
        df = pd.DataFrame([feature_dict])
        df = df.reindex(columns=self.feature_names, fill_value=0.0)
        
        # Preparar input para ONNX
        input_name = self.model.get_inputs()[0].name
        X = df.values.astype('float32')
        
        # Ejecutar predicción
        outputs = self.model.run(None, {input_name: X})
        
        # Extraer probabilidades
        probabilities = self._extract_probabilities_from_onnx(outputs)
        return probabilities
    
    def _predict_pickle(self, feature_dict: Dict[str, float]) -> List[float]:
        """Predicción usando modelo Pickle."""
        # Crear DataFrame
        df = pd.DataFrame([feature_dict])
        df = df.reindex(columns=self.feature_names, fill_value=0.0)
        
        # Realizar predicción
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(df.values)[0]
        else:
            # Si no tiene predict_proba, usar predict y simular probabilidades
            prediction = self.model.predict(df.values)[0]
            if prediction == 1:
                probabilities = [0.2, 0.8]  # Simulado: benign, malicious
            else:
                probabilities = [0.8, 0.2]
        
        return list(probabilities)
    
    def _extract_probabilities_from_onnx(self, outputs) -> List[float]:
        """Extrae probabilidades de la salida de ONNX."""
        # Buscar tensor de probabilidades
        prob_tensor = None
        
        for output in outputs:
            if hasattr(output, 'dtype') and 'float' in str(output.dtype):
                prob_tensor = output
                break
        
        if prob_tensor is not None:
            if len(prob_tensor.shape) > 1:
                return list(prob_tensor[0])  # Primera fila
            else:
                return list(prob_tensor)
        
        # Si no se encuentra, retornar neutro
        return [0.5, 0.5]
    
    def _interpret_results(self, features: FileFeatures, probabilities: List[float]) -> DetectionResult:
        """Interpreta los resultados de la predicción."""
        # Asumiendo formato [benign_prob, malicious_prob]
        if len(probabilities) >= 2:
            benign_prob = probabilities[0]
            malicious_prob = probabilities[1]
        else:
            # Formato no estándar
            benign_prob = 0.5
            malicious_prob = 0.5
        
        # Determinar nivel de amenaza y confianza
        if malicious_prob > 0.8:
            threat_level = ThreatLevel.MALICIOUS
            confidence = malicious_prob
        elif malicious_prob > 0.6:
            threat_level = ThreatLevel.SUSPICIOUS
            confidence = malicious_prob
        else:
            threat_level = ThreatLevel.BENIGN
            confidence = benign_prob
        
        return DetectionResult(
            file_path=Path("analyzed_file"),  # Se actualizará desde el use case
            threat_level=threat_level,
            confidence=confidence,
            features=features,
            timestamp=time.time(),
            model_version=self.model_version,
            details={
                "probabilities": {
                    "benign": benign_prob,
                    "malicious": malicious_prob
                },
                "model_type": self.model_type
            }
        )


class ONNXModelAdapter(MLModelAdapter):
    """Adaptador específico para modelos ONNX."""
    
    def __init__(self, model_path: Path, features_path: Path, labels_path: Optional[Path] = None):
        if not HAS_ONNX:
            raise ImportError("onnxruntime no está disponible para ONNXModelAdapter")
        super().__init__(model_path, features_path, labels_path)
        if not self.model_path.suffix.lower() == '.onnx':
            raise ValueError("ONNXModelAdapter requiere archivo .onnx")


class PickleModelAdapter(MLModelAdapter):
    """Adaptador específico para modelos Pickle."""
    
    def __init__(self, model_path: Path, features_path: Path, labels_path: Optional[Path] = None):
        super().__init__(model_path, features_path, labels_path)
        if not self.model_path.suffix.lower() == '.pkl':
            raise ValueError("PickleModelAdapter requiere archivo .pkl")


def create_model_adapter(
    model_path: Path, 
    features_path: Path, 
    labels_path: Optional[Path] = None
) -> MLModelAdapter:
    """Factory function para crear el adaptador apropiado."""
    ext = model_path.suffix.lower()
    
    if ext == '.onnx':
        return ONNXModelAdapter(model_path, features_path, labels_path)
    elif ext == '.pkl':
        return PickleModelAdapter(model_path, features_path, labels_path)
    else:
        raise ValueError(f"Formato de modelo no soportado: {ext}")