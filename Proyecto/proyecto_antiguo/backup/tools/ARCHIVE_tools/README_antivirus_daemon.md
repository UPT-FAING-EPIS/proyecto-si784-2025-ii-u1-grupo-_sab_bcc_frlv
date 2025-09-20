Antivirus daemon - build & usage

This daemon polls `config/antivirus_config.json`. When `enabled=true` it runs the existing Python inference script periodically and appends output to `logs/antivirus_daemon.log`.

Build (MSYS2 / MinGW64):
1. Open "MSYS2 MinGW 64-bit" shell.
2. Ensure toolchain installed:
   pacman -S --needed mingw-w64-x86_64-toolchain
3. Build:
   cd /c/Users/windows10/Documents/GitHub/Python_ML
   g++ -std=c++17 -O2 tools/antivirus_daemon.cpp -o tools/antivirus_daemon.exe

Build (MSVC):
1. Open "x64 Native Tools Command Prompt".
2. Run:
   cl.exe /EHsc tools\antivirus_daemon.cpp /Fe:tools\antivirus_daemon.exe

Run (PowerShell):
# Start in background (use Start-Process or a service manager):
Start-Process -FilePath .\tools\antivirus_daemon.exe -NoNewWindow

# Simple foreground run (for testing):
.\tools\antivirus_daemon.exe --model backup/modelo/modelo_keylogger_from_datos.onnx --input DATOS/Keylogger_Detection_Dataset.csv --interval 30

Notes:
- The daemon uses `python` from PATH to run `scripts/predecir_keylogger.py`. Ensure Python and required packages are installed.
- Logs are written to `logs/antivirus_daemon.log`.
- Modify `--interval` to control frequency.
