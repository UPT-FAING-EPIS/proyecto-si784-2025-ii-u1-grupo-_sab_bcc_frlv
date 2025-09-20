@echo off
title Desinstalador Anti-Keylogger
color 0C
chcp 65001 >nul

echo.
echo  ================================================================
echo   [TRASH] DESINSTALADOR ANTI-KEYLOGGER
echo  ================================================================
echo.
echo   Este script eliminara completamente el Anti-Keylogger
echo   Se eliminara la instalacion, archivos y accesos directos
echo.
echo  ================================================================
echo.
pause

cls
echo.
echo  [TRASH] Iniciando desinstalacion...
echo.

python uninstall_antivirus.py

echo.
echo  ================================================================
echo   [CHECK] Proceso de desinstalacion completado
echo  ================================================================
echo.
pause