"""
Pipeline Avanzado de Entrenamiento de Modelos - Anti-Keylogger
==============================================================

Este módulo implementa un pipeline completo de machine learning con:
- Multiple algoritmos (RandomForest, XGBoost, LightGBM)
- Hyperparameter tuning
- Cross-validation
- Métricas avanzadas
- Exportación a múltiples formatos (PKL, ONNX)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import logging
import json
import pickle
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Machine Learning libraries
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_curve, auc,
    precision_recall_curve, f1_score, accuracy_score, precision_score, recall_score
)

# Advanced ML algorithms
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

# ONNX conversion
try:
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
    import onnxruntime as ort
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedModelTrainer:
    """Entrenador avanzado de modelos para detección de keyloggers."""
    
    def __init__(self, output_dir: Path = Path("../models")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "development").mkdir(exist_ok=True)
        (self.output_dir / "production").mkdir(exist_ok=True)
        (self.output_dir / "experiments").mkdir(exist_ok=True)
        
        self.models = {}
        self.results = {}
        self.feature_names = []
        
    def load_processed_data(self, data_path: Path) -> Tuple[pd.DataFrame, str]:
        """Carga datos procesados en múltiples formatos."""
        if data_path.suffix == '.parquet':
            df = pd.read_parquet(data_path)
        elif data_path.suffix == '.pkl':
            df = pd.read_pickle(data_path)
        elif data_path.suffix == '.csv':
            df = pd.read_csv(data_path)
        else:
            raise ValueError(f"Formato no soportado: {data_path.suffix}")
        
        logger.info(f"Datos cargados: {df.shape[0]:,} filas, {df.shape[1]} columnas")
        return df, data_path.stem
    
    def prepare_features_and_target(self, 
                                   df: pd.DataFrame, 
                                   target_column: str,
                                   feature_columns: Optional[List[str]] = None) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepara features y target para entrenamiento."""
        
        # Identificar columna target
        if target_column not in df.columns:
            # Buscar columnas que podrían ser target
            possible_targets = [col for col in df.columns if any(term in col.lower() 
                               for term in ['class', 'label', 'target', 'malware', 'keylogger'])]
            if possible_targets:
                target_column = possible_targets[0]
                logger.info(f"Target column auto-detected: {target_column}")
            else:
                raise ValueError(f"No se encontró columna target. Columnas disponibles: {df.columns.tolist()}")
        
        # Separar features y target
        y = df[target_column]
        
        if feature_columns:
            X = df[feature_columns]
        else:
            X = df.drop(columns=[target_column])
        
        # Codificar target si es categórico
        if y.dtype == 'object':
            le = LabelEncoder()
            y = le.fit_transform(y)
            logger.info(f"Target codificado: {le.classes_}")
        
        # Guardar nombres de features
        self.feature_names = X.columns.tolist()
        
        logger.info(f"Features preparadas: {X.shape[1]} columnas")
        logger.info(f"Distribución de clases: {np.bincount(y)}")
        
        return X.values, y, self.feature_names
    
    def create_model_configurations(self) -> Dict[str, Dict]:
        """Define configuraciones de modelos a entrenar."""
        configs = {
            'random_forest': {
                'model': RandomForestClassifier,
                'params': {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'random_state': [42]
                },
                'available': True
            }
        }
        
        if HAS_XGBOOST:
            configs['xgboost'] = {
                'model': xgb.XGBClassifier,
                'params': {
                    'n_estimators': [100, 200],
                    'max_depth': [6, 10],
                    'learning_rate': [0.1, 0.01],
                    'subsample': [0.8, 1.0],
                    'random_state': [42]
                },
                'available': True
            }
        
        if HAS_LIGHTGBM:
            configs['lightgbm'] = {
                'model': lgb.LGBMClassifier,
                'params': {
                    'n_estimators': [100, 200],
                    'max_depth': [10, 20],
                    'learning_rate': [0.1, 0.01],
                    'num_leaves': [31, 62],
                    'random_state': [42]
                },
                'available': True
            }
        
        return configs
    
    def train_model_with_cv(self, 
                           X: np.ndarray, 
                           y: np.ndarray, 
                           model_name: str, 
                           config: Dict) -> Dict[str, Any]:
        """Entrena modelo con cross-validation y hyperparameter tuning."""
        logger.info(f"[START] Entrenando modelo: {model_name}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Grid search with cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        grid_search = GridSearchCV(
            config['model'](),
            config['params'],
            cv=cv,
            scoring='f1_weighted',
            n_jobs=-1,
            verbose=1
        )
        
        # Fit model
        grid_search.fit(X_train, y_train)
        best_model = grid_search.best_estimator_
        
        # Predictions
        y_train_pred = best_model.predict(X_train)
        y_test_pred = best_model.predict(X_test)
        y_test_proba = best_model.predict_proba(X_test)
        
        # Calculate metrics
        metrics = {
            'train_accuracy': accuracy_score(y_train, y_train_pred),
            'test_accuracy': accuracy_score(y_test, y_test_pred),
            'train_f1': f1_score(y_train, y_train_pred, average='weighted'),
            'test_f1': f1_score(y_test, y_test_pred, average='weighted'),
            'precision': precision_score(y_test, y_test_pred, average='weighted'),
            'recall': recall_score(y_test, y_test_pred, average='weighted'),
        }
        
        # Cross-validation scores
        cv_scores = cross_val_score(best_model, X_train, y_train, cv=cv, scoring='f1_weighted')
        metrics['cv_mean'] = cv_scores.mean()
        metrics['cv_std'] = cv_scores.std()
        
        # Feature importance
        if hasattr(best_model, 'feature_importances_'):
            feature_importance = dict(zip(self.feature_names, best_model.feature_importances_))
            # Sort by importance
            feature_importance = dict(sorted(feature_importance.items(), 
                                           key=lambda x: x[1], reverse=True))
        else:
            feature_importance = {}
        
        # Store results
        result = {
            'model_name': model_name,
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'metrics': metrics,
            'feature_importance': feature_importance,
            'classification_report': classification_report(y_test, y_test_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_test_pred).tolist(),
            'train_size': len(X_train),
            'test_size': len(X_test),
            'training_timestamp': datetime.now().isoformat()
        }
        
        # Store model
        self.models[model_name] = best_model
        self.results[model_name] = result
        
        logger.info(f"[OK] {model_name} entrenado - F1: {metrics['test_f1']:.4f}")
        
        return result
    
    def train_all_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Entrena todos los modelos configurados."""
        configs = self.create_model_configurations()
        all_results = {}
        
        for model_name, config in configs.items():
            if config['available']:
                try:
                    result = self.train_model_with_cv(X, y, model_name, config)
                    all_results[model_name] = result
                except Exception as e:
                    logger.error(f"Error entrenando {model_name}: {e}")
                    all_results[model_name] = {'error': str(e)}
        
        return all_results
    
    def select_best_model(self, results: Dict[str, Any], metric: str = 'test_f1') -> Tuple[str, Any]:
        """Selecciona el mejor modelo basado en una métrica."""
        best_score = -1
        best_model_name = None
        
        for model_name, result in results.items():
            if 'error' not in result and result['metrics'][metric] > best_score:
                best_score = result['metrics'][metric]
                best_model_name = model_name
        
        best_model = self.models[best_model_name] if best_model_name else None
        logger.info(f"🏆 Mejor modelo: {best_model_name} ({metric}: {best_score:.4f})")
        
        return best_model_name, best_model
    
    def save_model_pickle(self, model, model_name: str, dataset_name: str) -> Path:
        """Guarda modelo en formato Pickle."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{dataset_name}_{model_name}_{timestamp}.pkl"
        filepath = self.output_dir / "development" / filename
        
        with open(filepath, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(f"Modelo guardado (PKL): {filepath}")
        return filepath
    
    def convert_to_onnx(self, model, model_name: str, dataset_name: str, X_sample: np.ndarray) -> Optional[Path]:
        """Convierte modelo a formato ONNX."""
        if not HAS_ONNX:
            logger.warning("ONNX no disponible, saltando conversión")
            return None
        
        try:
            # Define input type
            initial_type = [('float_input', FloatTensorType([None, X_sample.shape[1]]))]
            
            # Convert to ONNX
            onx = convert_sklearn(model, initial_types=initial_type)
            
            # Save ONNX model
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{dataset_name}_{model_name}_{timestamp}.onnx"
            filepath = self.output_dir / "development" / filename
            
            with open(filepath, "wb") as f:
                f.write(onx.SerializeToString())
            
            logger.info(f"Modelo convertido a ONNX: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error convirtiendo a ONNX: {e}")
            return None
    
    def save_metadata(self, model_name: str, dataset_name: str, result: Dict[str, Any]) -> Path:
        """Guarda metadatos del modelo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{dataset_name}_{model_name}_metadata_{timestamp}.json"
        filepath = self.output_dir / "development" / filename
        
        metadata = {
            'model_name': model_name,
            'dataset_name': dataset_name,
            'feature_names': self.feature_names,
            'training_results': result,
            'model_info': {
                'algorithm': model_name,
                'num_features': len(self.feature_names),
                'training_timestamp': timestamp
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"Metadatos guardados: {filepath}")
        return filepath
    
    def create_visualizations(self, results: Dict[str, Any], output_dir: Path):
        """Crea visualizaciones de los resultados."""
        viz_dir = output_dir / "visualizations"
        viz_dir.mkdir(exist_ok=True)
        
        # Comparación de modelos
        models = []
        f1_scores = []
        accuracies = []
        
        for model_name, result in results.items():
            if 'error' not in result:
                models.append(model_name)
                f1_scores.append(result['metrics']['test_f1'])
                accuracies.append(result['metrics']['test_accuracy'])
        
        # Plot model comparison
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        ax1.bar(models, f1_scores)
        ax1.set_title('F1 Score Comparison')
        ax1.set_ylabel('F1 Score')
        ax1.tick_params(axis='x', rotation=45)
        
        ax2.bar(models, accuracies)
        ax2.set_title('Accuracy Comparison')
        ax2.set_ylabel('Accuracy')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(viz_dir / "model_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Visualizaciones guardadas en: {viz_dir}")
    
    def full_training_pipeline(self, 
                              data_path: Path, 
                              target_column: str,
                              feature_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Pipeline completo de entrenamiento."""
        logger.info("[START] Iniciando pipeline completo de entrenamiento")
        
        # 1. Cargar datos
        df, dataset_name = self.load_processed_data(data_path)
        
        # 2. Preparar features y target
        X, y, feature_names = self.prepare_features_and_target(df, target_column, feature_columns)
        
        # 3. Entrenar todos los modelos
        all_results = self.train_all_models(X, y)
        
        # 4. Seleccionar mejor modelo
        best_model_name, best_model = self.select_best_model(all_results)
        
        if best_model:
            # 5. Guardar mejor modelo
            pkl_path = self.save_model_pickle(best_model, best_model_name, dataset_name)
            onnx_path = self.convert_to_onnx(best_model, best_model_name, dataset_name, X)
            metadata_path = self.save_metadata(best_model_name, dataset_name, all_results[best_model_name])
            
            # 6. Crear visualizaciones
            self.create_visualizations(all_results, self.output_dir)
            
            # 7. Resumen final
            training_summary = {
                'dataset_name': dataset_name,
                'best_model': best_model_name,
                'all_results': all_results,
                'model_paths': {
                    'pickle': str(pkl_path),
                    'onnx': str(onnx_path) if onnx_path else None,
                    'metadata': str(metadata_path)
                },
                'feature_names': feature_names,
                'training_completed': datetime.now().isoformat()
            }
            
            # Guardar resumen
            summary_path = self.output_dir / f"{dataset_name}_training_summary.json"
            with open(summary_path, 'w') as f:
                json.dump(training_summary, f, indent=2, default=str)
            
            logger.info("[OK] Pipeline de entrenamiento completado")
            return training_summary
        
        else:
            logger.error("[ERROR] No se pudo entrenar ningún modelo exitosamente")
            return {'error': 'No successful models'}


def main():
    """Función principal para entrenar modelos."""
    trainer = AdvancedModelTrainer()
    
    # Buscar datos procesados
    processed_dir = Path("../data/processed")
    
    # Buscar archivos Parquet (más eficientes)
    parquet_files = list(processed_dir.glob("*.parquet"))
    
    if parquet_files:
        # Entrenar con el primer archivo encontrado
        data_path = parquet_files[0]
        logger.info(f"Entrenando con: {data_path}")
        
        summary = trainer.full_training_pipeline(
            data_path=data_path,
            target_column="class"  # Ajustar según el nombre real
        )
        
        print("[DATA] Resumen del entrenamiento:")
        if 'error' not in summary:
            print(f"[OK] Mejor modelo: {summary['best_model']}")
            best_result = summary['all_results'][summary['best_model']]
            print(f"[STATS] F1 Score: {best_result['metrics']['test_f1']:.4f}")
            print(f"[STATS] Accuracy: {best_result['metrics']['test_accuracy']:.4f}")
        else:
            print("[ERROR] Error en el entrenamiento")
    
    else:
        logger.error("No se encontraron datos procesados. Ejecuta primero data_preprocessing.py")


if __name__ == "__main__":
    main()