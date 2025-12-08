# ARANCELv2 Setup Script for PowerShell
# Este script configura todo automáticamente en Windows

param(
    [switch]$Reset = $false
)

Clear-Host

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ARANCELv2 Project Setup (PowerShell)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Python no está instalado o no está en PATH" -ForegroundColor Red
    Write-Host "Descárgalo desde: https://www.python.org/" -ForegroundColor Red
    Write-Host "IMPORTANTE: Marca 'Add Python to PATH' durante la instalación" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host ""

# Crear entorno virtual
Write-Host "[2/5] Configurando entorno virtual..." -ForegroundColor Yellow
if ((Test-Path "venv") -and -not $Reset) {
    Write-Host "✓ Entorno virtual ya existe" -ForegroundColor Green
} else {
    Write-Host "   Creando nuevo entorno virtual..." -ForegroundColor Cyan
    if ($Reset -and (Test-Path "venv")) {
        Remove-Item -Recurse -Force "venv" -ErrorAction SilentlyContinue
    }
    try {
        python -m venv venv
        Write-Host "✓ Entorno virtual creado" -ForegroundColor Green
    } catch {
        Write-Host "✗ ERROR: No se pudo crear el entorno virtual" -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
}
Write-Host ""

# Activar entorno virtual
Write-Host "[3/5] Activando entorno virtual..." -ForegroundColor Yellow
try {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✓ Entorno virtual activado" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: No se pudo activar el entorno virtual" -ForegroundColor Red
    Write-Host "   Intenta ejecutar como administrador o verifica los permisos" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host ""

# Instalar dependencias
Write-Host "[4/5] Instalando dependencias..." -ForegroundColor Yellow
try {
    Write-Host "   Actualizando pip..." -ForegroundColor Cyan
    python -m pip install --upgrade pip -q
    Write-Host "   Instalando paquetes from requirements.txt..." -ForegroundColor Cyan
    pip install -r requirements.txt
    Write-Host "✓ Dependencias instaladas" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: No se pudieron instalar las dependencias" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host ""

# Ejecutar migraciones
Write-Host "[5/5] Ejecutando migraciones de base de datos..." -ForegroundColor Yellow
try {
    python manage.py migrate
    Write-Host "✓ Migraciones completadas" -ForegroundColor Green
} catch {
    Write-Host "⚠ Advertencia: Hubo un problema con las migraciones" -ForegroundColor Yellow
    Write-Host "   Esto podría ser normal si la base de datos ya existe" -ForegroundColor Yellow
}
Write-Host ""

# Resumen final
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ✓ Setup completado exitosamente" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Para ejecutar el servidor:" -ForegroundColor Cyan
Write-Host "  1. Abre PowerShell en esta carpeta" -ForegroundColor White
Write-Host "  2. Ejecuta: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  3. Ejecuta: python manage.py runserver" -ForegroundColor White
Write-Host "  4. Abre: http://127.0.0.1:8000/" -ForegroundColor White
Write-Host ""

Write-Host "Para crear un usuario administrador:" -ForegroundColor Cyan
Write-Host "  python manage.py createsuperuser" -ForegroundColor White
Write-Host ""

Write-Host "Para ver el panel admin:" -ForegroundColor Cyan
Write-Host "  http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""

# Opcionalmente iniciar el servidor
$startServer = Read-Host "¿Deseas iniciar el servidor ahora? (S/N)"
if ($startServer -eq "S" -or $startServer -eq "s" -or $startServer -eq "Y" -or $startServer -eq "y") {
    Write-Host ""
    Write-Host "Iniciando servidor..." -ForegroundColor Green
    Write-Host "Presiona CTRL+C para detener el servidor" -ForegroundColor Yellow
    Write-Host ""
    python manage.py runserver
} else {
    Write-Host ""
    Write-Host "Listo. Para iniciar el servidor después, ejecuta:" -ForegroundColor Cyan
    Write-Host "  python manage.py runserver" -ForegroundColor White
    Write-Host ""
}
