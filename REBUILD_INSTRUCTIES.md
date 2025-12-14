# EXE Rebuild Instructies

## Belangrijk: Rebuild Vereist!

Na alle fixes (Tcl/Tk, Logging, Update Checker) **MOET** je de EXE opnieuw bouwen om de wijzigingen toe te passen.

## Stap 1: Rebuild de EXE

### Optie A: Via Build Script (Aanbevolen)

1. Open PowerShell in de project directory
2. Run:
   ```powershell
   .\build_exe.bat
   ```
   
   OF dubbelklik op `build_exe.bat` in Verkenner

### Optie B: Handmatig

```powershell
pyinstaller pizzeria.spec --clean --noconfirm
```

## Stap 2: Wacht tot Build Klaar is

- Build tijd: 2-5 minuten
- Je ziet progress in de terminal
- Wacht tot "Build completed successfully!"

## Stap 3: Test de Nieuwe EXE

1. Ga naar `dist\PizzeriaBestelformulier.exe`
2. Start de EXE
3. Controleer:
   - ✅ Geen Tcl/Tk fout
   - ✅ Geen permission error
   - ✅ Applicatie start correct
   - ✅ Update check werkt (na 3 seconden)

## Wat is Aangepast in deze Build?

### 1. Tcl/Tk Fix
- Tcl/Tk bestanden worden automatisch meegenomen
- Geen "Can't find init.tcl" fout meer

### 2. Logging Fix
- Logs worden geschreven naar `[EXE_DIR]/logs/app.log`
- Geen permission errors meer
- Fallback naar temp directory als backup

### 3. Update Checker
- `requests` library toegevoegd
- Automatische download functionaliteit
- Betere error handling

## Troubleshooting

### "Build failed"
- Controleer of PyInstaller geïnstalleerd is: `pip install pyinstaller`
- Controleer of alle dependencies geïnstalleerd zijn: `pip install -r requirements.txt`

### "EXE werkt nog steeds niet"
- Zorg dat je `--clean` gebruikt (verwijdert oude build)
- Controleer of de nieuwe EXE in `dist\` staat
- Test met de nieuwe EXE, niet de oude

### "Permission error blijft"
- Zorg dat je de EXE niet vanuit System32 start
- Start de EXE vanuit de `dist\` directory
- Of maak een shortcut naar de EXE

## Na Rebuild

De nieuwe EXE zou moeten werken zonder:
- ❌ Tcl/Tk errors
- ❌ Permission errors  
- ❌ Update check problemen

✅ Alles zou nu moeten werken!
