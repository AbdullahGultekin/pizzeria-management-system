@echo off
echo ========================================
echo Building PizzeriaBestelformulier.exe
echo ========================================
echo.
echo This may take 3-5 minutes. Please wait...
echo Progress will be saved to build_output.log
echo.

cd /d "%~dp0"

REM Start build and redirect output to log file
pyinstaller pizzeria.spec --clean --noconfirm > build_output.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Build completed successfully!
    echo ========================================
    echo.
    echo The executable can be found at: dist\PizzeriaBestelformulier.exe
    echo.
    if exist "dist\PizzeriaBestelformulier.exe" (
        echo Copying to root directory...
        copy "dist\PizzeriaBestelformulier.exe" "PizzeriaBestelformulier.exe" /Y
        echo Done!
    )
) else (
    echo.
    echo ========================================
    echo Build failed! Check build_output.log for details
    echo ========================================
    echo.
)

pause














