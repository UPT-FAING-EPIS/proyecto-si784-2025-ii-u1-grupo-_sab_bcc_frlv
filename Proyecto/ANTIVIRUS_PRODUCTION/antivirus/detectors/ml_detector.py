"""
Detector ML para Keyloggers
===========================

Utiliza los modelos entrenados para detectar keyloggers en tiempo real
mediante análisis de tráfico de red y características del sistema.
"""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import joblib
import json
import time

logger = logging.getLogger(__name__)


class MLKeyloggerDetector:
    """Detector de keyloggers usando Machine Learning"""
    
    def __init__(self, model_path: str = "models", 
                 use_onnx: bool = True, confidence_threshold: float = 0.8):
        self.model_path = Path(model_path)
        self.use_onnx = use_onnx
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.onnx_model = None
        self.feature_columns = None
        self.label_classes = None
        self.scaler = None
        
        # Estadísticas
        self.predictions_made = 0
        self.threats_detected = 0
        self.avg_prediction_time = 0.0
        
        # Cargar modelo
        self._load_model()
        self._load_feature_info()
        self._load_label_classes()
        
        logger.info(f"[ML] MLKeyloggerDetector inicializado (ONNX: {use_onnx})")
    
    def _load_model(self):
        """Carga el modelo de ML"""
        try:
            if self.use_onnx:
                self._load_onnx_model()
            else:
                self._load_sklearn_model()
                
        except Exception as e:
            logger.error(f"[ERROR] Error cargando modelo: {e}")
            # Fallback a sklearn si ONNX falla
            if self.use_onnx:
                logger.info("[SYNC] Fallback a modelo sklearn...")
                self._load_sklearn_model()
    
    def _load_onnx_model(self):
        """Carga el modelo ONNX optimizado"""
        try:
            import onnxruntime as ort
            
            onnx_path = self.model_path / "modelo_keylogger_from_datos.onnx"
            if not onnx_path.exists():
                raise FileNotFoundError(f"Modelo ONNX no encontrado: {onnx_path}")
            
            # Crear sesión ONNX
            self.onnx_model = ort.InferenceSession(str(onnx_path))
            
            # Obtener información del modelo
            input_details = self.onnx_model.get_inputs()[0]
            self.input_name = input_details.name
            self.input_shape = input_details.shape
            
            logger.info(f"[OK] Modelo ONNX cargado: {onnx_path}")
            logger.info(f"[DATA] Input shape: {self.input_shape}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error cargando ONNX: {e}")
            raise
    
    def _load_sklearn_model(self):
        """Carga el modelo sklearn"""
        try:
            # Buscar modelos disponibles en orden de preferencia
            model_candidates = [
                "rf_large_model_20250918_112442.pkl",
                "modelo_keylogger_from_datos.pkl",
            ]
            
            model_path = None
            for candidate in model_candidates:
                candidate_path = self.model_path / candidate
                if candidate_path.exists():
                    model_path = candidate_path
                    break
            
            if model_path is None:
                raise FileNotFoundError(f"Ningún modelo sklearn encontrado en {self.model_path}")
            
            self.model = joblib.load(model_path)
            logger.info(f"[OK] Modelo sklearn cargado: {model_path}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error cargando sklearn: {e}")
            raise
    
    def _load_feature_info(self):
        """Carga información sobre las características"""
        try:
            # Cargar desde metadata.json si existe
            metadata_path = self.model_path / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                self.feature_columns = metadata.get('feature_columns', [])
                logger.info(f"[INFO] Características cargadas: {len(self.feature_columns)} features")
            else:
                # Features por defecto basado en el dataset original
                self.feature_columns = [
                    'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
                    'Total Length of Fwd Packets', 'Total Length of Bwd Packets',
                    'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean',
                    'Fwd Packet Length Std', 'Bwd Packet Length Max', 'Bwd Packet Length Min',
                    'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s',
                    'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max',
                    'Flow IAT Min', 'Fwd IAT Total', 'Fwd IAT Mean', 'Fwd IAT Std',
                    'Fwd IAT Max', 'Fwd IAT Min', 'Bwd IAT Total', 'Bwd IAT Mean',
                    'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min', 'Fwd PSH Flags',
                    'Bwd PSH Flags', 'Fwd URG Flags', 'Bwd URG Flags', 'Fwd Header Length',
                    'Bwd Header Length', 'Fwd Packets/s', 'Bwd Packets/s', 'Min Packet Length',
                    'Max Packet Length', 'Packet Length Mean', 'Packet Length Std',
                    'Packet Length Variance', 'FIN Flag Count', 'SYN Flag Count',
                    'RST Flag Count', 'PSH Flag Count', 'ACK Flag Count', 'URG Flag Count',
                    'CWE Flag Count', 'ECE Flag Count', 'Down/Up Ratio', 'Average Packet Size',
                    'Avg Fwd Segment Size', 'Avg Bwd Segment Size', 'Fwd Header Length.1',
                    'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk', 'Fwd Avg Bulk Rate',
                    'Bwd Avg Bytes/Bulk', 'Bwd Avg Packets/Bulk', 'Bwd Avg Bulk Rate',
                    'Subflow Fwd Packets', 'Subflow Fwd Bytes', 'Subflow Bwd Packets',
                    'Subflow Bwd Bytes', 'Init_Win_bytes_forward', 'Init_Win_bytes_backward',
                    'act_data_pkt_fwd', 'min_seg_size_forward', 'Active Mean',
                    'Active Std', 'Active Max', 'Active Min', 'Idle Mean', 'Idle Std',
                    'Idle Max', 'Idle Min'
                ]
                logger.warning("[WARNING] Usando features por defecto (no se encontró metadata.json)")
                
        except Exception as e:
            logger.error(f"[ERROR] Error cargando feature info: {e}")
            self.feature_columns = []
    
    def _load_label_classes(self):
        """Carga las clases de etiquetas"""
        try:
            classes_path = self.model_path / "label_classes.json"
            if classes_path.exists():
                with open(classes_path, 'r') as f:
                    self.label_classes = json.load(f)
            else:
                self.label_classes = ["Benign", "Keylogger"]
            
            logger.info(f"[LABEL] Clases cargadas: {self.label_classes}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error cargando clases: {e}")
            self.label_classes = ["Benign", "Keylogger"]
    
    def extract_features_from_network_data(self, network_data: List[Dict]) -> np.ndarray:
        """Extrae características de datos de red para ML"""
        try:
            if not network_data:
                return np.array([]).reshape(0, len(self.feature_columns))
            
            # Convertir datos de red a formato numpy simple
            # Si network_data es una lista de diccionarios, convertir a formato numérico
            features_list = []
            
            # Para simplicidad sin pandas, crear características básicas
            if isinstance(network_data, list) and network_data:
                # Extraer características básicas sin pandas
                flow_features = self._extract_flow_features_simple(network_data)
                features_list.append(flow_features)
            else:
                # Datos agregados simples
                flow_features = self._create_default_features()
                features_list.append(flow_features)
            
            # Convertir a numpy array
            features_array = np.array(features_list)
            
            # Asegurar que tenemos el número correcto de características
            if features_array.shape[1] != len(self.feature_columns):
                # Ajustar dimensiones si es necesario
                features_array = self._adjust_feature_dimensions(features_array)
            
            return features_array
            
        except Exception as e:
            logger.error(f"[ERROR] Error extrayendo características: {e}")
            # Retornar array vacío en caso de error
            return np.array([]).reshape(0, len(self.feature_columns))
    
    def _extract_flow_features_simple(self, flow_data: List[Dict]) -> List[float]:
        """Extrae características de un flujo de red sin pandas"""
        try:
            if not flow_data:
                return self._create_default_features()
            
            # Características básicas del flujo
            total_packets = len(flow_data)
            
            # Extraer packet sizes si disponible
            packet_sizes = []
            for packet in flow_data:
                if 'packet_size' in packet:
                    packet_sizes.append(packet['packet_size'])
                elif 'size' in packet:
                    packet_sizes.append(packet['size'])
                else:
                    packet_sizes.append(64)  # tamaño promedio estimado
            
            if packet_sizes:
                total_bytes = sum(packet_sizes)
                avg_packet_size = total_bytes / len(packet_sizes)
                packet_size_std = np.std(packet_sizes) if len(packet_sizes) > 1 else 0
            else:
                total_bytes = avg_packet_size = packet_size_std = 0
            
            # Características direccionales estimadas
            fwd_packets = total_packets // 2
            bwd_packets = total_packets - fwd_packets
            
            # Crear vector de características básico (extendido para 81 features)
            features = [
                0.0,                          # Flow Duration
                float(fwd_packets),           # Total Fwd Packets
                float(bwd_packets),           # Total Backward Packets
                total_bytes * 0.6,           # Total Length of Fwd Packets
                total_bytes * 0.4,           # Total Length of Bwd Packets
                avg_packet_size * 1.2,       # Fwd Packet Length Max
                avg_packet_size * 0.8,       # Fwd Packet Length Min
                avg_packet_size,             # Fwd Packet Length Mean
                packet_size_std,             # Fwd Packet Length Std
                avg_packet_size * 1.1,       # Bwd Packet Length Max
                avg_packet_size * 0.9,       # Bwd Packet Length Min
                avg_packet_size,             # Bwd Packet Length Mean
                packet_size_std,             # Bwd Packet Length Std
                total_bytes / 60.0,          # Flow Bytes/s (estimado)
                float(total_packets) / 60.0, # Flow Packets/s (estimado)
            ]
            
            # Extender a 81 características con valores por defecto
            while len(features) < 81:
                features.append(0.0)
            
            # Truncar si hay demasiadas características
            if len(features) > 81:
                features = features[:81]
            
            return features
            
        except Exception as e:
            logger.error(f"[ERROR] Error extrayendo características simples: {e}")
            return self._create_default_features()
    
    def _create_default_features(self) -> List[float]:
        """Crea un vector de características por defecto"""
        # Crear 81 características con valores seguros por defecto
        return [0.0] * 81
    
    def _adjust_feature_dimensions(self, features_array: np.ndarray) -> np.ndarray:
        """Ajusta las dimensiones del array de características"""
        target_features = len(self.feature_columns)
        current_features = features_array.shape[1]
        
        if current_features < target_features:
            # Rellenar con ceros
            padding = np.zeros((features_array.shape[0], target_features - current_features))
            features_array = np.hstack([features_array, padding])
        elif current_features > target_features:
            # Truncar
            features_array = features_array[:, :target_features]
        
        return features_array
    
    def predict(self, features: np.ndarray) -> Tuple[List[str], List[float]]:
        """Realiza predicción usando el modelo cargado"""
        start_time = time.time()
        
        try:
            if features.shape[0] == 0:
                return [], []
            
            # Normalizar características si es necesario
            features_normalized = self._normalize_features(features)
            
            if self.onnx_model:
                # Predicción con ONNX
                predictions, probabilities = self._predict_onnx(features_normalized)
            elif self.model:
                # Predicción con sklearn
                predictions, probabilities = self._predict_sklearn(features_normalized)
            else:
                raise RuntimeError("No hay modelo cargado")
            
            # Actualizar estadísticas solo si hay predicciones exitosas
            if predictions:
                self.predictions_made += len(predictions)
                prediction_time = time.time() - start_time
                
                # Evitar división por cero
                if self.predictions_made > 0:
                    self.avg_prediction_time = (self.avg_prediction_time * (self.predictions_made - len(predictions)) + 
                                              prediction_time) / self.predictions_made
                else:
                    self.avg_prediction_time = prediction_time

            return predictions, probabilities
            
        except Exception as e:
            logger.error(f"[ERROR] Error en predicción: {e}")
            return [], []
    
    def _normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Normaliza las características (si es necesario)"""
        try:
            # Si tenemos un scaler guardado, usarlo
            if self.scaler:
                return self.scaler.transform(features)
            else:
                # Normalización simple (z-score)
                mean = np.mean(features, axis=0)
                std = np.std(features, axis=0)
                std[std == 0] = 1  # Evitar división por cero
                return (features - mean) / std
                
        except Exception as e:
            logger.warning(f"[WARNING] Error normalizando: {e}, usando features originales")
            return features
    
    def _predict_onnx(self, features: np.ndarray) -> Tuple[List[str], List[float]]:
        """Predicción usando modelo ONNX"""
        try:
            # Verificar dimensiones
            if features.shape[1] != 81:
                logger.error(f"[ERROR] Dimensiones incorrectas: esperadas 81, recibidas {features.shape[1]}")
                return [], []
            
            # Convertir a float32 (requerido por ONNX)
            features_float32 = features.astype(np.float32)
            
            # Realizar predicción
            outputs = self.onnx_model.run(None, {self.input_name: features_float32})
            
            # Extraer etiquetas y probabilidades
            # Output 0: etiquetas (tensor int64)
            # Output 1: probabilidades (seq de maps - formato complejo)
            labels_output = outputs[0]  # numpy array con índices de clases
            probabilities_output = outputs[1]  # lista de diccionarios con probabilidades
            
            predictions = []
            max_probs = []
            
            # Procesar cada predicción
            for i, label_idx in enumerate(labels_output):
                # Convertir índice a nombre de clase
                if 0 <= label_idx < len(self.label_classes):
                    predicted_class = self.label_classes[label_idx]
                else:
                    predicted_class = self.label_classes[0]  # Fallback
                
                predictions.append(predicted_class)
                
                # Extraer probabilidad máxima
                try:
                    if i < len(probabilities_output):
                        prob_dict = probabilities_output[i]
                        if isinstance(prob_dict, dict):
                            # Buscar la probabilidad más alta
                            max_prob = max(prob_dict.values()) if prob_dict else 0.5
                        else:
                            max_prob = 0.5  # Fallback
                    else:
                        max_prob = 0.5  # Fallback
                    
                    max_probs.append(float(max_prob))
                    
                except (IndexError, AttributeError, TypeError):
                    max_probs.append(0.5)  # Fallback
            
            return predictions, max_probs
            
        except Exception as e:
            logger.error(f"[ERROR] Error en predicción ONNX: {e}")
            return [], []
    
    def _predict_sklearn(self, features: np.ndarray) -> Tuple[List[str], List[float]]:
        """Predicción usando modelo sklearn"""
        try:
            # Predicciones
            predictions = self.model.predict(features)
            
            # Probabilidades
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(features)
                max_probs = [float(np.max(prob_row)) for prob_row in probabilities]
            else:
                # Si no hay predict_proba, usar confianza fija
                max_probs = [0.8] * len(predictions)
            
            # Convertir predicciones numéricas a nombres de clase
            if isinstance(predictions[0], (int, np.integer)):
                predictions = [self.label_classes[pred] for pred in predictions]
            
            return list(predictions), max_probs
            
        except Exception as e:
            logger.error(f"[ERROR] Error en predicción sklearn: {e}")
            return [], []
    
    def analyze_network_data(self, network_data: List[Dict]) -> List[Dict]:
        """Analiza datos de red y retorna amenazas detectadas"""
        threats = []
        
        try:
            # Extraer características
            features = self.extract_features_from_network_data(network_data)
            
            if features.shape[0] == 0:
                return threats
            
            # Realizar predicción
            predictions, probabilities = self.predict(features)
            
            # Procesar resultados
            for i, (prediction, probability) in enumerate(zip(predictions, probabilities)):
                if prediction == "Keylogger" and probability >= self.confidence_threshold:
                    threat = {
                        'type': 'keylogger',
                        'severity': 'high' if probability > 0.9 else 'medium',
                        'confidence': probability,
                        'source': 'ml_detector',
                        'details': {
                            'model_prediction': prediction,
                            'probability': probability,
                            'flow_index': i,
                            'feature_count': features.shape[1]
                        }
                    }
                    threats.append(threat)
                    self.threats_detected += 1
            
            logger.info(f"[SEARCH] Analizados {len(predictions)} flujos, {len(threats)} amenazas detectadas")
            
        except Exception as e:
            logger.error(f"[ERROR] Error analizando datos de red: {e}")
        
        return threats
    
    def quick_analyze(self, single_data_point: Dict) -> float:
        """Análisis rápido de un punto de datos individual"""
        try:
            # Convertir punto único a lista para procesamiento
            features = self.extract_features_from_network_data([single_data_point])
            
            if features.shape[0] == 0:
                return 0.0
            
            predictions, probabilities = self.predict(features)
            
            if predictions and predictions[0] == "Keylogger":
                return probabilities[0]
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"[ERROR] Error en análisis rápido: {e}")
            return 0.0
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del detector"""
        return {
            'predictions_made': self.predictions_made,
            'threats_detected': self.threats_detected,
            'avg_prediction_time': self.avg_prediction_time,
            'model_type': 'ONNX' if self.onnx_model else 'sklearn',
            'confidence_threshold': self.confidence_threshold,
            'feature_count': len(self.feature_columns),
            'label_classes': self.label_classes
        }
    
    def is_loaded(self) -> bool:
        """Verifica si el modelo está cargado correctamente"""
        return (self.onnx_model is not None) or (self.model is not None)