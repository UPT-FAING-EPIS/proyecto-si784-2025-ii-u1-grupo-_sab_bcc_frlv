"""
Pipeline de Preprocesamiento de Datos para Anti-Keylogger
=========================================================

Este módulo contiene las funciones para limpiar y preparar los datasets
de detección de keyloggers para machine learning.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Dict, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Clase principal para preprocesamiento de datos de keylogger."""
    
    def __init__(self, output_dir: Path = Path("../data/processed")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cleaning_stats = {}
    
    def load_raw_data(self, file_path: Path, sample_size: int = None) -> pd.DataFrame:
        """Carga datos raw con manejo de errores."""
        try:
            if sample_size:
                df = pd.read_csv(file_path, nrows=sample_size, low_memory=False)
                logger.info(f"Muestra de {sample_size:,} filas cargada de {file_path.name}")
            else:
                df = pd.read_csv(file_path, low_memory=False)
                logger.info(f"Dataset completo cargado: {df.shape[0]:,} filas de {file_path.name}")
            
            return df
        except Exception as e:
            logger.error(f"Error cargando {file_path}: {e}")
            raise
    
    def explore_data_quality(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        """Analiza la calidad de los datos."""
        logger.info(f"Analizando calidad de datos para: {dataset_name}")
        
        quality_report = {
            'dataset_name': dataset_name,
            'shape': df.shape,
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'duplicates': df.duplicated().sum(),
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.to_dict(),
            'unique_values_per_column': df.nunique().to_dict(),
        }
        
        # Detectar columnas con posibles problemas
        problematic_columns = []
        for col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 50:
                problematic_columns.append(f"{col}: {missing_pct:.1f}% missing")
        
        quality_report['problematic_columns'] = problematic_columns
        
        # Estadísticas básicas para columnas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            quality_report['numeric_stats'] = df[numeric_cols].describe().to_dict()
        
        return quality_report
    
    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y estandariza nombres de columnas."""
        original_cols = df.columns.tolist()
        
        # Convertir a lowercase y reemplazar espacios/caracteres especiales
        df.columns = (df.columns
                      .str.lower()
                      .str.replace(' ', '_')
                      .str.replace('[^a-zA-Z0-9_]', '', regex=True)
                      .str.replace('__+', '_', regex=True)
                      .str.strip('_'))
        
        cleaned_cols = df.columns.tolist()
        
        # Log cambios
        changed_cols = [(orig, new) for orig, new in zip(original_cols, cleaned_cols) if orig != new]
        if changed_cols:
            logger.info(f"Columnas renombradas: {len(changed_cols)} cambios")
            for orig, new in changed_cols[:5]:  # Show first 5
                logger.info(f"  {orig} → {new}")
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'smart') -> pd.DataFrame:
        """Maneja valores faltantes con diferentes estrategias."""
        missing_before = df.isnull().sum().sum()
        
        if strategy == 'smart':
            # Estrategia inteligente basada en el tipo de columna y porcentaje de missing
            for col in df.columns:
                missing_pct = (df[col].isnull().sum() / len(df)) * 100
                
                if missing_pct > 80:
                    # Eliminar columnas con >80% missing
                    df = df.drop(columns=[col])
                    logger.info(f"Columna eliminada (>{missing_pct:.1f}% missing): {col}")
                
                elif missing_pct > 0:
                    if df[col].dtype in ['int64', 'float64']:
                        # Para numéricas: llenar con mediana
                        df[col].fillna(df[col].median(), inplace=True)
                    elif df[col].dtype == 'object':
                        # Para categóricas: llenar con moda o 'unknown'
                        mode_val = df[col].mode()
                        fill_val = mode_val[0] if len(mode_val) > 0 else 'unknown'
                        df[col].fillna(fill_val, inplace=True)
                    else:
                        # Para otros tipos: llenar con 0
                        df[col].fillna(0, inplace=True)
        
        elif strategy == 'drop_rows':
            df = df.dropna()
        
        elif strategy == 'drop_columns':
            df = df.dropna(axis=1)
        
        missing_after = df.isnull().sum().sum()
        logger.info(f"Valores faltantes: {missing_before:,} → {missing_after:,}")
        
        return df
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Elimina filas duplicadas."""
        duplicates_before = df.duplicated().sum()
        df = df.drop_duplicates()
        duplicates_removed = duplicates_before - df.duplicated().sum()
        
        if duplicates_removed > 0:
            logger.info(f"Duplicados eliminados: {duplicates_removed:,}")
        
        return df
    
    def detect_outliers(self, df: pd.DataFrame, method: str = 'iqr') -> Dict[str, List]:
        """Detecta outliers en columnas numéricas."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outliers_info = {}
        
        for col in numeric_cols:
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index.tolist()
                outliers_info[col] = {
                    'count': len(outliers),
                    'percentage': (len(outliers) / len(df)) * 100,
                    'bounds': (lower_bound, upper_bound)
                }
        
        return outliers_info
    
    def encode_categorical_variables(self, df: pd.DataFrame, target_col: str = None) -> Tuple[pd.DataFrame, Dict]:
        """Codifica variables categóricas."""
        categorical_cols = df.select_dtypes(include=['object']).columns
        if target_col and target_col in categorical_cols:
            categorical_cols = categorical_cols.drop(target_col)
        
        encoding_info = {}
        
        for col in categorical_cols:
            unique_values = df[col].nunique()
            
            if unique_values <= 10:  # One-hot encoding para pocas categorías
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
                df = pd.concat([df, dummies], axis=1)
                df = df.drop(columns=[col])
                encoding_info[col] = {
                    'method': 'one_hot',
                    'new_columns': dummies.columns.tolist()
                }
            else:  # Label encoding para muchas categorías
                from sklearn.preprocessing import LabelEncoder
                le = LabelEncoder()
                df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
                df = df.drop(columns=[col])
                encoding_info[col] = {
                    'method': 'label_encoding',
                    'encoder': le,
                    'new_column': f"{col}_encoded"
                }
        
        return df, encoding_info
    
    def export_to_efficient_formats(self, df: pd.DataFrame, base_name: str):
        """Exporta datos a formatos eficientes."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Parquet (más eficiente que CSV)
        parquet_path = self.output_dir / f"{base_name}_clean_{timestamp}.parquet"
        df.to_parquet(parquet_path, index=False, compression='snappy')
        logger.info(f"Exportado a Parquet: {parquet_path}")
        
        # Pickle (preserva tipos de datos exactos)
        pickle_path = self.output_dir / f"{base_name}_clean_{timestamp}.pkl"
        df.to_pickle(pickle_path)
        logger.info(f"Exportado a Pickle: {pickle_path}")
        
        # CSV comprimido (para compatibilidad)
        csv_path = self.output_dir / f"{base_name}_clean_{timestamp}.csv.gz"
        df.to_csv(csv_path, index=False, compression='gzip')
        logger.info(f"Exportado a CSV comprimido: {csv_path}")
        
        return {
            'parquet': parquet_path,
            'pickle': pickle_path,
            'csv_gz': csv_path,
            'rows': len(df),
            'columns': len(df.columns)
        }
    
    def full_preprocessing_pipeline(self, 
                                   input_path: Path, 
                                   dataset_name: str,
                                   sample_size: int = None,
                                   target_column: str = None) -> Dict[str, Any]:
        """Pipeline completo de preprocesamiento."""
        logger.info(f"[START] Iniciando pipeline de preprocesamiento para: {dataset_name}")
        
        # 1. Cargar datos
        df = self.load_raw_data(input_path, sample_size)
        
        # 2. Análisis de calidad inicial
        quality_before = self.explore_data_quality(df, f"{dataset_name}_raw")
        
        # 3. Limpieza de nombres de columnas
        df = self.clean_column_names(df)
        
        # 4. Manejo de valores faltantes
        df = self.handle_missing_values(df, strategy='smart')
        
        # 5. Eliminación de duplicados
        df = self.remove_duplicates(df)
        
        # 6. Detección de outliers
        outliers_info = self.detect_outliers(df)
        
        # 7. Codificación de variables categóricas
        df, encoding_info = self.encode_categorical_variables(df, target_column)
        
        # 8. Análisis de calidad final
        quality_after = self.explore_data_quality(df, f"{dataset_name}_clean")
        
        # 9. Exportar a formatos eficientes
        export_info = self.export_to_efficient_formats(df, dataset_name)
        
        # Resumen del procesamiento
        processing_summary = {
            'dataset_name': dataset_name,
            'quality_before': quality_before,
            'quality_after': quality_after,
            'outliers_info': outliers_info,
            'encoding_info': encoding_info,
            'export_info': export_info,
            'processing_timestamp': datetime.now().isoformat()
        }
        
        # Guardar resumen
        summary_path = self.output_dir / f"{dataset_name}_processing_summary.json"
        with open(summary_path, 'w') as f:
            # Convert numpy types to native Python types for JSON serialization
            def convert_numpy(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return obj
            
            import json
            json.dump(processing_summary, f, indent=2, default=convert_numpy)
        
        logger.info(f"[OK] Pipeline completado para {dataset_name}")
        logger.info(f"[DATA] Filas: {quality_before['shape'][0]:,} → {quality_after['shape'][0]:,}")
        logger.info(f"[DATA] Columnas: {quality_before['shape'][1]} → {quality_after['shape'][1]}")
        
        return processing_summary


def main():
    """Función principal para ejecutar el pipeline de preprocesamiento."""
    preprocessor = DataPreprocessor()
    
    # Definir rutas de datos
    data_dir = Path("../data/raw")
    
    # Procesar dataset pequeño
    small_dataset_path = data_dir / "keylogger_dataset_small.csv"
    if small_dataset_path.exists():
        summary_small = preprocessor.full_preprocessing_pipeline(
            small_dataset_path, 
            "keylogger_small",
            target_column="class"  # Ajustar según el nombre real de la columna target
        )
    
    # Procesar muestra del dataset grande
    large_dataset_path = data_dir / "keylogger_dataset_large.csv"
    if large_dataset_path.exists():
        summary_large = preprocessor.full_preprocessing_pipeline(
            large_dataset_path, 
            "keylogger_large_sample",
            sample_size=100000,  # Procesar solo 100k filas para empezar
            target_column="class"
        )


if __name__ == "__main__":
    main()