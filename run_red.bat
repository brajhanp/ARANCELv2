@echo off
REM Script para iniciar el servidor ARANCELv2 en modo RED
REM Permite acceso desde otros dispositivos en la misma red

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
echo   Iniciando ARANCELv2 en modo RED
echo ========================================
echo.

REM Obtener la IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    set IP=!IP:~1!
    goto :found
)
:found

echo Tu IP local es: %IP%
echo.
echo El servidor estara disponible en:
echo   - http://%IP%:8000/
echo   - http://localhost:8000/
echo.
echo IMPORTANTE: Asegurate de que el firewall de Windows
echo permita conexiones entrantes en el puerto 8000
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

REM Activar venv y ejecutar servidor en 0.0.0.0 (todas las interfaces)
call venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000

echo.
echo El servidor se ha detenido.
pause

