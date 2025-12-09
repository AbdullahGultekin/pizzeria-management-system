# Testing Guide - Pizzeria Management System

## Overzicht

Deze guide helpt je om het programma grondig te testen op zowel macOS als Windows om platform-specifieke bugs te vinden.

## Snelle Start

### macOS
```bash
./test_macos.sh
```

### Windows
```cmd
test_windows.bat
```

Of handmatig:
```bash
python3 test_suite.py  # macOS
python test_suite.py    # Windows
```

## Test Suite

De `test_suite.py` script test automatisch:

1. **Platform Detection** - Detecteert het besturingssysteem
2. **Module Imports** - Controleert of alle modules beschikbaar zijn
3. **File Structure** - Controleert of alle benodigde bestanden aanwezig zijn
4. **JSON Validation** - Valideert menu.json, extras.json, settings.json
5. **Database** - Test database connectie en schema
6. **Printer Support** - Test printer functionaliteit (Windows)
7. **Sound Support** - Test geluid notificaties
8. **Path Handling** - Test bestandspaden (Windows vs Unix)
9. **Clipboard Monitor** - Test clipboard functionaliteit
10. **Encoding** - Test encoding (UTF-8, CP858)
11. **Tkinter UI** - Test of UI kan worden geïnitialiseerd

## Handmatige Tests

Na de automatische tests, voer handmatige tests uit volgens `TEST_CHECKLIST.md`.

### Belangrijkste Test Gebieden

#### 1. Koeriers Toewijzing (Performance)
- **Test**: Selecteer 10 bestellingen, wijs toe aan koerier
- **Verwacht**: < 1 seconde, geen UI freeze
- **Platform verschillen**: Geen verwacht

#### 2. Tab Switching (Performance)
- **Test**: Wissel tussen tabs (vooral zware tabs zoals Geschiedenis, Koeriers)
- **Verwacht**: < 0.5 seconden eerste keer, < 0.1 seconden daarna
- **Platform verschillen**: Geen verwacht

#### 3. Print Functionaliteit
- **Test**: Maak bestelling, print bon
- **Windows**: Fysieke printer moet werken
- **macOS**: Print preview moet werken
- **Platform verschillen**: Windows heeft fysieke printer, macOS alleen preview

#### 4. Geluid Notificaties
- **Test**: Plaats online bestelling, wacht op notificatie
- **Windows**: winsound.Beep() moet werken
- **macOS**: afplay moet werken
- **Platform verschillen**: Verschillende libraries

#### 5. Afhaal Bestellingen Filtering
- **Test**: Maak afhaal bestelling, check Koeriers tab
- **Verwacht**: Afhaal bestelling NIET zichtbaar in Koeriers tab
- **Test**: Check Afhaal tab
- **Verwacht**: Alleen afhaal bestellingen zichtbaar
- **Platform verschillen**: Geen verwacht

## Bekende Platform Verschillen

### 1. Printer Support
- **Windows**: `win32print` voor fysieke printers
- **macOS**: Alleen print preview (geen fysieke printer support)

### 2. Geluid Notificaties
- **Windows**: `winsound.Beep()`
- **macOS**: `afplay` of `os.system()`

### 3. Clipboard Monitor
- **Windows**: `win32clipboard` (optioneel, sneller)
- **macOS**: Tkinter clipboard (altijd beschikbaar)

### 4. Path Separators
- **Windows**: `\` (backslash)
- **macOS**: `/` (forward slash)
- **Oplossing**: Gebruik `pathlib.Path` voor cross-platform compatibiliteit

### 5. Encoding
- **Windows**: CP858 voor printer, UTF-8 voor bestanden
- **macOS**: UTF-8 overal

## Test Rapportage

Na het testen:

1. **Run test suite op beide platforms**:
   ```bash
   # macOS
   python3 test_suite.py
   
   # Windows
   python test_suite.py
   ```

2. **Vergelijk test reports**:
   - Check `test_report_Windows_*.txt`
   - Check `test_report_Darwin_*.txt` (macOS)
   - Vergelijk verschillen

3. **Documenteer bugs**:
   - Noteer welke tests falen op welk platform
   - Beschrijf het probleem
   - Noteer stappen om te reproduceren

4. **Fix bugs**:
   - Fix platform-specifieke bugs
   - Test opnieuw
   - Update test suite indien nodig

## Tips voor Effectief Testen

### 1. Test op Schone Installatie
- Verwijder `pizzeria.db` voor een schone start
- Test met minimale data eerst
- Voeg dan meer data toe voor performance tests

### 2. Test Edge Cases
- Lege velden
- Zeer lange strings
- Speciale tekens (€, é, ñ, ü)
- Negatieve getallen
- Zeer grote aantallen

### 3. Test Error Scenarios
- Verwijder bestanden tijdens runtime
- Sluit database tijdens operatie
- Test met ongeldige input
- Test met ontbrekende dependencies

### 4. Performance Testing
- Test met veel data (100+ bestellingen)
- Test met veel klanten (100+ klanten)
- Monitor geheugengebruik
- Check voor memory leaks

### 5. UI Testing
- Test op verschillende schermresoluties
- Test met verschillende font sizes
- Test keyboard shortcuts
- Test mouse interactions

## Automatische Test Integratie

Voor continue testing, overweeg:

1. **GitHub Actions** (voor CI/CD):
   - Test op Windows en macOS
   - Run automatisch bij commits
   - Genereer test reports

2. **Local Testing Script**:
   - Run `test_suite.py` regelmatig
   - Vergelijk reports tussen platforms
   - Documenteer verschillen

## Troubleshooting

### Test Suite Fails
- Check Python versie (3.8+)
- Check of alle dependencies geïnstalleerd zijn
- Check of bestanden aanwezig zijn
- Check log bestanden

### Platform-Specifieke Fails
- Check of platform-specifieke libraries geïnstalleerd zijn
  - Windows: `pywin32` voor win32print
  - macOS: `afplay` is standaard beschikbaar
- Check encoding issues
- Check path separator issues

### Performance Issues
- Check database queries (gebruik EXPLAIN QUERY PLAN)
- Check voor N+1 query problemen
- Check voor memory leaks
- Profile de applicatie

## Contact

Als je bugs vindt die niet in deze guide staan:
1. Documenteer het probleem
2. Noteer het platform
3. Voeg toe aan test suite
4. Fix het probleem

