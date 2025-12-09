@echo off
REM Setup script voor eerste installatie op Windows PC
REM Dit script installeert alle dependencies en maakt de applicatie klaar voor gebruik

echo ========================================
echo Pizzeria Management System - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is niet geinstalleerd!
    echo.
    echo Installeer Python 3.11 of hoger van:
    echo https://www.python.org/downloads/
    echo.
    echo BELANGRIJK: Vink "Add Python to PATH" aan tijdens installatie!
    echo.
    pause
    exit /b 1
)

echo [1/5] Python gevonden...
python --version
echo.

echo [2/5] Upgrade pip...
python -m pip install --upgrade pip
echo.

echo [3/5] Installeer dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Dependencies installatie gefaald
    pause
    exit /b 1
)
echo.

echo [4/5] Installeer Windows printer support...
pip install pywin32
if errorlevel 1 (
    echo WAARSCHUWING: pywin32 installatie gefaald (optioneel)
    echo Printer functionaliteit werkt mogelijk niet
)
echo.

echo [5/5] Maak benodigde mappen...
if not exist "logs" mkdir logs
if not exist "data\backup" mkdir data\backup
echo.

echo ========================================
echo Setup voltooid!
echo ========================================
echo.
echo Je kunt nu de applicatie starten met:
echo   python main.py
echo.
echo Of maak een exe met:
echo   cd scripts\build
echo   build_windows.bat
echo.
pause

