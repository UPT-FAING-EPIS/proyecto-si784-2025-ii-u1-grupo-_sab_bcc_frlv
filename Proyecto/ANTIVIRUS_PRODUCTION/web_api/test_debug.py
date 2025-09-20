#!/usr/bin/env python3
import requests
import json

print('🔍 Verificando debug endpoint...')
response = requests.get('https://proyecto-anti-keylogger-production.up.railway.app/debug-dashboard')
print(f'Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    print('✅ Debug info:')
    print(f'   Timestamp: {data.get("timestamp", "N/A")}')
    print(f'   Logs subidos disponibles: {data.get("uploaded_logs_available", False)}')
    print(f'   Security log existe: {data.get("uploaded_security_exists", False)}')
    print(f'   Antivirus log existe: {data.get("uploaded_antivirus_exists", False)}')
    print(f'   Tamaño security log: {data.get("uploaded_security_size", 0)} bytes')
    print(f'   Detecciones: {data.get("detections_count", 0)}')
    print(f'   Notificaciones: {data.get("notifications_count", 0)}')
    if data.get('sample_detection'):
        sample = data['sample_detection']
        print(f'   Muestra detección: {sample.get("program_name")} - {sample.get("threat_level")}')
else:
    print(f'❌ Error: {response.text}')