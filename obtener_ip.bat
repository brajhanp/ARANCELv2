@echo off
REM Script para obtener la IP local del equipo
echo.
echo ========================================
echo   Obtener IP Local
echo ========================================
echo.

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    set IP=!IP:~1!
    echo Tu IP local es: %IP%
    echo.
    echo Accede desde otros dispositivos usando:
    echo   http://%IP%:8000/
    echo.
    goto :end
)

echo No se pudo obtener la IP local.
echo Verifica que tengas conexion de red activa.

:end
echo.
pause

