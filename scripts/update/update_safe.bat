@echo off
setlocal enabledelayedexpansion
echo ========================================
echo Veilige Update - Pizzeria Management System
echo (Beschermt lokale gegevens)
echo ========================================
echo.

cd /d "%~dp0\..\.."

REM Lijst van lokale bestanden die beschermd moeten worden
set "LOCAL_DATA=pizzeria.db settings.json app.log app_errors.log pizzeria_backup.db"

REM Maak backup folder
if not exist "data\backup\update_backup" mkdir "data\backup\update_backup"

echo [1/4] Backuppen van lokale gegevens...
set BACKUP_COUNT=0
for %%f in (%LOCAL_DATA%) do (
    if exist "%%f" (
        echo   - Backuppen: %%f
        copy /Y "%%f" "data\backup\update_backup\%%f" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set /a BACKUP_COUNT+=1
        )
    )
)
echo   !BACKUP_COUNT! bestand(en) gebackupt
echo.

echo [2/4] Stashen van lokale wijzigingen (code bestanden)...
git stash push -m "Auto-stash before update %date% %time%"

if %ERRORLEVEL% NEQ 0 (
    echo   Geen lokale wijzigingen om te stashen
) else (
    echo   Lokale wijzigingen gestasht
)
echo.

echo [3/4] Ophalen van laatste wijzigingen van GitHub...
git pull origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Git pull gefaald!
    echo.
    echo Herstellen van lokale gegevens...
    for %%f in (%LOCAL_DATA%) do (
        if exist "data\backup\update_backup\%%f" (
            copy /Y "data\backup\update_backup\%%f" "%%f" >nul 2>&1
        )
    )
    echo.
    echo Lokale gegevens hersteld. Controleer je internet verbinding en probeer opnieuw.
    pause
    exit /b 1
)

echo   Update succesvol!
echo.

echo [4/4] Controleren of lokale gegevens intact zijn...
set RESTORE_COUNT=0
for %%f in (%LOCAL_DATA%) do (
    if exist "data\backup\update_backup\%%f" (
        REM Check of bestand overschreven is (door git pull)
        git check-ignore "%%f" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            REM Bestand staat in .gitignore, zou niet overschreven moeten zijn
            REM Maar controleer of het nog bestaat
            if not exist "%%f" (
                echo   - Herstellen: %%f (was verwijderd)
                copy /Y "data\backup\update_backup\%%f" "%%f" >nul 2>&1
                set /a RESTORE_COUNT+=1
            ) else (
                echo   - OK: %%f (intact)
            )
        )
    )
)

if !RESTORE_COUNT! GTR 0 (
    echo   !RESTORE_COUNT! bestand(en) hersteld
) else (
    echo   Alle lokale gegevens zijn intact
)
echo.

echo ========================================
echo Update voltooid!
echo ========================================
echo.
echo Lokale gegevens zijn beschermd:
echo   - Database (pizzeria.db)
echo   - Instellingen (settings.json)
echo   - Log bestanden
echo.
echo Backup locatie: data\backup\update_backup\
echo.

REM Optioneel: dependencies updaten
set /p update_deps="Dependencies updaten? (j/n): "
if /i "%update_deps%"=="j" (
    echo.
    echo Dependencies updaten...
    pip install -r requirements.txt --quiet
    echo   Klaar!
)

echo.
set /p start_app="Applicatie starten? (j/n): "
if /i "%start_app%"=="j" (
    echo.
    echo Applicatie starten...
    python main.py
)

echo.
echo Klaar!
pause

