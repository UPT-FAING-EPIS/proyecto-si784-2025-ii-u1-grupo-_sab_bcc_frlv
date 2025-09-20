@echo off
title Instalador Anti-Keylogger
color 0B
chcp 65001 >nul

echo.
echo  ================================================================
echo   [SHIELD] INSTALADOR ANTI-KEYLOGGER PROTECTION
echo  ================================================================
echo.
echo   Este instalador configurara el Anti-Keylogger en tu PC
echo   Instalara dependencias y creara accesos directos automaticamente
echo.
echo  ================================================================
echo.
pause

cls
echo.
echo  [ROCKET] Iniciando instalacion...
echo.

python install_antivirus.py

echo.
echo  ================================================================
echo   [CHECK] Proceso de instalacion completado
echo  ================================================================
echo.
pause