#!/usr/bin/env python3
"""
Test de Detección ML - Prueba específica del detector de keyloggers
================================================================

Prueba el detector ML con datos sintéticos de red para verificar
que puede detectar patrones sospechosos.
"""

import time
import numpy as np
from antivirus.detectors.ml_detector import MLKeyloggerDetector

def test_ml_detection():
    """Prueba la detección ML con diferentes tipos de datos"""
    print("🤖 PRUEBA DE DETECCIÓN ML")
    print("=" * 50)
    
    # Inicializar detector
    print("1. Inicializando detector ML...")
    detector = MLKeyloggerDetector()
    
    if not detector.is_loaded():
        print("❌ Error: Detector ML no está cargado")
        return False
    
    print("✅ Detector ML inicializado")
    stats = detector.get_stats()
    print(f"   Tipo de modelo: {stats['model_type']}")
    print(f"   Features esperadas: 81")
    print(f"   Clases: {stats['label_classes']}")
    
    # Test 1: Datos normales (benignos)
    print("\n2. Probando datos normales (actividad benigna)...")
    benign_features = np.random.normal(0.3, 0.1, 81).astype(np.float32)
    benign_features = np.clip(benign_features, 0, 1)  # Mantener en rango [0,1]
    
    try:
        start_time = time.time()
        predictions, probabilities = detector.predict(benign_features.reshape(1, -1))
        pred_time = time.time() - start_time
        
        print(f"   Predicción: {predictions[0]}")
        print(f"   Probabilidad: {probabilities[0]:.4f}")
        print(f"   Tiempo: {pred_time:.4f}s")
        
    except Exception as e:
        print(f"   ❌ Error en predicción: {e}")
    
    # Test 2: Datos sospechosos (posible keylogger)
    print("\n3. Probando datos sospechosos (posible keylogger)...")
    suspicious_features = np.random.normal(0.7, 0.15, 81).astype(np.float32)
    suspicious_features = np.clip(suspicious_features, 0, 1)
    
    try:
        start_time = time.time()
        predictions, probabilities = detector.predict(suspicious_features.reshape(1, -1))
        pred_time = time.time() - start_time
        
        print(f"   Predicción: {predictions[0]}")
        print(f"   Probabilidad: {probabilities[0]:.4f}")
        print(f"   Tiempo: {pred_time:.4f}s")
        
    except Exception as e:
        print(f"   ❌ Error en predicción: {e}")
    
    # Test 3: Batch de múltiples predicciones
    print("\n4. Probando batch de múltiples predicciones...")
    batch_size = 10
    batch_features = np.random.normal(0.5, 0.2, (batch_size, 81)).astype(np.float32)
    batch_features = np.clip(batch_features, 0, 1)
    
    try:
        start_time = time.time()
        predictions, probabilities = detector.predict(batch_features)
        pred_time = time.time() - start_time
        
        print(f"   Predicciones procesadas: {len(predictions)}")
        print(f"   Tiempo total: {pred_time:.4f}s")
        print(f"   Tiempo promedio por predicción: {pred_time/len(predictions):.4f}s")
        
        # Mostrar resumen
        benign_count = sum(1 for p in predictions if p == 'Benign')
        keylogger_count = sum(1 for p in predictions if p == 'Keylogger')
        
        print(f"   Resultados: {benign_count} Benign, {keylogger_count} Keylogger")
        
    except Exception as e:
        print(f"   ❌ Error en batch: {e}")
    
    # Estadísticas finales
    print("\n5. Estadísticas finales del detector...")
    final_stats = detector.get_stats()
    
    for key, value in final_stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.4f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n✅ PRUEBA DE DETECCIÓN ML COMPLETADA")
    return True

def test_network_analysis():
    """Prueba el análisis de datos de red"""
    print("\n🌐 PRUEBA DE ANÁLISIS DE RED")
    print("=" * 50)
    
    try:
        detector = MLKeyloggerDetector()
        
        # Simular datos de red
        network_data = [
            {
                'src_ip': '192.168.1.100',
                'dst_ip': '8.8.8.8',
                'src_port': 45230,
                'dst_port': 443,
                'protocol': 'TCP',
                'bytes_sent': 1024,
                'bytes_received': 2048,
                'duration': 5.5,
                'timestamp': time.time()
            },
            {
                'src_ip': '192.168.1.100', 
                'dst_ip': '192.168.1.1',
                'src_port': 45231,
                'dst_port': 53,
                'protocol': 'UDP',
                'bytes_sent': 64,
                'bytes_received': 128,
                'duration': 0.1,
                'timestamp': time.time()
            }
        ]
        
        print("1. Analizando datos de red simulados...")
        results = detector.analyze_network_data(network_data)
        
        print(f"   Conexiones analizadas: {len(results)}")
        for i, result in enumerate(results):
            print(f"   Conexión {i+1}: Score de riesgo = {result.get('risk_score', 0):.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis de red: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🔬 SUITE DE PRUEBAS ML AVANZADAS")
    print("=" * 60)
    
    success_count = 0
    total_tests = 2
    
    # Test 1: Detección ML básica
    if test_ml_detection():
        success_count += 1
    
    # Test 2: Análisis de red
    if test_network_analysis():
        success_count += 1
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"Pruebas exitosas: {success_count}/{total_tests}")
    print(f"Tasa de éxito: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 TODAS LAS PRUEBAS PASARON")
        return True
    else:
        print("⚠️ ALGUNAS PRUEBAS FALLARON")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)