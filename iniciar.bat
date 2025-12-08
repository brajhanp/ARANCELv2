@echo off
REM Script principal de inicio - Muestra menú de opciones
setlocal enabledelayedexpansion
cd /d "%~dp0"

:MENU
cls
echo.
echo ========================================
echo   ARANCELv2 - Menu de Inicio
echo ========================================
echo.
echo Selecciona una opcion:
echo.
echo   1. Iniciar con ngrok (Internet - cualquier red)
echo   2. Iniciar en red local (misma WiFi)
echo   3. Iniciar solo local (tu computadora)
echo   4. Configurar firewall (solo una vez)
echo   5. Ver mi IP local
echo   6. Salir
echo.
set /p opcion="Ingresa el numero de opcion: "

if "%opcion%"=="1" goto NGROK
if "%opcion%"=="2" goto RED
if "%opcion%"=="3" goto LOCAL
if "%opcion%"=="4" goto FIREWALL
if "%opcion%"=="5" goto IP
if "%opcion%"=="6" goto SALIR

echo.
echo Opcion invalida. Presiona cualquier tecla para continuar...
pause >nul
goto MENU

:NGROK
cls
echo.
echo Iniciando con ngrok...
echo.
call iniciar_con_ngrok.bat
goto MENU

:RED
cls
echo.
echo Iniciando en modo red local...
echo.
call run_red.bat
goto MENU

:LOCAL
cls
echo.
echo Iniciando solo local...
echo.
call run.bat
goto MENU

:FIREWALL
cls
echo.
echo Configurando firewall...
echo.
call configurar_firewall.bat
echo.
echo Presiona cualquier tecla para volver al menu...
pause >nul
goto MENU

:IP
cls
echo.
call obtener_ip.bat
echo.
echo Presiona cualquier tecla para volver al menu...
pause >nul
goto MENU

:SALIR
echo.
echo Hasta luego!
timeout /t 1 >nul
exit

