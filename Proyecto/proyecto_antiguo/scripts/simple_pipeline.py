"""
Pipeline Simple de ML - Anti-Keylogger
======================================

Versión simplificada para ejecutar el pipeline paso a paso.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
from datetime import datetime
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def step1_load_and_preview_data():
    """Paso 1: Cargar y preview de datos"""
    logger.info("[SEARCH] PASO 1: Cargando y analizando datos...")
    
    # Obtener el directorio base del proyecto (un nivel arriba)
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data" / "raw"
    
    for csv_file in data_dir.glob("*.csv"):
        logger.info(f"[FILE] Analizando: {csv_file.name}")
        
        # Obtener info básica del archivo
        file_size_mb = csv_file.stat().st_size / (1024 * 1024)
        logger.info(f"   Tamaño: {file_size_mb:.1f} MB")
        
        # Leer primeras filas para análisis
        try:
            df_sample = pd.read_csv(csv_file, nrows=1000)
            logger.info(f"   Columnas: {len(df_sample.columns)}")
            logger.info(f"   Muestra de columnas: {list(df_sample.columns[:5])}")
            
            # Buscar columna target
            target_candidates = [col for col in df_sample.columns 
                               if any(term in col.lower() for term in ['class', 'label', 'target', 'malware'])]
            if target_candidates:
                logger.info(f"   Posible target: {target_candidates[0]}")
                
                # Distribución de clases
                if target_candidates[0] in df_sample.columns:
                    class_dist = df_sample[target_candidates[0]].value_counts()
                    logger.info(f"   Distribución de clases: {dict(class_dist)}")
            
        except Exception as e:
            logger.error(f"   Error leyendo {csv_file.name}: {e}")
    
    return True

def step2_basic_preprocessing():
    """Paso 2: Preprocesamiento básico"""
    logger.info("[CLEAN] PASO 2: Preprocesamiento básico...")
    
    # Obtener el directorio base del proyecto (un nivel arriba)
    base_dir = Path(__file__).parent.parent
    raw_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"
    processed_dir.mkdir(exist_ok=True)
    
    # Procesar archivo pequeño primero
    small_file = raw_dir / "keylogger_dataset_small.csv"
    
    if small_file.exists():
        logger.info(f"[DATA] Procesando {small_file.name}...")
        
        try:
            # Cargar datos
            df = pd.read_csv(small_file)
            logger.info(f"   Datos cargados: {len(df):,} filas, {df.shape[1]} columnas")
            
            # Identificar columna target
            target_column = None
            for col in df.columns:
                if any(term in col.lower() for term in ['class', 'label', 'target', 'malware']):
                    target_column = col
                    break
            
            if target_column:
                logger.info(f"   Target identificado: {target_column}")
                
                # Análisis básico
                missing_count = df.isnull().sum().sum()
                logger.info(f"   Valores faltantes: {missing_count:,}")
                
                duplicates = df.duplicated().sum()
                logger.info(f"   Duplicados: {duplicates:,}")
                
                # Distribución de clases
                class_dist = df[target_column].value_counts()
                logger.info(f"   Distribución: {dict(class_dist)}")
                
                # Limpiar datos básico
                if missing_count > 0:
                    df_clean = df.dropna()
                    logger.info(f"   Después de limpiar NaN: {len(df_clean):,} filas")
                else:
                    df_clean = df.copy()
                
                if duplicates > 0:
                    df_clean = df_clean.drop_duplicates()
                    logger.info(f"   Después de eliminar duplicados: {len(df_clean):,} filas")
                
                # Guardar datos procesados
                try:
                    output_file = processed_dir / "dataset_small_clean.parquet"
                    df_clean.to_parquet(output_file, index=False)
                    logger.info(f"   [OK] Guardado en Parquet: {output_file}")
                except Exception as parquet_error:
                    logger.warning(f"   [WARNING] Error con Parquet: {parquet_error}")
                    output_file = processed_dir / "dataset_small_clean.csv"
                    df_clean.to_csv(output_file, index=False)
                    logger.info(f"   [OK] Guardado en CSV: {output_file}")
                
                return True, target_column, output_file
                
            else:
                logger.error("   [ERROR] No se encontró columna target")
                return False, None, None
                
        except Exception as e:
            logger.error(f"   [ERROR] Error procesando datos: {e}")
            return False, None, None
    
    else:
        logger.error(f"[ERROR] No se encontró {small_file}")
        return False, None, None

def step3_simple_training():
    """Paso 3: Entrenamiento simple"""
    logger.info("[START] PASO 3: Entrenamiento de modelo...")
    
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report, accuracy_score
    from sklearn.preprocessing import LabelEncoder
    import pickle
    
    # Obtener el directorio base del proyecto (un nivel arriba)
    base_dir = Path(__file__).parent.parent
    processed_dir = base_dir / "data" / "processed"
    models_dir = base_dir / "models" / "development"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Buscar datos procesados
    parquet_file = processed_dir / "dataset_small_clean.parquet"
    csv_file = processed_dir / "dataset_small_clean.csv"
    
    data_file = None
    if parquet_file.exists():
        data_file = parquet_file
    elif csv_file.exists():
        data_file = csv_file
    
    if data_file is None:
        logger.error("[ERROR] No se encontraron datos procesados. Ejecuta paso 2 primero.")
        return False
    
    try:
        # Cargar datos
        if data_file.suffix == '.parquet':
            df = pd.read_parquet(data_file)
        else:
            df = pd.read_csv(data_file)
        logger.info(f"   Datos cargados: {len(df):,} filas")
        
        # Identificar target
        target_column = None
        for col in df.columns:
            if any(term in col.lower() for term in ['class', 'label', 'target', 'malware']):
                target_column = col
                break
        
        if not target_column:
            logger.error("[ERROR] No se encontró columna target")
            return False
        
        # Separar features y target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Codificar target si es necesario
        if y.dtype == 'object':
            le = LabelEncoder()
            y = le.fit_transform(y)
            logger.info(f"   Target codificado: {list(le.classes_)}")
        
        # Verificar que X sean numéricas
        non_numeric = X.select_dtypes(exclude=[np.number]).columns
        if len(non_numeric) > 0:
            logger.info(f"   Eliminando columnas no numéricas: {list(non_numeric)}")
            X = X.select_dtypes(include=[np.number])
        
        logger.info(f"   Features finales: {X.shape[1]} columnas")
        
        # Split datos
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"   Train: {len(X_train):,}, Test: {len(X_test):,}")
        
        # Entrenar modelo
        logger.info("   [SYNC] Entrenando Random Forest...")
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        
        # Evaluar
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        y_pred = model.predict(X_test)
        
        logger.info(f"   [STATS] Accuracy Train: {train_score:.4f}")
        logger.info(f"   [STATS] Accuracy Test: {test_score:.4f}")
        
        # Reporte detallado
        report = classification_report(y_test, y_pred, output_dict=True)
        f1_score = report['weighted avg']['f1-score']
        logger.info(f"   [STATS] F1-Score: {f1_score:.4f}")
        
        # Guardar modelo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_file = models_dir / f"rf_model_{timestamp}.pkl"
        
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
        
        # Guardar metadatos
        metadata = {
            'model_type': 'RandomForestClassifier',
            'features': list(X.columns),
            'target_column': target_column,
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'f1_score': f1_score,
            'timestamp': timestamp,
            'data_shape': df.shape
        }
        
        metadata_file = models_dir / f"rf_metadata_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"   [OK] Modelo guardado: {model_file}")
        logger.info(f"   [OK] Metadatos guardados: {metadata_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Error en entrenamiento: {e}")
        return False

def step4_simple_prediction():
    """Paso 4: Predicciones simples"""
    logger.info("[TARGET] PASO 4: Realizando predicciones...")
    
    import pickle
    
    # Obtener el directorio base del proyecto (un nivel arriba)
    base_dir = Path(__file__).parent.parent
    models_dir = base_dir / "models" / "development"
    processed_dir = base_dir / "data" / "processed"
    predictions_dir = base_dir / "models" / "predictions"
    predictions_dir.mkdir(parents=True, exist_ok=True)
    
    # Buscar el modelo más reciente
    model_files = list(models_dir.glob("rf_model_*.pkl"))
    
    if not model_files:
        logger.error("[ERROR] No se encontraron modelos. Ejecuta paso 3 primero.")
        return False
    
    latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
    logger.info(f"   [PACKAGE] Usando modelo: {latest_model.name}")
    
    try:
        # Cargar modelo
        with open(latest_model, 'rb') as f:
            model = pickle.load(f)
        
        # Cargar datos de test
        parquet_file = processed_dir / "dataset_small_clean.parquet"
        csv_file = processed_dir / "dataset_small_clean.csv"
        
        if parquet_file.exists():
            df = pd.read_parquet(parquet_file)
        elif csv_file.exists():
            df = pd.read_csv(csv_file)
        else:
            logger.error("[ERROR] No se encontraron datos procesados")
            return False
        
        # Identificar target
        target_column = None
        for col in df.columns:
            if any(term in col.lower() for term in ['class', 'label', 'target', 'malware']):
                target_column = col
                break
        
        # Preparar datos
        X = df.drop(columns=[target_column])
        X = X.select_dtypes(include=[np.number])  # Solo numéricas
        
        # Hacer predicciones
        logger.info(f"   [SYNC] Prediciendo {len(X):,} muestras...")
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)
        
        # Crear DataFrame con resultados
        results_df = df.copy()
        results_df['predicted_class'] = predictions
        results_df['prediction_confidence'] = np.max(probabilities, axis=1)
        
        # Análisis de resultados
        unique_preds, counts = np.unique(predictions, return_counts=True)
        pred_dist = dict(zip(unique_preds, counts))
        logger.info(f"   [DATA] Distribución predicciones: {pred_dist}")
        
        avg_confidence = np.mean(results_df['prediction_confidence'])
        logger.info(f"   [DATA] Confianza promedio: {avg_confidence:.4f}")
        
        # Guardar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            output_file = predictions_dir / f"predictions_{timestamp}.parquet"
            results_df.to_parquet(output_file, index=False)
            logger.info(f"   [OK] Predicciones guardadas: {output_file}")
        except Exception:
            output_file = predictions_dir / f"predictions_{timestamp}.csv"
            results_df.to_csv(output_file, index=False)
            logger.info(f"   [OK] Predicciones guardadas: {output_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Error en predicciones: {e}")
        return False

def run_simple_pipeline():
    """Ejecuta el pipeline completo simplificado"""
    logger.info("[START] INICIANDO PIPELINE SIMPLE DE ML")
    logger.info("=" * 50)
    
    start_time = datetime.now()
    
    # Paso 1: Análisis de datos
    if not step1_load_and_preview_data():
        logger.error("[ERROR] Falló paso 1")
        return False
    
    # Paso 2: Preprocesamiento
    success, target_col, processed_file = step2_basic_preprocessing()
    if not success:
        logger.error("[ERROR] Falló paso 2")
        return False
    
    # Paso 3: Entrenamiento
    if not step3_simple_training():
        logger.error("[ERROR] Falló paso 3")
        return False
    
    # Paso 4: Predicciones
    if not step4_simple_prediction():
        logger.error("[ERROR] Falló paso 4")
        return False
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("=" * 50)
    logger.info(f"[OK] PIPELINE COMPLETADO EXITOSAMENTE")
    logger.info(f"[TIME]  Duración total: {duration}")
    logger.info("=" * 50)
    
    # Resumen final
    logger.info("[INFO] RESUMEN:")
    logger.info(f"   [OK] Datos procesados: data/processed/")
    logger.info(f"   [OK] Modelo entrenado: models/development/")
    logger.info(f"   [OK] Predicciones: models/predictions/")
    
    return True

if __name__ == "__main__":
    try:
        success = run_simple_pipeline()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("[ERROR] Pipeline interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[ERROR] Error inesperado: {e}")
        sys.exit(1)