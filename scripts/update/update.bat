@echo off
echo ========================================
echo Pizzeria Management System - Update Script
echo ========================================
echo.
echo WAARSCHUWING: Dit script beschermt lokale gegevens NIET automatisch.
echo Gebruik update_safe.bat voor veilige updates met data bescherming.
echo.
set /p continue="Doorgaan? (j/n): "
if /i not "%continue%"=="j" (
    echo Geannuleerd.
    exit /b 0
)
echo.

cd /d "%~dp0\..\.."

echo [1/3] Stashen van lokale wijzigingen...
git stash push -m "Auto-stash before update %date% %time%"

echo [2/3] Pulling latest changes from GitHub...
git pull origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Git pull failed!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo [2/3] Updating Python dependencies...
pip install -r requirements.txt --quiet

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Some dependencies might not have updated correctly.
)

echo.
echo [3/3] Update complete!
echo.
echo Choose an option:
echo   1. Start application in Python mode (recommended)
echo   2. Build new .exe file (takes 2-5 minutes)
echo   3. Exit
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Starting application...
    python main.py
) else if "%choice%"=="2" (
    echo.
    echo Building executable...
    echo This may take 2-5 minutes. Please wait...
    pyinstaller pizzeria.spec --clean --noconfirm
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ========================================
        echo Build completed successfully!
        echo ========================================
        echo.
        echo The executable can be found at: dist\PizzeriaBestelformulier.exe
    ) else (
        echo.
        echo ========================================
        echo Build failed!
        echo ========================================
    )
    pause
) else (
    echo.
    echo Exiting...
    exit /b 0
)


