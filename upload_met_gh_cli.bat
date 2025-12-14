@echo off
echo ========================================
echo GitHub CLI Upload Script
echo ========================================
echo.

cd /d "%~dp0"

echo Checking GitHub CLI installation...
gh --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: GitHub CLI niet gevonden!
    echo.
    echo Volg deze stappen:
    echo 1. Download GitHub CLI van: https://cli.github.com/
    echo 2. Installeer het .msi bestand
    echo 3. Sluit deze PowerShell en open een nieuwe
    echo 4. Run: gh auth login
    echo 5. Run dit script opnieuw
    echo.
    echo Zie GITHUB_CLI_INSTALLATIE.md voor gedetailleerde instructies.
    echo.
    pause
    exit /b 1
)

echo GitHub CLI gevonden!
echo.

echo Checking authentication...
gh auth status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Je bent niet ingelogd!
    echo.
    echo Run eerst:
    echo   gh auth login
    echo.
    echo Volg de instructies om in te loggen met je browser.
    echo.
    pause
    exit /b 1
)

echo Authenticated!
echo.

echo Checking if ZIP file exists...
if not exist "dist\PizzeriaBestelformulier.zip" (
    echo.
    echo ERROR: dist\PizzeriaBestelformulier.zip niet gevonden!
    echo.
    echo Maak eerst de ZIP met:
    echo   python create_release_zip.py
    echo.
    pause
    exit /b 1
)

echo ZIP file gevonden!
echo.

echo ========================================
echo Uploaden naar GitHub Release v1.1.1
echo ========================================
echo.
echo Dit kan enkele minuten duren voor grote bestanden...
echo.

gh release upload v1.1.1 "dist\PizzeriaBestelformulier.zip" --repo AbdullahGultekin/pizzeria-management-system --clobber

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Upload SUCCESVOL!
    echo ========================================
    echo.
    echo De ZIP is geüpload naar GitHub Release v1.1.1!
    echo.
    echo Check de release hier:
    echo https://github.com/AbdullahGultekin/pizzeria-management-system/releases/tag/v1.1.1
    echo.
    echo Wacht 2-5 minuten voordat de API cache bijwerkt.
    echo Dan zou automatische download moeten werken!
) else (
    echo.
    echo ========================================
    echo Upload GEFAALD!
    echo ========================================
    echo.
    echo Mogelijke oorzaken:
    echo - Internet verbinding probleem
    echo - Release bestaat niet
    echo - Authenticatie probleem (run: gh auth login)
    echo.
    echo Probeer later opnieuw of check je internet verbinding.
)

echo.
pause
