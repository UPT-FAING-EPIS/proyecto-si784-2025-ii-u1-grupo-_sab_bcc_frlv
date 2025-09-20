#!/usr/bin/env python3
"""
Debug del sistema de logs en Railway
===================================
"""

import requests
import json

def test_railway_endpoints():
    """Probar todos los endpoints de Railway"""
    base_url = "https://proyecto-anti-keylogger-production.up.railway.app"
    
    endpoints = [
        "/api/stats/summary",
        "/api/detections/recent", 
        "/api/notifications"
    ]
    
    print("🔍 TESTING RAILWAY ENDPOINTS")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            print(f"\n📡 Testing: {base_url}{endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   Data: Lista con {len(data)} elementos")
                    if len(data) > 0:
                        print(f"   Primer elemento: {list(data[0].keys()) if data[0] else 'Vacío'}")
                elif isinstance(data, dict):
                    print(f"   Data: {list(data.keys())}")
                    print(f"   Valores: {data}")
                else:
                    print(f"   Data: {type(data)} - {data}")
            else:
                print(f"   Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test completado")

if __name__ == "__main__":
    test_railway_endpoints()