"""
Orquestador Principal del Pipeline de ML - Anti-Keylogger
========================================================

Este script orquesta todo el pipeline de machine learning:
1. Preprocesamiento de datos
2. Entrenamiento de modelos
3. Evaluación de modelos
4. Deployment y predicciones

Uso:
    python run_pipeline.py --stage [all|preprocess|train|evaluate|predict]
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
import json
from typing import Optional

# Agregar directorios al path
base_dir = Path(__file__).parent.parent
sys.path.append(str(base_dir))
sys.path.append(str(base_dir / "data_science"))
sys.path.append(str(base_dir / "ml_pipeline" / "training"))
sys.path.append(str(base_dir / "ml_pipeline" / "evaluation"))
sys.path.append(str(base_dir / "ml_pipeline" / "deployment"))

# Imports de los módulos del pipeline
try:
    from ml_pipeline.training.data_preprocessing import DataPreprocessor
    from ml_pipeline.training.train_model import AdvancedModelTrainer
    from ml_pipeline.evaluation.evaluate_model import ModelEvaluator
    from ml_pipeline.deployment.predict_model import ModelPredictor, BatchProcessor
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de que todos los archivos del pipeline estén en su lugar")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MLPipelineOrchestrator:
    """Orquestador del pipeline completo de ML."""
    
    def __init__(self, base_dir: Path = None):
        # Si no se especifica base_dir, usar el directorio padre del script
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)
        self.results = {}
        
        # Directorios principales
        self.data_dir = self.base_dir / "data"
        self.models_dir = self.base_dir / "models"
        self.logs_dir = self.base_dir / "logs"
        
        # Crear directorios si no existen
        self.logs_dir.mkdir(exist_ok=True)
        
    def run_preprocessing(self, force_reprocess: bool = False) -> bool:
        """Ejecuta el preprocesamiento de datos."""
        logger.info("[SYNC] Iniciando preprocesamiento de datos...")
        
        try:
            # Buscar datos raw
            raw_data_dir = self.data_dir / "raw"
            csv_files = list(raw_data_dir.glob("*.csv"))
            
            if not csv_files:
                logger.error("No se encontraron archivos CSV en data/raw/")
                return False
            
            # Inicializar preprocessor
            preprocessor = DataPreprocessor()
            
            processed_files = []
            for csv_file in csv_files:
                logger.info(f"Procesando: {csv_file.name}")
                
                # Verificar si ya está procesado
                processed_dir = self.data_dir / "processed"
                parquet_file = processed_dir / f"{csv_file.stem}_cleaned.parquet"
                
                if parquet_file.exists() and not force_reprocess:
                    logger.info(f"Archivo ya procesado: {parquet_file.name}")
                    processed_files.append(parquet_file)
                    continue
                
                # Cargar y procesar datos
                df = preprocessor.load_data(csv_file)
                
                # Análisis de calidad
                quality_report = preprocessor.analyze_data_quality(df)
                logger.info(f"Calidad de datos - Missing: {quality_report['missing_percentage']:.2%}")
                
                # Limpiar datos
                df_clean = preprocessor.clean_data(df)
                
                # Exportar en múltiples formatos
                output_files = preprocessor.export_processed_data(
                    df_clean, 
                    f"{csv_file.stem}_cleaned",
                    formats=['parquet', 'pickle']
                )
                
                processed_files.extend(output_files)
                logger.info(f"[OK] Procesado: {csv_file.name}")
            
            self.results['preprocessing'] = {
                'status': 'success',
                'processed_files': [str(f) for f in processed_files],
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("[OK] Preprocesamiento completado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Error en preprocesamiento: {e}")
            self.results['preprocessing'] = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def run_training(self) -> bool:
        """Ejecuta el entrenamiento de modelos."""
        logger.info("[START] Iniciando entrenamiento de modelos...")
        
        try:
            # Buscar datos procesados
            processed_dir = self.data_dir / "processed"
            parquet_files = list(processed_dir.glob("*_cleaned.parquet"))
            
            if not parquet_files:
                logger.error("No se encontraron datos procesados. Ejecuta preprocesamiento primero.")
                return False
            
            # Usar el primer archivo encontrado (o el más grande)
            data_file = max(parquet_files, key=lambda x: x.stat().st_size)
            logger.info(f"Entrenando con: {data_file.name}")
            
            # Inicializar trainer
            trainer = AdvancedModelTrainer(self.models_dir)
            
            # Ejecutar pipeline completo
            training_summary = trainer.full_training_pipeline(
                data_path=data_file,
                target_column="class"  # Ajustar según el dataset
            )
            
            if 'error' not in training_summary:
                self.results['training'] = {
                    'status': 'success',
                    'best_model': training_summary['best_model'],
                    'model_paths': training_summary['model_paths'],
                    'summary': training_summary,
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info(f"[OK] Entrenamiento completado. Mejor modelo: {training_summary['best_model']}")
                return True
            else:
                raise Exception(training_summary['error'])
                
        except Exception as e:
            logger.error(f"[ERROR] Error en entrenamiento: {e}")
            self.results['training'] = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def run_evaluation(self) -> bool:
        """Ejecuta la evaluación de modelos."""
        logger.info("[SEARCH] Iniciando evaluación de modelos...")
        
        try:
            # Buscar modelos entrenados
            models_dir = self.models_dir / "development"
            model_files = list(models_dir.glob("*.pkl"))
            
            if not model_files:
                logger.error("No se encontraron modelos entrenados. Ejecuta entrenamiento primero.")
                return False
            
            # Buscar datos de test
            processed_dir = self.data_dir / "processed"
            test_files = list(processed_dir.glob("*.parquet"))
            
            if not test_files:
                logger.error("No se encontraron datos de test.")
                return False
            
            test_data_path = test_files[0]
            
            # Inicializar evaluador
            evaluator = ModelEvaluator(self.models_dir / "evaluation")
            
            # Evaluar todos los modelos
            for model_path in model_files:
                logger.info(f"Evaluando: {model_path.name}")
                
                evaluator.evaluate_model_comprehensive(
                    model_path=model_path,
                    test_data_path=test_data_path,
                    target_column="class"
                )
            
            # Generar resumen
            evaluation_summary = evaluator.generate_evaluation_summary()
            
            self.results['evaluation'] = {
                'status': 'success',
                'summary': evaluation_summary,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("[OK] Evaluación completada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Error en evaluación: {e}")
            self.results['evaluation'] = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def run_prediction(self, input_file: Optional[Path] = None) -> bool:
        """Ejecuta predicciones con el mejor modelo."""
        logger.info("[TARGET] Iniciando predicciones...")
        
        try:
            # Buscar el mejor modelo
            models_dir = self.models_dir / "development"
            model_files = list(models_dir.glob("*.pkl"))
            
            if not model_files:
                logger.error("No se encontraron modelos. Ejecuta entrenamiento primero.")
                return False
            
            # Usar el modelo más reciente
            latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
            
            # Buscar metadatos
            metadata_files = list(models_dir.glob(f"{latest_model.stem}*metadata*.json"))
            metadata_path = metadata_files[0] if metadata_files else None
            
            # Crear predictor
            predictor = ModelPredictor(latest_model, metadata_path)
            
            # Determinar archivo de entrada
            if input_file is None:
                processed_dir = self.data_dir / "processed"
                parquet_files = list(processed_dir.glob("*.parquet"))
                if not parquet_files:
                    logger.error("No se encontraron datos para predicción.")
                    return False
                input_file = parquet_files[0]
            
            logger.info(f"Realizando predicciones con: {input_file.name}")
            
            # Crear procesador batch
            batch_processor = BatchProcessor(predictor, self.models_dir / "predictions")
            
            # Procesar archivo
            if input_file.suffix == '.parquet':
                result_path = batch_processor.process_parquet_file(
                    input_file, 
                    target_column="class"
                )
            elif input_file.suffix == '.csv':
                result_path = batch_processor.process_csv_file(
                    input_file,
                    target_column="class"
                )
            else:
                raise ValueError(f"Formato no soportado: {input_file.suffix}")
            
            # Obtener estadísticas
            stats = predictor.get_stats()
            
            self.results['prediction'] = {
                'status': 'success',
                'model_used': str(latest_model),
                'input_file': str(input_file),
                'output_file': str(result_path),
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"[OK] Predicciones completadas. Resultados en: {result_path}")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Error en predicciones: {e}")
            self.results['prediction'] = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def run_full_pipeline(self, force_reprocess: bool = False) -> bool:
        """Ejecuta el pipeline completo."""
        logger.info("[START] Iniciando pipeline completo de ML...")
        
        start_time = datetime.now()
        
        # Ejecutar cada etapa
        success = True
        
        if not self.run_preprocessing(force_reprocess):
            success = False
        
        if success and not self.run_training():
            success = False
        
        if success and not self.run_evaluation():
            success = False
        
        if success and not self.run_prediction():
            success = False
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Resumen final
        pipeline_summary = {
            'pipeline_status': 'success' if success else 'failed',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'stages_results': self.results
        }
        
        # Guardar resumen
        summary_file = self.logs_dir / f"pipeline_summary_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(pipeline_summary, f, indent=2, default=str)
        
        if success:
            logger.info(f"[OK] Pipeline completado exitosamente en {duration}")
            logger.info(f"[INFO] Resumen guardado en: {summary_file}")
        else:
            logger.error(f"[ERROR] Pipeline falló después de {duration}")
        
        return success
    
    def print_summary(self):
        """Imprime un resumen de los resultados."""
        print("\n" + "="*60)
        print("[DATA] RESUMEN DEL PIPELINE DE ML")
        print("="*60)
        
        for stage, result in self.results.items():
            status = result.get('status', 'unknown')
            emoji = "[OK]" if status == 'success' else "[ERROR]"
            
            print(f"\n{emoji} {stage.upper()}: {status}")
            
            if status == 'success':
                if stage == 'training' and 'best_model' in result:
                    print(f"   Mejor modelo: {result['best_model']}")
                elif stage == 'prediction' and 'stats' in result:
                    total_preds = result['stats']['usage_stats']['total_predictions']
                    print(f"   Predicciones realizadas: {total_preds:,}")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        print("\n" + "="*60)


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Pipeline de ML para detección de keyloggers')
    parser.add_argument('--stage', 
                       choices=['all', 'preprocess', 'train', 'evaluate', 'predict'],
                       default='all',
                       help='Etapa del pipeline a ejecutar')
    parser.add_argument('--force-reprocess', 
                       action='store_true',
                       help='Forzar reprocesamiento de datos existentes')
    parser.add_argument('--input-file',
                       type=Path,
                       help='Archivo de entrada para predicciones')
    
    args = parser.parse_args()
    
    # Crear orquestador
    orchestrator = MLPipelineOrchestrator()
    
    # Ejecutar etapa solicitada
    success = False
    
    if args.stage == 'all':
        success = orchestrator.run_full_pipeline(args.force_reprocess)
    elif args.stage == 'preprocess':
        success = orchestrator.run_preprocessing(args.force_reprocess)
    elif args.stage == 'train':
        success = orchestrator.run_training()
    elif args.stage == 'evaluate':
        success = orchestrator.run_evaluation()
    elif args.stage == 'predict':
        success = orchestrator.run_prediction(args.input_file)
    
    # Mostrar resumen
    orchestrator.print_summary()
    
    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()