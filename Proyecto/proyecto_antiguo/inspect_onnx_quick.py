#!/usr/bin/env python3
"""
Inspección rápida del modelo ONNX
"""

import onnxruntime as ort
import numpy as np

def inspect_onnx_model():
    """Inspecciona la estructura del modelo ONNX"""
    model_path = "models/development/modelo_keylogger_from_datos.onnx"
    
    print("🔍 INSPECCIÓN DEL MODELO ONNX")
    print("=" * 50)
    
    try:
        # Cargar el modelo
        session = ort.InferenceSession(model_path)
        
        print("📋 INFORMACIÓN DEL MODELO:")
        print(f"   Archivo: {model_path}")
        
        # Inputs
        print("\n📥 INPUTS:")
        for i, input_desc in enumerate(session.get_inputs()):
            print(f"   {i}: {input_desc.name}")
            print(f"      Tipo: {input_desc.type}")
            print(f"      Shape: {input_desc.shape}")
        
        # Outputs
        print("\n📤 OUTPUTS:")
        for i, output_desc in enumerate(session.get_outputs()):
            print(f"   {i}: {output_desc.name}")
            print(f"      Tipo: {output_desc.type}")
            print(f"      Shape: {output_desc.shape}")
        
        # Test con datos sintéticos
        print("\n🧪 PRUEBA CON DATOS SINTÉTICOS:")
        input_name = session.get_inputs()[0].name
        test_data = np.random.rand(1, 81).astype(np.float32)
        
        print(f"   Input name: {input_name}")
        print(f"   Test data shape: {test_data.shape}")
        
        try:
            outputs = session.run(None, {input_name: test_data})
            print(f"   Número de outputs: {len(outputs)}")
            
            for i, output in enumerate(outputs):
                print(f"   Output {i} shape: {output.shape}")
                print(f"   Output {i} tipo: {type(output)}")
                print(f"   Output {i} sample: {output[:3] if len(output) > 3 else output}")
                
        except Exception as e:
            print(f"   ❌ Error en prueba: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inspeccionando modelo: {e}")
        return False

if __name__ == "__main__":
    success = inspect_onnx_model()
    exit(0 if success else 1)