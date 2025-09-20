@echo off
title Instalador Anti-Keylogger
color 0B
chcp 65001 >nul 2>&1

cls
echo.
echo  ================================================================
echo                INSTALADOR ANTI-KEYLOGGER
echo  ================================================================
echo.
echo   * Este instalador configurara el Anti-Keylogger en tu PC
echo   * Instalara dependencias automaticamente
echo   * Creara accesos directos en el escritorio
echo   * Verificara que todo funcione correctamente
echo.
echo  ================================================================
echo.
echo   REQUISITOS:
echo   - Python 3.8 o superior
echo   - Conexion a internet
echo   - Permisos de administrador (recomendado)
echo.
echo  ================================================================
echo.
set /p continuar="Presiona ENTER para continuar o CTRL+C para cancelar..."

cls
echo.
echo  ================================================================
echo              INICIANDO INSTALACION...
echo  ================================================================
echo.

python install_antivirus.py

echo.
echo  ================================================================
echo              INSTALACION COMPLETADA
echo  ================================================================
echo.
echo   El Anti-Keylogger ha sido instalado en tu sistema.
echo   Revisa los mensajes anteriores para mas detalles.
echo.
pause