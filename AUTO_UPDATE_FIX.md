# Automatische Update Fix

## Probleem
De EXE doet geen automatische update check bij opstarten.

## Gevonden Problemen

### 1. ✅ **OPGELOST: `requests` library niet in EXE build**
   - **Probleem**: De `requests` library was niet toegevoegd aan `hiddenimports` in `pizzeria.spec`
   - **Gevolg**: PyInstaller includeerde de library niet in de EXE, waardoor update checks faalden
   - **Oplossing**: Toegevoegd aan `pizzeria.spec`:
     - `requests`
     - `urllib3` (vereist door requests)
     - `certifi` (SSL certificaten)
     - `charset_normalizer` (character encoding)
     - `idna` (internationalized domain names)

### 2. ✅ **OPGELOST: Error logging verbeterd**
   - **Probleem**: Fouten werden alleen als `debug` gelogd, waardoor ze niet zichtbaar waren
   - **Oplossing**: Error logging verbeterd in `utils/updater.py` om ImportError specifiek te vangen en te loggen

### 3. ⚠️ **Te controleren: Versienummer**
   - Huidige versie in code: `1.1.0` (regel 78 in app.py)
   - **Belangrijk**: Zorg dat GitHub releases dezelfde versie tag gebruiken (bijv. `v1.1.0` of `1.1.0`)

## Wat te doen

### 1. Rebuild de EXE
   ```bash
   pyinstaller pizzeria.spec --clean --noconfirm
   ```

   Of gebruik de GitHub Actions workflow (die wordt automatisch getriggerd bij een release).

### 2. Test de update check
   - Start de nieuwe EXE
   - Controleer de logs in `logs/` directory voor update check berichten
   - Als er een nieuwe release op GitHub is met een hoger versienummer, zou er een update dialog moeten verschijnen

### 3. Verifieer GitHub Release
   - Zorg dat er een release bestaat op GitHub met een versie tag (bijv. `v1.2.0`)
   - De release moet een `.exe` asset bevatten
   - De tag moet een hoger versienummer hebben dan `1.1.0`

## Debugging Tips

Als de update check nog steeds niet werkt:

1. **Controleer logs**: Kijk in `logs/pizzeria.log` voor error berichten
2. **Test handmatig**: Gebruik "Help > Check for Updates" in het menu
3. **Controleer internet verbinding**: De EXE moet toegang hebben tot `api.github.com`
4. **Test met Python script**: 
   ```python
   from utils.updater import UpdateChecker
   checker = UpdateChecker("1.1.0")
   has_update = checker.check_for_updates()
   print(f"Update available: {has_update}")
   ```

## Belangrijke Bestanden Aangepast

- ✅ `pizzeria.spec` - `requests` en dependencies toegevoegd aan hiddenimports
- ✅ `utils/updater.py` - Betere error handling voor ImportError

## Volgende Stappen

1. Commit deze wijzigingen
2. Push naar GitHub
3. Maak een nieuwe release (dit triggert automatisch de build)
4. Test de nieuwe EXE
