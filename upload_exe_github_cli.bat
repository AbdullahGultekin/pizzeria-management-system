@echo off
echo ========================================
echo GitHub CLI Upload Script
echo ========================================
echo.

cd /d "%~dp0"

echo Checking GitHub CLI...
gh --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: GitHub CLI niet gevonden!
    echo.
    echo Download en installeer GitHub CLI van:
    echo https://cli.github.com/
    echo.
    pause
    exit /b 1
)

echo GitHub CLI gevonden!
echo.

echo Uploaden PizzeriaBestelformulier.zip naar release v1.1.1...
gh release upload v1.1.1 "dist\PizzeriaBestelformulier.zip" --repo AbdullahGultekin/pizzeria-management-system --clobber

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Upload succesvol!
    echo ========================================
    echo.
    echo De ZIP is geüpload naar GitHub!
    echo Wacht 2-5 minuten voordat de API cache bijwerkt.
) else (
    echo.
    echo ========================================
    echo Upload gefaald!
    echo ========================================
    echo.
    echo Mogelijke oorzaken:
    echo - Je bent niet ingelogd (run: gh auth login)
    echo - Internet verbinding probleem
    echo - Bestand bestaat niet
)

echo.
pause
