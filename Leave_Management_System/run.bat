@echo off
REM Quick Start Guide for Leave Management System on Windows

echo.
echo Leave Management System - Quick Start (Windows)
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.7 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Install dependencies
echo [*] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Run setup script
echo [*] Setting up demo data...
python setup.py
if errorlevel 1 (
    echo Error: Failed to setup demo data
    pause
    exit /b 1
)
echo [OK] Demo data created
echo.

REM Run application
echo [*] Starting the Leave Management System...
echo.
echo Open your browser and go to: http://localhost:5000
echo.
echo Demo Credentials:
echo   Admin: username=admin, password=admin123
echo   Employee: username=employee, password=emp123
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
