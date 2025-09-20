"""
Pipeline para Dataset Grande - Anti-Keylogger
=============================================

Versión optimizada para manejar el dataset grande.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_large_dataset():
    """Procesa el dataset grande por chunks"""
    logger.info("[START] Procesando dataset grande...")
    
    # Obtener el directorio base del proyecto (dos niveles arriba)
    base_dir = Path(__file__).parent.parent.parent
    raw_file = base_dir / "data" / "raw" / "keylogger_dataset_large.csv"
    processed_dir = base_dir / "data" / "processed"
    processed_dir.mkdir(exist_ok=True)
    
    chunk_size = 10000  # Procesar de 10k en 10k
    processed_chunks = []
    
    logger.info(f"[DATA] Leyendo {raw_file.name} en chunks de {chunk_size:,}...")
    
    for i, chunk in enumerate(pd.read_csv(raw_file, chunksize=chunk_size)):
        logger.info(f"   Procesando chunk {i+1}: {len(chunk):,} filas")
        
        # Limpieza básica
        chunk_clean = chunk.dropna()
        
        # Identificar columnas numéricas
        numeric_cols = chunk_clean.select_dtypes(include=[np.number]).columns
        string_cols = ['Flow ID', ' Source IP', ' Destination IP', ' Timestamp']
        
        # Mantener solo numéricas y target
        keep_cols = list(numeric_cols) + ['Class']
        chunk_final = chunk_clean[keep_cols]
        
        processed_chunks.append(chunk_final)
        
        if i >= 4:  # Procesar solo los primeros 5 chunks como demo
            logger.info("   [PACKAGE] Procesando primeros 5 chunks como demostración")
            break
    
    # Combinar chunks
    logger.info("[SYNC] Combinando chunks...")
    df_large = pd.concat(processed_chunks, ignore_index=True)
    
    logger.info(f"[DATA] Dataset grande procesado: {len(df_large):,} filas")
    
    # Guardar
    output_file = processed_dir / "dataset_large_sample.parquet"
    df_large.to_parquet(output_file, index=False)
    
    logger.info(f"[OK] Guardado: {output_file}")
    return True

if __name__ == "__main__":
    process_large_dataset()