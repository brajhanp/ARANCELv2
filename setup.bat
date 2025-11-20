@echo off
REM Setup script for ARANCELv2 Django project on Windows
REM This script creates a virtual environment, installs dependencies, and runs migrations

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ========================================
echo   ARANCELv2 Project Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)
echo.

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)
echo Virtual environment activated.
echo.

echo [3/5] Installing dependencies...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

echo [4/5] Running migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to run migrations.
    echo This might be expected if the database already exists.
    pause
    exit /b 1
)
echo Migrations completed.
echo.

echo [5/5] Setup complete!
echo.
echo ========================================
echo   To run the development server:
echo   1. Open PowerShell or Command Prompt
echo   2. Navigate to: %cd%
echo   3. Run: venv\Scripts\activate.bat
echo   4. Run: python manage.py runserver
echo   5. Open: http://127.0.0.1:8000/
echo ========================================
echo.
pause
