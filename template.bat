@echo off
REM =============================================================================
REM Custom QR Code Generator - Batch File Template
REM =============================================================================
REM 
REM Instructions:
REM 1. Copy this file and rename it to "run.bat"
REM 2. Replace the placeholders below with your actual paths
REM 3. Make sure your Python environment is set up correctly
REM 
REM Placeholders to replace:
REM - [YOUR_PROJECT_PATH]: Full path to where you cloned/downloaded this project
REM - [YOUR_PYTHON_PATH]: Path to your Python executable (can be system Python or virtual environment)
REM
REM Examples:
REM - System Python: "C:\Python39\python.exe"
REM - Virtual Environment: "C:\path\to\your\project\.venv\Scripts\python.exe"
REM - Anaconda/Miniconda: "C:\Users\YourName\anaconda3\python.exe"
REM =============================================================================

echo Starting Custom-QR-Code-Generator...

REM Option 1: Using a virtual environment (recommended)
REM Replace [YOUR_PROJECT_PATH] with your actual project path
"[YOUR_PROJECT_PATH]\.env\Scripts\python.exe" main.py

REM Option 2: Using system Python (uncomment the line below and comment the line above)
REM python main.py

REM Option 3: Using specific Python path (uncomment and modify the line below)
REM "[YOUR_PYTHON_PATH]" main.py

echo.
echo Script execution completed.
pause