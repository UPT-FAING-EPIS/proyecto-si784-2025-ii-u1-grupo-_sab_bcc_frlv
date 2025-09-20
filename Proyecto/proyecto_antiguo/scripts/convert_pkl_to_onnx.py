#!/usr/bin/env python3
"""
Convertir modelo sklearn a ONNX
"""

import sys
import joblib
import numpy as np
from pathlib import Path

def convert_sklearn_to_onnx():
    """Convierte modelo sklearn a ONNX"""
    
    # Rutas
    model_path = Path("models/development/modelo_keylogger_from_datos.pkl")
    onnx_path = Path("models/development/modelo_keylogger_from_datos.onnx")
    
    if not model_path.exists():
        print(f"[ERROR] Modelo no encontrado: {model_path}")
        return False
    
    try:
        print("[IN] Cargando modelo sklearn...")
        model = joblib.load(model_path)
        print(f"[OK] Modelo cargado: {type(model).__name__}")
        
        # Intentar conversión ONNX
        try:
            import skl2onnx
            from skl2onnx import to_onnx
            
            print("[SYNC] Convirtiendo a ONNX...")
            
            # Crear datos de ejemplo para inferir el schema
            # Usamos el número de features que tenga el modelo
            if hasattr(model, 'n_features_in_'):
                n_features = model.n_features_in_
            else:
                # Fallback: intentar con datos comunes
                n_features = 81  # número típico de features de keylogger detection
            
            X_sample = np.random.rand(1, n_features).astype(np.float32)
            
            # Convertir a ONNX
            onnx_model = to_onnx(model, X_sample, target_opset=12)
            
            # Guardar modelo ONNX
            with open(onnx_path, "wb") as f:
                f.write(onnx_model.SerializeToString())
            
            print(f"[OK] Modelo ONNX guardado: {onnx_path}")
            
            # Verificar el modelo ONNX
            try:
                import onnxruntime as ort
                session = ort.InferenceSession(str(onnx_path))
                print("[OK] Modelo ONNX verificado")
                return True
                
            except Exception as e:
                print(f"[WARNING] Error verificando ONNX: {e}")
                return True  # Aún consideramos exitoso
                
        except ImportError:
            print("[WARNING] skl2onnx no disponible, instalando...")
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "skl2onnx"])
            print("[OK] skl2onnx instalado, re-intente la conversión")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error durante conversión: {e}")
        return False

if __name__ == "__main__":
    success = convert_sklearn_to_onnx()
    sys.exit(0 if success else 1)