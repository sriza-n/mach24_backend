@echo off
echo Starting Flask Server...

:: Change to the script's directory
cd /D "%~dp0"

:: Check if virtual environment exists (assuming it's in 'venv' folder)
if exist ".venv\Scripts\activate" (
    call .venv\Scripts\activate
) else (
    echo Virtual environment not found, using system Python...
)

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Run the Flask application
echo Starting server...
python app.py

:: If there was an error, pause to show the message
if errorlevel 1 (
    echo Server failed to start
    pause
    exit /b 1
)