
import sys
import subprocess
from pathlib import Path

MENU = '''\n================= ANTIVIRUS CLI INTERACTIVO =================
1. Analizar el dataset de ejemplo
2. Analizar un archivo CSV propio
3. Salir
============================================================='''

def analizar_dataset_ejemplo():
    print("\n[INFO] Ejecutando inferencia sobre el dataset de ejemplo...")
    cmd = [sys.executable, 'predecir_keylogger.py', '--onnx', 'modelo_keylogger_from_datos.onnx', '--input', 'Keylogger_Detection_Dataset.csv', '--features', 'modelo_keylogger_from_datos_features.json']
    print(f"[EJECUTANDO] {' '.join(cmd)}\n")
    subprocess.run(cmd)

def analizar_archivo_personal():
    ruta = input("\nIngrese la ruta al archivo CSV a analizar: ").strip()
    if not Path(ruta).exists():
        print("[ERROR] El archivo no existe.")
        return
    print(f"[INFO] Ejecutando inferencia sobre: {ruta}")
    cmd = [sys.executable, 'predecir_keylogger.py', '--onnx', 'modelo_keylogger_from_datos.onnx', '--input', ruta, '--features', 'modelo_keylogger_from_datos_features.json']
    print(f"[EJECUTANDO] {' '.join(cmd)}\n")
    subprocess.run(cmd)

def main():
    while True:
        print(MENU)
        opcion = input("Seleccione una opción: ").strip()
        if opcion == '1':
            analizar_dataset_ejemplo()
        elif opcion == '2':
            analizar_archivo_personal()
        elif opcion == '3':
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == '__main__':
    main()
