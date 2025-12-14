# Logging Fix Update

## Probleem
De EXE gaf een `PermissionError` bij het schrijven naar `C:\WINDOWS\System32\app.log` omdat:
- De EXE werd gestart vanuit System32 (verkeerde working directory)
- De logging configuratie gebruikte relatieve paden
- System32 is een beschermde directory waar je niet mag schrijven

## Oplossing
De `logging_config.py` is verbeterd om:
1. **Altijd absolute paden te gebruiken** - gebaseerd op de EXE locatie, niet de working directory
2. **Fallback naar temp directory** - als de EXE directory niet beschikbaar is
3. **Betere error handling** - probeert meerdere locaties voordat het faalt

## Wat is aangepast

### `get_safe_log_directory()`
- Gebruikt altijd `sys.executable` (EXE locatie) als basis
- Retourneert altijd een absoluut pad
- Val terug op temp directory als EXE directory niet beschikbaar is

### `setup_logging()`
- Controleert of de log directory beschrijfbaar is
- Gebruikt altijd absolute paden
- Betere fallback logica voor error logs

## Volgende Stappen

### 1. Rebuild de EXE
```powershell
# Option 1: Gebruik build script
.\build_exe.bat

# Option 2: Handmatig
pyinstaller pizzeria.spec --clean --noconfirm
```

### 2. Test de EXE
- Start de EXE vanuit elke directory
- Controleer of er geen PermissionError meer is
- Logs zouden moeten verschijnen in: `[EXE_DIRECTORY]\logs\app.log`

### 3. Verifieer
- Start de EXE vanuit verschillende locaties
- Check of logs correct worden geschreven
- Geen errors meer in de console

## Belangrijk
- **De EXE moet opnieuw gebouwd worden** om deze fix te krijgen
- De oude EXE heeft nog steeds het probleem
- Na rebuild zou alles moeten werken
