# Windows Executable Build Instructions

Dit document beschrijft hoe je de Pizzeria Bestelformulier applicatie compileert naar een Windows .exe bestand.

## Vereisten

1. **Python 3.8 of hoger** geïnstalleerd op Windows
2. **pip** (Python package manager)
3. **Alle projectbestanden** (menu.json, extras.json, etc.)

## Stap 1: Installeer Dependencies

Open een Command Prompt of PowerShell in de project directory en voer uit:

```bash
# Installeer alle dependencies
pip install -r requirements.txt

# Installeer PyInstaller
pip install pyinstaller
```

## Stap 2: Controleer Bestanden

Zorg ervoor dat de volgende bestanden aanwezig zijn in de project root:
- `main.py` (entry point)
- `menu.json`
- `extras.json`
- `settings.json` (optioneel, wordt aangemaakt als niet aanwezig)
- `straatnamen.json` (optioneel)
- `straatnamen.csv` (optioneel)
- `logo.ico` (optioneel, voor applicatie icoon)

## Stap 3: Build de Executable

Voer het volgende commando uit:

```bash
pyinstaller pizzeria.spec
```

Of gebruik de directe PyInstaller commando's:

```bash
pyinstaller --name="PizzeriaBestelformulier" ^
    --onefile ^
    --windowed ^
    --icon=logo.ico ^
    --add-data="menu.json;." ^
    --add-data="extras.json;." ^
    --add-data="settings.json;." ^
    --add-data="straatnamen.json;." ^
    --add-data="straatnamen.csv;." ^
    --hidden-import=PIL._imaging ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=qrcode ^
    --hidden-import=win32print ^
    --exclude-module=matplotlib ^
    --exclude-module=numpy ^
    --exclude-module=pandas ^
    main.py
```

## Stap 4: Locatie van Executable

Na het builden vind je de executable in:
```
dist/PizzeriaBestelformulier.exe
```

## Stap 5: Testen

1. Kopieer `PizzeriaBestelformulier.exe` naar een test directory
2. Zorg dat de database bestand (`pizzeria.db`) in dezelfde directory staat (of laat de applicatie deze aanmaken)
3. Dubbelklik op de .exe om te testen

## Troubleshooting

### Probleem: "ModuleNotFoundError"
**Oplossing**: Voeg de ontbrekende module toe aan `hiddenimports` in `pizzeria.spec`

### Probleem: "FileNotFoundError" voor JSON bestanden
**Oplossing**: Controleer of alle data bestanden correct zijn toegevoegd in de `datas` lijst in `pizzeria.spec`

### Probleem: Console venster verschijnt
**Oplossing**: Zet `console=False` in de `exe` sectie van `pizzeria.spec`

### Probleem: Executable is te groot
**Oplossing**: 
- Gebruik `--onefile` in plaats van `--onedir` (al gedaan)
- Voeg meer modules toe aan `excludes` lijst
- Gebruik UPX compression (al geactiveerd met `upx=True`)

### Probleem: QR code functionaliteit werkt niet
**Oplossing**: Zorg dat `Pillow` en `qrcode` correct zijn geïnstalleerd:
```bash
pip install Pillow qrcode[pil]
```

### Probleem: Printer functionaliteit werkt niet op Windows
**Oplossing**: Installeer `pywin32`:
```bash
pip install pywin32
```

## Distributie

Voor distributie naar andere Windows computers:
1. Kopieer `PizzeriaBestelformulier.exe`
2. De eerste keer dat de applicatie draait, worden de benodigde bestanden aangemaakt
3. Optioneel: Kopieer ook `pizzeria.db` als je een bestaande database wilt meenemen

## Opmerkingen

- De eerste keer opstarten kan wat langer duren (ongeveer 5-10 seconden)
- De applicatie maakt automatisch een database aan als deze niet bestaat
- Instellingen worden opgeslagen in `settings.json` in dezelfde directory als de .exe

