# Logging Permission Fix

## Probleem
De EXE geeft fout: `PermissionError: [Errno 13] Permission denied: 'C:\\WINDOWS\\System32\\app.log'`

Dit gebeurt omdat:
- De EXE probeert te schrijven naar de "current working directory"
- Als de EXE vanuit System32 wordt gestart, heeft het geen schrijfrechten daar
- Relatieve paden zoals `"app.log"` worden geïnterpreteerd relatief aan de working directory

## Oplossing
De `logging_config.py` is aangepast om:
1. ✅ Automatisch de EXE directory te detecteren
2. ✅ Logs te schrijven naar `logs/` directory naast de EXE
3. ✅ Fallback mechanisme als schrijven faalt

## Wat is Aangepast

### logging_config.py
- ✅ `get_safe_log_directory()` functie toegevoegd
- ✅ Detecteert of applicatie vanuit EXE draait
- ✅ Gebruikt EXE directory voor logs (niet working directory)
- ✅ Maakt `logs/` directory automatisch aan
- ✅ Error handling toegevoegd voor permission errors

## Log Locaties

**Vanuit EXE:**
- Logs worden geschreven naar: `[EXE_DIRECTORY]/logs/app.log`
- Error logs: `[EXE_DIRECTORY]/logs/app_errors.log`

**Vanuit Python script:**
- Logs worden geschreven naar: `./logs/app.log`
- Error logs: `./logs/app_errors.log`

## Rebuild de EXE

Na deze fix, rebuild de EXE:

```powershell
pyinstaller pizzeria.spec --clean --noconfirm
```

## Verificatie

Na rebuild, test de EXE:
1. Start `dist\PizzeriaBestelformulier.exe` vanuit elke locatie
2. De applicatie zou moeten opstarten zonder permission errors
3. Logs worden geschreven naar `dist\logs\app.log`

## Belangrijk

- Logs worden altijd geschreven naar een locatie waar de applicatie rechten heeft
- Geen afhankelijkheid van working directory
- Werkt zelfs als EXE vanuit System32 wordt gestart
