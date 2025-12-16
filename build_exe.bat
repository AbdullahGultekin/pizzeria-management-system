@echo off
echo ========================================
echo Building PizzeriaBestelformulier.exe
echo ========================================
echo.
echo This may take 2-5 minutes. Please wait...
echo.

cd /d "%~dp0"
pyinstaller pizzeria.spec --clean

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Build completed successfully!
    echo ========================================
    echo.
    echo The executable can be found at: dist\PizzeriaBestelformulier.exe
    echo.
) else (
    echo.
    echo ========================================
    echo Build failed!
    echo ========================================
    echo.
)

pause





















