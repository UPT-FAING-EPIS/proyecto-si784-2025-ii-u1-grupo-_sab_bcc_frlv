#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')
from main import read_real_detections, read_real_stats, read_real_notifications
import json

def test_real_data():
    print("=== PROBANDO DATOS REALES ===")
    print()
    
    # Probar estadísticas
    print("📊 ESTADÍSTICAS REALES:")
    try:
        stats = read_real_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print()
    except Exception as e:
        print(f"  Error en estadísticas: {e}")
        print()
    
    # Probar detecciones
    print("🔍 DETECCIONES REALES (últimas 3):")
    try:
        detections = read_real_detections()
        for i, detection in enumerate(detections[:3]):
            print(f"  {i+1}. {detection['program_name']} - {detection['threat_level']} ({detection['confidence']}%)")
        print(f"✅ Total detecciones encontradas: {len(detections)}")
        print()
    except Exception as e:
        print(f"  Error en detecciones: {e}")
        print()
    
    # Probar notificaciones
    print("🔔 NOTIFICACIONES REALES (últimas 2):")
    try:
        notifications = read_real_notifications()
        for i, notif in enumerate(notifications[:2]):
            print(f"  {i+1}. {notif['message']} - {notif['type']}")
        print(f"✅ Total notificaciones encontradas: {len(notifications)}")
    except Exception as e:
        print(f"  Error en notificaciones: {e}")

if __name__ == "__main__":
    test_real_data()