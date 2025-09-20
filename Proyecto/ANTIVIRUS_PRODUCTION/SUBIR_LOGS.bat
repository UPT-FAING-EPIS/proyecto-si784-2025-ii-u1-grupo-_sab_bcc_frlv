@echo off
chcp 65001 >nul
echo.
echo ========================================
echo  🛡️  SUBIR LOGS DEL ANTIVIRUS A RAILWAY
echo ========================================
echo.

cd /d "%~dp0"

REM Verificar si Python esta disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado
    echo    Instala Python desde https://python.org
    pause
    exit /b 1
)

echo 📦 Instalando dependencias necesarias...
python -m pip install requests >nul 2>&1

echo.
echo 🚀 Iniciando uploader...
echo.

python simple_uploader.py

echo.
echo ✅ Proceso completado
pause