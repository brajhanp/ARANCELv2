@echo off
REM Script para iniciar el servidor Django con ngrok
REM Requiere tener ngrok instalado

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ========================================
echo   Iniciando ARANCELv2 con ngrok
echo ========================================
echo.

REM Verificar si ngrok existe
where ngrok >nul 2>&1
if errorlevel 1 (
    echo ERROR: ngrok no se encuentra en el PATH.
    echo.
    echo Para usar este script:
    echo 1. Descarga ngrok desde: https://ngrok.com/download
    echo 2. Extrae ngrok.exe en una carpeta
    echo 3. Agrega esa carpeta al PATH de Windows
    echo    O modifica este script para usar la ruta completa
    echo.
    echo Alternativa: Ejecuta ngrok manualmente en otra ventana:
    echo    ngrok http 8000
    echo.
    pause
    exit /b 1
)

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no se encuentra instalado.
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

echo Iniciando servidor Django en segundo plano...
start "Django Server" cmd /k "call venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000"

echo Esperando 3 segundos para que el servidor inicie...
timeout /t 3 /nobreak >nul

echo.
echo Iniciando ngrok...
echo.
echo ========================================
echo   Tu URL publica aparecera abajo
echo   Compartela para acceder desde cualquier lugar
echo ========================================
echo.
echo Presiona Ctrl+C para detener ngrok y el servidor
echo.

REM Iniciar ngrok
ngrok http 8000

REM Al cerrar ngrok, cerrar también el servidor Django
echo.
echo Deteniendo servidor Django...
taskkill /FI "WINDOWTITLE eq Django Server*" /T /F >nul 2>&1

echo.
echo ========================================
echo   Servidor detenido correctamente
echo ========================================
pause

