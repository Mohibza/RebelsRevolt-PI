@echo off
title EyeConExcel Web App
color 0B

echo.
echo  ============================================
echo   EyeConExcel - Phone Intelligence WebApp
echo  ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  [ERROR] Python not found!
    echo  Download from: https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: Install dependencies
echo  [1/2] Installing dependencies...
python -m pip install -r "%~dp0requirements.txt" --quiet
if errorlevel 1 (
    color 0C
    echo  [ERROR] Failed to install requirements!
    echo  Try running as Administrator.
    echo.
    pause
    exit /b 1
)

echo  [2/2] Starting EyeConExcel...
echo.
echo  App will open in your browser at: http://localhost:5000
echo  Press Ctrl+C in this window to stop.
echo.

cd /d "%~dp0"
python run.py

if errorlevel 1 (
    color 0C
    echo.
    echo  [ERROR] App crashed. See error above.
    echo.
    pause
)
