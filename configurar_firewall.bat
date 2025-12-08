@echo off
REM Script para configurar el firewall de Windows automáticamente
REM Permite conexiones entrantes en el puerto 8000

echo.
echo ========================================
echo   Configurando Firewall de Windows
echo ========================================
echo.

REM Verificar si ya existe la regla
netsh advfirewall firewall show rule name="Django ARANCELv2" >nul 2>&1
if %errorlevel% == 0 (
    echo La regla del firewall ya existe.
    echo.
    choice /C SN /M "Deseas eliminarla y crearla de nuevo"
    if errorlevel 2 goto :end
    if errorlevel 1 (
        echo Eliminando regla existente...
        netsh advfirewall firewall delete rule name="Django ARANCELv2"
    )
)

echo.
echo Creando regla del firewall para permitir conexiones en el puerto 8000...
echo.

REM Crear regla de entrada para el puerto 8000
netsh advfirewall firewall add rule name="Django ARANCELv2" dir=in action=allow protocol=TCP localport=8000

if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo   Firewall configurado correctamente!
    echo ========================================
    echo.
    echo El puerto 8000 ahora esta abierto para conexiones entrantes.
    echo Puedes acceder desde otros dispositivos en tu red.
    echo.
) else (
    echo.
    echo ERROR: No se pudo configurar el firewall.
    echo Es posible que necesites ejecutar este script como Administrador.
    echo.
    echo Haz clic derecho en este archivo y selecciona
    echo "Ejecutar como administrador"
    echo.
)

:end
pause

