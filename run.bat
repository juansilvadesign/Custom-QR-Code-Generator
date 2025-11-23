@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo              Custom QR Code Generator
echo ========================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Define virtual environment folder
set "VENV_DIR=.venv"

REM Check if .env exists (legacy support)
if exist ".env" (
    set "VENV_DIR=.env"
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

REM Install requirements
if exist "requirements.txt" (
    echo Checking and installing requirements...
    "!VENV_DIR!\Scripts\python.exe" -m pip install -r requirements.txt
)

REM Run the application
echo.
echo Starting Custom QR Code Generator...
echo.
"!VENV_DIR!\Scripts\python.exe" main.py

pause