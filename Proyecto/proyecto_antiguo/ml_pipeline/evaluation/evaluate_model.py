"""
Sistema de Evaluación Avanzada de Modelos - Anti-Keylogger
==========================================================

Este módulo proporciona evaluación comprehensiva de modelos incluyendo:
- Métricas de rendimiento detalladas
- Análisis de robustez
- Comparación de modelos
- Reportes automáticos
- Validación de drift de datos
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

# Machine Learning libraries
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_curve, auc,
    precision_recall_curve, accuracy_score, f1_score, 
    precision_score, recall_score, matthews_corrcoef,
    balanced_accuracy_score, log_loss
)
from sklearn.model_selection import cross_val_score, StratifiedKFold

# ONNX runtime
try:
    import onnxruntime as ort
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False

# Data drift detection
try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluador avanzado de modelos para detección de keyloggers."""
    
    def __init__(self, output_dir: Path = Path("../models/evaluation")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.evaluation_results = {}
        self.model_comparison = {}
        
    def load_model(self, model_path: Path) -> Tuple[Any, str]:
        """Carga modelo desde archivo PKL o ONNX."""
        if model_path.suffix == '.pkl':
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            model_type = 'sklearn'
        elif model_path.suffix == '.onnx' and HAS_ONNX:
            model = ort.InferenceSession(str(model_path))
            model_type = 'onnx'
        else:
            raise ValueError(f"Formato de modelo no soportado: {model_path.suffix}")
        
        logger.info(f"Modelo cargado: {model_path.name} (tipo: {model_type})")
        return model, model_type
    
    def load_test_data(self, data_path: Path) -> pd.DataFrame:
        """Carga datos de test en múltiples formatos."""
        if data_path.suffix == '.parquet':
            df = pd.read_parquet(data_path)
        elif data_path.suffix == '.pkl':
            df = pd.read_pickle(data_path)
        elif data_path.suffix == '.csv':
            df = pd.read_csv(data_path)
        else:
            raise ValueError(f"Formato no soportado: {data_path.suffix}")
        
        logger.info(f"Datos de test cargados: {df.shape[0]:,} filas, {df.shape[1]} columnas")
        return df
    
    def predict_sklearn(self, model, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predicciones con modelo sklearn."""
        predictions = model.predict(X)
        probabilities = model.predict_proba(X) if hasattr(model, 'predict_proba') else None
        return predictions, probabilities
    
    def predict_onnx(self, model, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predicciones con modelo ONNX."""
        input_name = model.get_inputs()[0].name
        result = model.run(None, {input_name: X.astype(np.float32)})
        
        # El primer output suele ser las predicciones de clase
        predictions = result[0]
        
        # El segundo output (si existe) suelen ser las probabilidades
        probabilities = result[1] if len(result) > 1 else None
        
        return predictions, probabilities
    
    def calculate_comprehensive_metrics(self, 
                                       y_true: np.ndarray, 
                                       y_pred: np.ndarray, 
                                       y_proba: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Calcula métricas comprehensivas de evaluación."""
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted'),
            'recall': recall_score(y_true, y_pred, average='weighted'),
            'f1_score': f1_score(y_true, y_pred, average='weighted'),
            'f1_macro': f1_score(y_true, y_pred, average='macro'),
            'f1_micro': f1_score(y_true, y_pred, average='micro'),
            'balanced_accuracy': balanced_accuracy_score(y_true, y_pred),
            'matthews_corrcoef': matthews_corrcoef(y_true, y_pred)
        }
        
        # Métricas específicas para clasificación binaria
        if len(np.unique(y_true)) == 2:
            # Reorganizar para que la clase positiva sea 1
            pos_label = 1 if 1 in np.unique(y_true) else np.max(y_true)
            
            metrics.update({
                'precision_binary': precision_score(y_true, y_pred, pos_label=pos_label),
                'recall_binary': recall_score(y_true, y_pred, pos_label=pos_label),
                'f1_binary': f1_score(y_true, y_pred, pos_label=pos_label),
            })
            
            # Métricas de probabilidad si están disponibles
            if y_proba is not None:
                # Usar probabilidad de la clase positiva
                if y_proba.ndim > 1:
                    y_proba_pos = y_proba[:, 1] if y_proba.shape[1] > 1 else y_proba[:, 0]
                else:
                    y_proba_pos = y_proba
                
                try:
                    metrics['log_loss'] = log_loss(y_true, y_proba_pos)
                    
                    # ROC AUC
                    fpr, tpr, _ = roc_curve(y_true, y_proba_pos, pos_label=pos_label)
                    metrics['roc_auc'] = auc(fpr, tpr)
                    
                    # Precision-Recall AUC
                    precision_curve, recall_curve, _ = precision_recall_curve(
                        y_true, y_proba_pos, pos_label=pos_label
                    )
                    metrics['pr_auc'] = auc(recall_curve, precision_curve)
                    
                except Exception as e:
                    logger.warning(f"Error calculando métricas de probabilidad: {e}")
        
        return metrics
    
    def calculate_confusion_matrix_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """Calcula métricas derivadas de la matriz de confusión."""
        cm = confusion_matrix(y_true, y_pred)
        
        # Para clasificación binaria
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            npv = tn / (tn + fn) if (tn + fn) > 0 else 0  # Negative predictive value
            
            metrics = {
                'true_positives': int(tp),
                'true_negatives': int(tn),
                'false_positives': int(fp),
                'false_negatives': int(fn),
                'specificity': specificity,
                'negative_predictive_value': npv,
                'false_positive_rate': fp / (fp + tn) if (fp + tn) > 0 else 0,
                'false_negative_rate': fn / (fn + tp) if (fn + tp) > 0 else 0
            }
        else:
            # Para clasificación multiclase
            metrics = {
                'confusion_matrix': cm.tolist(),
                'per_class_accuracy': cm.diagonal() / cm.sum(axis=1)
            }
        
        return metrics
    
    def analyze_prediction_confidence(self, y_proba: np.ndarray) -> Dict[str, float]:
        """Analiza la confianza de las predicciones."""
        if y_proba is None:
            return {}
        
        # Máxima probabilidad por predicción
        if y_proba.ndim > 1:
            max_proba = np.max(y_proba, axis=1)
        else:
            max_proba = np.abs(y_proba - 0.5) + 0.5  # Para probabilidades binarias
        
        confidence_metrics = {
            'mean_confidence': float(np.mean(max_proba)),
            'std_confidence': float(np.std(max_proba)),
            'min_confidence': float(np.min(max_proba)),
            'max_confidence': float(np.max(max_proba)),
            'low_confidence_ratio': float(np.mean(max_proba < 0.7)),  # % predicciones con baja confianza
            'high_confidence_ratio': float(np.mean(max_proba > 0.9))  # % predicciones con alta confianza
        }
        
        return confidence_metrics
    
    def detect_data_drift(self, X_train: np.ndarray, X_test: np.ndarray, feature_names: List[str]) -> Dict[str, Any]:
        """Detecta drift en los datos usando tests estadísticos."""
        if not HAS_SCIPY:
            return {'error': 'SciPy no disponible para detección de drift'}
        
        drift_results = {}
        
        for i, feature_name in enumerate(feature_names):
            if i < X_train.shape[1] and i < X_test.shape[1]:
                train_values = X_train[:, i]
                test_values = X_test[:, i]
                
                # Test de Kolmogorov-Smirnov
                ks_stat, ks_p_value = stats.ks_2samp(train_values, test_values)
                
                # Diferencia en medias
                mean_diff = np.abs(np.mean(test_values) - np.mean(train_values))
                
                # Diferencia en desviaciones estándar
                std_diff = np.abs(np.std(test_values) - np.std(train_values))
                
                drift_results[feature_name] = {
                    'ks_statistic': float(ks_stat),
                    'ks_p_value': float(ks_p_value),
                    'has_significant_drift': ks_p_value < 0.05,
                    'mean_difference': float(mean_diff),
                    'std_difference': float(std_diff)
                }
        
        # Resumen de drift
        significant_drifts = sum(1 for result in drift_results.values() 
                               if result.get('has_significant_drift', False))
        
        drift_summary = {
            'total_features': len(drift_results),
            'features_with_drift': significant_drifts,
            'drift_ratio': significant_drifts / len(drift_results) if drift_results else 0,
            'feature_details': drift_results
        }
        
        return drift_summary
    
    def evaluate_model_comprehensive(self, 
                                   model_path: Path,
                                   test_data_path: Path,
                                   target_column: str,
                                   feature_columns: Optional[List[str]] = None,
                                   training_data_path: Optional[Path] = None) -> Dict[str, Any]:
        """Evaluación comprehensiva de un modelo."""
        logger.info(f"[SEARCH] Evaluando modelo: {model_path.name}")
        
        # 1. Cargar modelo
        model, model_type = self.load_model(model_path)
        
        # 2. Cargar datos de test
        test_df = self.load_test_data(test_data_path)
        
        # 3. Preparar datos
        if target_column not in test_df.columns:
            # Buscar columna target automáticamente
            possible_targets = [col for col in test_df.columns if any(term in col.lower() 
                               for term in ['class', 'label', 'target', 'malware', 'keylogger'])]
            if possible_targets:
                target_column = possible_targets[0]
                logger.info(f"Target column auto-detected: {target_column}")
            else:
                raise ValueError(f"No se encontró columna target. Columnas: {test_df.columns.tolist()}")
        
        y_true = test_df[target_column].values
        if feature_columns:
            X_test = test_df[feature_columns].values
        else:
            X_test = test_df.drop(columns=[target_column]).values
        
        # 4. Realizar predicciones
        if model_type == 'sklearn':
            y_pred, y_proba = self.predict_sklearn(model, X_test)
        elif model_type == 'onnx':
            y_pred, y_proba = self.predict_onnx(model, X_test)
        else:
            raise ValueError(f"Tipo de modelo no soportado: {model_type}")
        
        # 5. Calcular métricas
        comprehensive_metrics = self.calculate_comprehensive_metrics(y_true, y_pred, y_proba)
        confusion_metrics = self.calculate_confusion_matrix_metrics(y_true, y_pred)
        confidence_metrics = self.analyze_prediction_confidence(y_proba)
        
        # 6. Detección de drift (si hay datos de entrenamiento)
        drift_analysis = {}
        if training_data_path:
            try:
                train_df = self.load_test_data(training_data_path)
                X_train = train_df.drop(columns=[target_column]).values
                feature_names = train_df.drop(columns=[target_column]).columns.tolist()
                drift_analysis = self.detect_data_drift(X_train, X_test, feature_names)
            except Exception as e:
                logger.warning(f"Error en análisis de drift: {e}")
        
        # 7. Compilar resultados
        evaluation_result = {
            'model_info': {
                'model_path': str(model_path),
                'model_type': model_type,
                'test_data_path': str(test_data_path),
                'evaluation_timestamp': datetime.now().isoformat()
            },
            'data_info': {
                'test_samples': len(X_test),
                'num_features': X_test.shape[1],
                'class_distribution': dict(zip(*np.unique(y_true, return_counts=True)))
            },
            'performance_metrics': comprehensive_metrics,
            'confusion_matrix_analysis': confusion_metrics,
            'prediction_confidence': confidence_metrics,
            'data_drift_analysis': drift_analysis
        }
        
        # 8. Guardar resultados
        model_name = model_path.stem
        self.evaluation_results[model_name] = evaluation_result
        
        # Guardar reporte individual
        report_path = self.output_dir / f"{model_name}_evaluation_report.json"
        with open(report_path, 'w') as f:
            json.dump(evaluation_result, f, indent=2, default=str)
        
        logger.info(f"[OK] Evaluación completada - F1: {comprehensive_metrics['f1_score']:.4f}")
        return evaluation_result
    
    def compare_models(self, evaluation_results: Dict[str, Dict]) -> Dict[str, Any]:
        """Compara múltiples modelos evaluados."""
        if len(evaluation_results) < 2:
            logger.warning("Se necesitan al menos 2 modelos para comparar")
            return {}
        
        # Métricas a comparar
        comparison_metrics = [
            'accuracy', 'precision', 'recall', 'f1_score', 
            'balanced_accuracy', 'matthews_corrcoef'
        ]
        
        comparison_table = {}
        for metric in comparison_metrics:
            comparison_table[metric] = {}
            for model_name, results in evaluation_results.items():
                if 'performance_metrics' in results:
                    comparison_table[metric][model_name] = results['performance_metrics'].get(metric, 0)
        
        # Ranking de modelos por F1 score
        f1_scores = comparison_table.get('f1_score', {})
        model_ranking = sorted(f1_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Análisis de robustez (basado en confianza de predicciones)
        robustness_analysis = {}
        for model_name, results in evaluation_results.items():
            confidence_metrics = results.get('prediction_confidence', {})
            if confidence_metrics:
                robustness_score = (
                    confidence_metrics.get('mean_confidence', 0) * 0.4 +
                    confidence_metrics.get('high_confidence_ratio', 0) * 0.4 +
                    (1 - confidence_metrics.get('low_confidence_ratio', 1)) * 0.2
                )
                robustness_analysis[model_name] = {
                    'robustness_score': robustness_score,
                    **confidence_metrics
                }
        
        comparison_summary = {
            'comparison_table': comparison_table,
            'model_ranking': model_ranking,
            'best_model': model_ranking[0][0] if model_ranking else None,
            'robustness_analysis': robustness_analysis,
            'comparison_timestamp': datetime.now().isoformat()
        }
        
        # Guardar comparación
        comparison_path = self.output_dir / "model_comparison_report.json"
        with open(comparison_path, 'w') as f:
            json.dump(comparison_summary, f, indent=2, default=str)
        
        logger.info(f"[DATA] Comparación de modelos completada. Mejor modelo: {comparison_summary.get('best_model', 'N/A')}")
        return comparison_summary
    
    def generate_evaluation_summary(self) -> Dict[str, Any]:
        """Genera resumen completo de todas las evaluaciones."""
        if not self.evaluation_results:
            logger.warning("No hay resultados de evaluación para resumir")
            return {}
        
        # Resumen general
        summary = {
            'evaluation_overview': {
                'total_models_evaluated': len(self.evaluation_results),
                'evaluation_date': datetime.now().isoformat()
            },
            'individual_results': self.evaluation_results
        }
        
        # Comparación si hay múltiples modelos
        if len(self.evaluation_results) > 1:
            comparison = self.compare_models(self.evaluation_results)
            summary['model_comparison'] = comparison
        
        # Guardar resumen
        summary_path = self.output_dir / "complete_evaluation_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"[INFO] Resumen de evaluación guardado: {summary_path}")
        return summary


def main():
    """Función principal para evaluar modelos."""
    evaluator = ModelEvaluator()
    
    # Buscar modelos en directorio de desarrollo
    models_dir = Path("../models/development")
    test_data_dir = Path("../data/processed")
    
    # Buscar modelos PKL
    model_files = list(models_dir.glob("*.pkl"))
    
    if not model_files:
        logger.error("No se encontraron modelos para evaluar")
        return
    
    # Buscar datos de test
    test_files = list(test_data_dir.glob("*test*.parquet"))
    if not test_files:
        test_files = list(test_data_dir.glob("*.parquet"))
    
    if not test_files:
        logger.error("No se encontraron datos de test")
        return
    
    test_data_path = test_files[0]
    logger.info(f"Usando datos de test: {test_data_path}")
    
    # Evaluar todos los modelos
    for model_path in model_files:
        try:
            evaluator.evaluate_model_comprehensive(
                model_path=model_path,
                test_data_path=test_data_path,
                target_column="class"  # Ajustar según sea necesario
            )
        except Exception as e:
            logger.error(f"Error evaluando {model_path.name}: {e}")
    
    # Generar resumen final
    summary = evaluator.generate_evaluation_summary()
    
    # Mostrar resultados
    if 'model_comparison' in summary:
        print("[DATA] Resultados de la Comparación de Modelos:")
        best_model = summary['model_comparison'].get('best_model')
        if best_model:
            print(f"🏆 Mejor modelo: {best_model}")
            
            f1_scores = summary['model_comparison']['comparison_table'].get('f1_score', {})
            for model, score in f1_scores.items():
                print(f"[STATS] {model}: F1 = {score:.4f}")


if __name__ == "__main__":
    main()