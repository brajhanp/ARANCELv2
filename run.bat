@echo off
REM Script rápido para iniciar el servidor ARANCELv2
REM Simplemente ejecuta este archivo para iniciar el servidor

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no se encuentra instalado.
    echo Descargalo desde: https://www.python.org/
    pause
    exit /b 1
)

REM Verificar si venv existe
if not exist venv (
    echo ERROR: El entorno virtual no existe.
    echo Por favor ejecuta primero: setup.bat
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Iniciando ARANCELv2
echo ========================================
echo.

REM Activar venv y ejecutar servidor
call venv\Scripts\activate.bat
python manage.py runserver

echo.
echo El servidor se ha detenido.
pause
