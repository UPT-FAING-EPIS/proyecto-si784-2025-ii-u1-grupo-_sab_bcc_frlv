
import time
import json
from pathlib import Path
import subprocess
import sys
import argparse
import psutil


# Configuración
# Carpeta a monitorear (por defecto, Descargas del usuario)
WATCH_DIR = Path.home() / 'Downloads'
# Umbral para considerar probabilidad de keylogger como alerta
ALERT_THRESHOLD = 0.6
# Archivos del modelo (esperados en el mismo directorio que este script)
MODEL_DIR = Path(__file__).resolve().parent
ONNX_PATH = MODEL_DIR / 'modelo_keylogger_from_datos.onnx'
FEATS_PATH = MODEL_DIR / 'modelo_keylogger_from_datos_features.json'
LABELS_PATH = MODEL_DIR / 'label_classes.json'
PREDICT_SCRIPT = MODEL_DIR / 'predecir_keylogger.py'
# Archivo de log
LOG_PATH = MODEL_DIR / 'monitor_log.txt'
ALERT_LOG_PATH = MODEL_DIR / 'monitor_alerts.txt'
# Utilidad para registrar en log
def log_event(msg: str):
    print(msg)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def log_alert(msg: str, extra: dict = None):
    print(msg)
    with open(ALERT_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
        if extra:
            json.dump(extra, f, ensure_ascii=False, indent=2)
            f.write('\n')


# Registro de tiempos de modificación para detectar cambios
seen_mtimes = {}


# Detecta si es un archivo regular (no carpeta)
def is_file_to_analyze(path: Path) -> bool:
    return path.is_file() and not path.name.startswith('.')


# Función base para extracción de features según tipo de archivo

import hashlib
try:
    import pefile
except ImportError:
    pefile = None
try:
    import magic
except ImportError:
    magic = None
def extract_features_from_file(path: Path) -> dict:
    """Extrae features básicos según el tipo de archivo."""
    features = {'file_size': path.stat().st_size}
    ext = path.suffix.lower()
    # Ejecutables
    if ext in ['.exe', '.dll'] and pefile:
        try:
            pe = pefile.PE(str(path))
            features['num_sections'] = len(pe.sections)
            features['has_imports'] = int(hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'))
            features['entropy'] = sum([s.get_entropy() for s in pe.sections]) / len(pe.sections) if pe.sections else 0
            with open(path, 'rb') as f:
                features['md5'] = hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            log_event(f"[WARN] No se pudieron extraer features PE: {e}")
    # Documentos
    elif ext in ['.pdf', '.docx', '.doc', '.xlsx', '.pptx']:
        features['is_document'] = 1
    # Imágenes
    elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
        features['is_image'] = 1
    # Comprimidos
    elif ext in ['.zip', '.rar', '.7z']:
        features['is_archive'] = 1
    # Audio/video
    elif ext in ['.mp3', '.wav', '.mp4', '.avi', '.mkv']:
        features['is_media'] = 1
    # Otros: solo tamaño
    return features

def run_inference_on_file(path: Path):
    log_event(f"\n[DETECCIÓN] Analizando archivo: {path}")
    features = extract_features_from_file(path)
    import tempfile
    import pandas as pd
    feats_list = list(json.load(open(FEATS_PATH)))
    row = {k: features.get(k, 0) for k in feats_list}
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.csv') as tmp:
        pd.DataFrame([row]).to_csv(tmp.name, index=False)
        tmp_path = tmp.name
    cmd = [sys.executable, str(PREDICT_SCRIPT), '--onnx', str(ONNX_PATH), '--input', tmp_path, '--features', str(FEATS_PATH)]
    log_event(f"[EJECUTANDO] {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    log_event("[STDOUT]\n" + proc.stdout)
    if proc.stderr:
        log_event("[STDERR]\n" + proc.stderr)
    if 'Probabilidades (primeras 5 filas):' in proc.stdout:
        try:
            import re
            m = re.search(r"\[\[([^\]]+)\]", proc.stdout)
            if m:
                vals = m.group(1).strip().split()
                if len(vals) >= 2:
                    benign = float(vals[0])
                    keylog = float(vals[1])
                    if keylog >= ALERT_THRESHOLD:
                        alert_msg = f"[ALERTA] Alta probabilidad de keylogger ({keylog:.2f}) en {path}"
                        alert_data = {
                            'archivo': str(path),
                            'probabilidad_keylogger': keylog,
                            'features': features,
                            'cmd': ' '.join(cmd),
                            'stdout': proc.stdout,
                            'stderr': proc.stderr
                        }
                        log_alert(alert_msg, alert_data)
                        # Detener análisis lanzando excepción
                        raise SystemExit(f"ALERTA: Keylogger detectado en {path}\nRevisa monitor_alerts.txt para detalles.")
        except Exception:
            pass


def scan_once():
    global seen_mtimes
    if not WATCH_DIR.exists():
        print(f"[WARN] Carpeta a monitorear no existe: {WATCH_DIR}")
        return
    for path in WATCH_DIR.iterdir():
        if not is_file_to_analyze(path):
            continue
        try:
            mtime = path.stat().st_mtime
        except Exception:
            continue
        last = seen_mtimes.get(path)
        if last is None or mtime > last:
            seen_mtimes[path] = mtime
            run_inference_on_file(path)

# Escaneo de procesos en segundo plano
def scan_background_processes():
    log_event("\n[INFO] Escaneando procesos en segundo plano...")
    found = False
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            info = proc.info
            exe_path = info.get('exe')
            if exe_path and Path(exe_path).exists():
                features = extract_features_from_file(Path(exe_path))
                import tempfile
                import pandas as pd
                feats_list = list(json.load(open(FEATS_PATH)))
                row = {k: features.get(k, 0) for k in feats_list}
                with tempfile.NamedTemporaryFile('w', delete=False, suffix='.csv') as tmp:
                    pd.DataFrame([row]).to_csv(tmp.name, index=False)
                    tmp_path = tmp.name
                cmd = [sys.executable, str(PREDICT_SCRIPT), '--onnx', str(ONNX_PATH), '--input', tmp_path, '--features', str(FEATS_PATH)]
                log_event(f"[EJECUTANDO proceso] {' '.join(cmd)}")
                proc2 = subprocess.run(cmd, capture_output=True, text=True)
                log_event("[STDOUT proceso]\n" + proc2.stdout)
                if proc2.stderr:
                    log_event("[STDERR proceso]\n" + proc2.stderr)
                if 'Probabilidades (primeras 5 filas):' in proc2.stdout:
                    try:
                        import re
                        m = re.search(r"\[\[([^\]]+)\]", proc2.stdout)
                        if m:
                            vals = m.group(1).strip().split()
                            if len(vals) >= 2:
                                benign = float(vals[0])
                                keylog = float(vals[1])
                                if keylog >= ALERT_THRESHOLD:
                                    alert_msg = f"[ALERTA] Proceso sospechoso: {info['name']} (PID {info['pid']}) probabilidad keylogger {keylog:.2f}"
                                    alert_data = {
                                        'proceso': info['name'],
                                        'pid': info['pid'],
                                        'ruta': exe_path,
                                        'probabilidad_keylogger': keylog,
                                        'features': features,
                                        'cmd': ' '.join(cmd),
                                        'stdout': proc2.stdout,
                                        'stderr': proc2.stderr
                                    }
                                    log_alert(alert_msg, alert_data)
                                    raise SystemExit(f"ALERTA: Proceso sospechoso detectado: {info['name']} (PID {info['pid']})\nRevisa monitor_alerts.txt para detalles.")
                    except Exception:
                        pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if not found:
        log_event("[INFO] No se detectaron procesos sospechosos en segundo plano.")



def main():
    parser = argparse.ArgumentParser(description="Monitor de keyloggers en Descargas")
    parser.add_argument('--mode', choices=['once', 'timed', 'loop'], default='once', help='Modo de ejecución: once (una vez), timed (por tiempo), loop (bucle infinito)')
    parser.add_argument('--interval', type=int, default=10, help='Intervalo en segundos entre escaneos (solo timed/loop)')
    parser.add_argument('--duration', type=int, default=60, help='Duración en segundos (solo modo timed)')
    args = parser.parse_args()

    log_event(f"[INFO] Monitoreando carpeta: {WATCH_DIR}")
    log_event("Presiona Ctrl+C para salir.")

    if args.mode == 'once':
        scan_once()
        scan_background_processes()
        log_event("[INFO] Monitoreo finalizado. Revisa el archivo monitor_log.txt para los resultados.")
    elif args.mode == 'timed':
        import time
        end_time = time.time() + args.duration
        try:
            while time.time() < end_time:
                scan_once()
                scan_background_processes()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            log_event("[INFO] Monitoreo interrumpido por el usuario.")
        log_event("[INFO] Monitoreo por tiempo finalizado. Revisa el archivo monitor_log.txt para los resultados.")
    elif args.mode == 'loop':
        import time
        try:
            while True:
                scan_once()
                scan_background_processes()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            log_event("[INFO] Monitoreo interrumpido por el usuario.")
        log_event("[INFO] Monitoreo en bucle finalizado. Revisa el archivo monitor_log.txt para los resultados.")

if __name__ == '__main__':
    main()