@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo              Custom QR Code Generator
echo ========================================================

REM Define virtual environment folder
set "VENV_DIR=.venv"

REM Check if .env exists (legacy support)
if exist ".env" (
    set "VENV_DIR=.env"
)

REM Check if local Python exists
if exist "!VENV_DIR!\Scripts\python.exe" (
    echo Found local Python environment in !VENV_DIR!
    set "PYTHON_EXE=!VENV_DIR!\Scripts\python.exe"
    goto :SKIP_SETUP
)

REM Check if Global Python is installed (only if local not found)
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed globally and no local environment found.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "!VENV_DIR!" (
    echo Creating virtual environment in !VENV_DIR!...
    python -m venv "!VENV_DIR!"
    if !errorlevel! neq 0 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created.
)
set "PYTHON_EXE=!VENV_DIR!\Scripts\python.exe"

:SKIP_SETUP
REM Install requirements
if exist "requirements.txt" (
    echo Checking and installing requirements...
    "!PYTHON_EXE!" -m pip install -r requirements.txt >nul 2>&1
)

REM Run the application
echo.
echo Starting Custom QR Code Generator...
echo.
"!PYTHON_EXE!" main.py

pause