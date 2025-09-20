"""
Evaluación Avanzada del Modelo Anti-Keylogger
==============================================

Análisis detallado de rendimiento, métricas y visualizaciones.
"""

import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
import logging
from datetime import datetime

from sklearn.metrics import (
    classification_report, confusion_matrix, 
    roc_curve, auc, precision_recall_curve,
    matthews_corrcoef
)

# Para visualizaciones (si matplotlib está disponible)
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("[WARNING]  Matplotlib no disponible, saltando visualizaciones")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelEvaluator:
    """Evaluador avanzado para modelos de detección de keyloggers"""
    
    def __init__(self):
        self.results = {}
        
    def load_latest_model(self):
        """Carga el modelo más reciente"""
        # Obtener el directorio base del proyecto (dos niveles arriba)
        base_dir = Path(__file__).parent.parent.parent
        models_dir = base_dir / "models" / "development"
        
        # Buscar modelos (priorizar el grande)
        large_models = list(models_dir.glob("rf_large_model_*.pkl"))
        regular_models = list(models_dir.glob("rf_model_*.pkl"))
        
        if large_models:
            model_files = large_models
            logger.info("[DATA] Usando modelo GRANDE")
        elif regular_models:
            model_files = regular_models
            logger.info("[DATA] Usando modelo regular")
        else:
            logger.error("[ERROR] No se encontraron modelos")
            return None, None, None
        
        latest_model_file = max(model_files, key=lambda x: x.stat().st_mtime)
        
        # Cargar modelo
        with open(latest_model_file, 'rb') as f:
            model = pickle.load(f)
        
        # Cargar metadatos
        if 'large' in latest_model_file.name:
            metadata_file = models_dir / latest_model_file.name.replace('rf_large_model_', 'rf_large_metadata_').replace('.pkl', '.json')
        else:
            metadata_file = models_dir / latest_model_file.name.replace('rf_model_', 'rf_metadata_').replace('.pkl', '.json')
        
        metadata = {}
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        
        logger.info(f"[OK] Modelo cargado: {latest_model_file.name}")
        return model, metadata, str(latest_model_file)
    
    def load_test_data(self):
        """Carga datos de test"""
        processed_dir = Path("data/processed")
        
        # Priorizar dataset grande
        large_file = processed_dir / "dataset_large_sample.parquet"
        small_file = processed_dir / "dataset_small_clean.parquet"
        
        if large_file.exists():
            df = pd.read_parquet(large_file)
            dataset_name = "large"
        elif small_file.exists():
            df = pd.read_parquet(small_file)
            dataset_name = "small"
        else:
            logger.error("[ERROR] No se encontraron datos de test")
            return None, None
        
        logger.info(f"[DATA] Datos de test cargados: {len(df):,} filas ({dataset_name})")
        return df, dataset_name
    
    def comprehensive_evaluation(self, model, df, metadata):
        """Evaluación comprehensiva del modelo"""
        logger.info("[SEARCH] Iniciando evaluación comprehensiva...")
        
        # Preparar datos
        X = df.drop(columns=['Class'])
        y = df['Class']
        
        # Codificar si es necesario
        if y.dtype == 'object':
            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            y_encoded = le.fit_transform(y)
            class_names = le.classes_
        else:
            y_encoded = y
            class_names = ['Benign', 'Keylogger']
        
        # Solo columnas numéricas
        X_numeric = X.select_dtypes(include=[np.number])
        
        # Predicciones
        y_pred = model.predict(X_numeric)
        y_proba = model.predict_proba(X_numeric)
        
        # === MÉTRICAS BÁSICAS ===
        accuracy = model.score(X_numeric, y_encoded)
        report = classification_report(y_encoded, y_pred, target_names=class_names, output_dict=True)
        cm = confusion_matrix(y_encoded, y_pred)
        
        logger.info(f"[STATS] Accuracy: {accuracy:.4f}")
        logger.info(f"[STATS] F1-Score: {report['weighted avg']['f1-score']:.4f}")
        logger.info(f"[STATS] Precision: {report['weighted avg']['precision']:.4f}")
        logger.info(f"[STATS] Recall: {report['weighted avg']['recall']:.4f}")
        
        # === MÉTRICAS AVANZADAS ===
        mcc = matthews_corrcoef(y_encoded, y_pred)
        logger.info(f"[STATS] Matthews Correlation: {mcc:.4f}")
        
        # === ANÁLISIS DE MATRIZ DE CONFUSIÓN ===
        tn, fp, fn, tp = cm.ravel()
        
        specificity = tn / (tn + fp)
        sensitivity = tp / (tp + fn)  # = recall
        precision = tp / (tp + fp)
        npv = tn / (tn + fn)  # Negative predictive value
        
        logger.info("[DATA] Análisis detallado de matriz de confusión:")
        logger.info(f"   True Positives (Keyloggers detectados): {tp:,}")
        logger.info(f"   True Negatives (Benign correctos): {tn:,}")
        logger.info(f"   False Positives (Falsos keyloggers): {fp:,}")
        logger.info(f"   False Negatives (Keyloggers perdidos): {fn:,}")
        logger.info(f"   Specificity (TNR): {specificity:.4f}")
        logger.info(f"   Sensitivity (TPR): {sensitivity:.4f}")
        logger.info(f"   Negative Predictive Value: {npv:.4f}")
        
        # === ANÁLISIS ROC ===
        if y_proba.shape[1] == 2:
            fpr, tpr, _ = roc_curve(y_encoded, y_proba[:, 1])
            roc_auc = auc(fpr, tpr)
            logger.info(f"[STATS] ROC AUC: {roc_auc:.4f}")
            
            # Precision-Recall curve
            precision_curve, recall_curve, _ = precision_recall_curve(y_encoded, y_proba[:, 1])
            pr_auc = auc(recall_curve, precision_curve)
            logger.info(f"[STATS] PR AUC: {pr_auc:.4f}")
        
        # === ANÁLISIS DE CONFIANZA ===
        confidences = np.max(y_proba, axis=1)
        logger.info("[DATA] Análisis de confianza de predicciones:")
        logger.info(f"   Confianza promedio: {np.mean(confidences):.4f}")
        logger.info(f"   Confianza mínima: {np.min(confidences):.4f}")
        logger.info(f"   Confianza máxima: {np.max(confidences):.4f}")
        logger.info(f"   Predicciones con baja confianza (<70%): {np.sum(confidences < 0.7):,} ({np.mean(confidences < 0.7):.2%})")
        logger.info(f"   Predicciones con alta confianza (>90%): {np.sum(confidences > 0.9):,} ({np.mean(confidences > 0.9):.2%})")
        
        # === FEATURE IMPORTANCE ===
        if hasattr(model, 'feature_importances_'):
            feature_names = X_numeric.columns
            importances = model.feature_importances_
            
            # Top 15 features
            top_indices = np.argsort(importances)[-15:][::-1]
            
            logger.info("🔝 Top 15 Features más importantes:")
            for i, idx in enumerate(top_indices):
                logger.info(f"   {i+1:2d}. {feature_names[idx]:<25s}: {importances[idx]:.4f}")
        
        # === COMPILAR RESULTADOS ===
        evaluation_results = {
            'basic_metrics': {
                'accuracy': accuracy,
                'f1_score': report['weighted avg']['f1-score'],
                'precision': report['weighted avg']['precision'],
                'recall': report['weighted avg']['recall'],
                'matthews_correlation': mcc
            },
            'confusion_matrix': {
                'matrix': cm.tolist(),
                'true_positives': int(tp),
                'true_negatives': int(tn),
                'false_positives': int(fp),
                'false_negatives': int(fn),
                'specificity': specificity,
                'sensitivity': sensitivity,
                'npv': npv
            },
            'confidence_analysis': {
                'mean_confidence': float(np.mean(confidences)),
                'min_confidence': float(np.min(confidences)),
                'max_confidence': float(np.max(confidences)),
                'low_confidence_count': int(np.sum(confidences < 0.7)),
                'high_confidence_count': int(np.sum(confidences > 0.9)),
                'low_confidence_ratio': float(np.mean(confidences < 0.7)),
                'high_confidence_ratio': float(np.mean(confidences > 0.9))
            },
            'detailed_report': report,
            'timestamp': datetime.now().isoformat()
        }
        
        # Agregar ROC si está disponible
        if y_proba.shape[1] == 2:
            evaluation_results['roc_analysis'] = {
                'roc_auc': roc_auc,
                'pr_auc': pr_auc
            }
        
        # Agregar feature importance si está disponible
        if hasattr(model, 'feature_importances_'):
            feature_importance_dict = dict(zip(feature_names, importances))
            top_features = [(feature_names[idx], float(importances[idx])) for idx in top_indices]
            
            evaluation_results['feature_analysis'] = {
                'all_features': feature_importance_dict,
                'top_15_features': top_features
            }
        
        return evaluation_results
    
    def save_evaluation_report(self, results, model_path, dataset_name):
        """Guarda reporte de evaluación"""
        # Obtener el directorio base del proyecto (dos niveles arriba)
        base_dir = Path(__file__).parent.parent.parent
        reports_dir = base_dir / "models" / "evaluation"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = Path(model_path).stem
        
        report_file = reports_dir / f"evaluation_report_{model_name}_{dataset_name}_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"[INFO] Reporte guardado: {report_file}")
        return report_file
    
    def print_summary(self, results):
        """Imprime resumen ejecutivo"""
        print("\n" + "="*70)
        print("[DATA] RESUMEN EJECUTIVO - EVALUACIÓN DEL MODELO")
        print("="*70)
        
        basic = results['basic_metrics']
        conf_matrix = results['confusion_matrix']
        confidence = results['confidence_analysis']
        
        print(f"[TARGET] RENDIMIENTO GENERAL:")
        print(f"   Accuracy:     {basic['accuracy']:.2%}")
        print(f"   F1-Score:     {basic['f1_score']:.2%}")
        print(f"   Precision:    {basic['precision']:.2%}")
        print(f"   Recall:       {basic['recall']:.2%}")
        print(f"   Matthews Corr: {basic['matthews_correlation']:.4f}")
        
        print(f"\n[SEARCH] DETECCIÓN DE KEYLOGGERS:")
        print(f"   Keyloggers detectados:    {conf_matrix['true_positives']:,}")
        print(f"   Keyloggers perdidos:      {conf_matrix['false_negatives']:,}")
        print(f"   Falsos positivos:         {conf_matrix['false_positives']:,}")
        print(f"   Tasa de detección:        {conf_matrix['sensitivity']:.2%}")
        print(f"   Tasa de falsos positivos: {conf_matrix['false_positives']/(conf_matrix['false_positives']+conf_matrix['true_negatives']):.2%}")
        
        print(f"\n[STATS] CONFIANZA DE PREDICCIONES:")
        print(f"   Confianza promedio:       {confidence['mean_confidence']:.2%}")
        print(f"   Predicciones confiables:  {confidence['high_confidence_ratio']:.2%} (>90%)")
        print(f"   Predicciones dudosas:     {confidence['low_confidence_ratio']:.2%} (<70%)")
        
        if 'roc_analysis' in results:
            roc = results['roc_analysis']
            print(f"\n[DATA] MÉTRICAS AVANZADAS:")
            print(f"   ROC AUC:      {roc['roc_auc']:.4f}")
            print(f"   PR AUC:       {roc['pr_auc']:.4f}")
        
        if 'feature_analysis' in results:
            top_feature = results['feature_analysis']['top_15_features'][0]
            print(f"\n🔝 FEATURE MÁS IMPORTANTE:")
            print(f"   {top_feature[0]}: {top_feature[1]:.4f}")
        
        print("="*70)

def main():
    """Función principal"""
    evaluator = ModelEvaluator()
    
    # Cargar modelo
    model, metadata, model_path = evaluator.load_latest_model()
    if model is None:
        return
    
    # Cargar datos de test
    df, dataset_name = evaluator.load_test_data()
    if df is None:
        return
    
    # Evaluación comprehensiva
    results = evaluator.comprehensive_evaluation(model, df, metadata)
    
    # Guardar reporte
    report_path = evaluator.save_evaluation_report(results, model_path, dataset_name)
    
    # Mostrar resumen
    evaluator.print_summary(results)
    
    print(f"\n[INFO] Reporte completo guardado en: {report_path}")

if __name__ == "__main__":
    main()