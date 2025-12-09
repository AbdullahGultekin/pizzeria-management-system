# Test Checklist - Pizzeria Management System

## Platform-Specific Testing Guide

Deze checklist helpt je om het programma grondig te testen op zowel macOS als Windows.

## Voorbereiding

### Op macOS:
```bash
python3 test_suite.py
```

### Op Windows:
```cmd
python test_suite.py
```

## Functionele Tests

### 1. Applicatie Start
- [ ] Applicatie start zonder errors
- [ ] Modus selector verschijnt (Kassa/Admin)
- [ ] Geen console errors bij opstarten
- [ ] Database wordt correct geïnitialiseerd

### 2. Kassa Modus (Front)

#### Bestellingen Maken
- [ ] Product toevoegen werkt
- [ ] Product opties dialog opent correct
- [ ] Half-half pizza selectie werkt
- [ ] Extras toevoegen werkt
- [ ] Bijgerechten toevoegen werkt
- [ ] Sauzen selecteren werkt
- [ ] Aantal wijzigen werkt
- [ ] Product verwijderen werkt

#### Klantgegevens
- [ ] Telefoonnummer invoeren werkt
- [ ] Telefoonnummer validatie (alle EU landen)
- [ ] Autocomplete voor straatnamen werkt
- [ ] Postcode/Gemeente selectie werkt
- [ ] Klantgegevens worden opgeslagen
- [ ] Bestaande klant wordt gevonden

#### Bestelling Opslaan
- [ ] Bestelling opslaan werkt
- [ ] Bonnummer wordt gegenereerd
- [ ] Database update werkt
- [ ] Bestelling verschijnt in geschiedenis

#### Print Functionaliteit
- [ ] Print preview opent
- [ ] Bon tekst is correct geformatteerd
- [ ] **Windows**: Printer werkt (win32print)
- [ ] **macOS**: Print preview werkt (geen fysieke printer)
- [ ] QR code wordt gegenereerd (als qrcode geïnstalleerd)

### 3. Admin Modus (Back)

#### Geschiedenis
- [ ] Bestellingen worden getoond
- [ ] Filteren op datum werkt
- [ ] Zoeken werkt
- [ ] Bestelling details bekijken werkt
- [ ] Bestelling verwijderen werkt
- [ ] Bestelling opnieuw openen werkt

#### Klantenbeheer
- [ ] Klantenlijst wordt getoond
- [ ] Klant zoeken werkt
- [ ] Klant bewerken werkt
- [ ] Klant verwijderen werkt
- [ ] Klant statistieken worden getoond

#### Menu Management
- [ ] Menu items worden getoond
- [ ] Product toevoegen werkt
- [ ] Product bewerken werkt
- [ ] Product verwijderen werkt
- [ ] Categorie volgorde wijzigen werkt

#### Extras Management
- [ ] Extras worden getoond
- [ ] Extra toevoegen werkt
- [ ] Extra bewerken werkt
- [ ] Extra verwijderen werkt

#### Koeriers
- [ ] Koerierslijst wordt getoond
- [ ] Koerier toevoegen werkt
- [ ] Koerier verwijderen werkt
- [ ] Bestellingen toewijzen werkt (SNEL TESTEN!)
- [ ] Koerier totalen worden berekend
- [ ] **Windows**: Totalen afdrukken werkt
- [ ] Afhaal bestellingen zijn NIET zichtbaar

#### Afhaal Bestellingen
- [ ] Afhaal tab opent
- [ ] Alleen afhaal bestellingen worden getoond
- [ ] Status wijzigen (Nieuw/Afgehaald) werkt
- [ ] Bezorg bestellingen zijn NIET zichtbaar

#### Online Bestellingen
- [ ] Online bestellingen tab opent
- [ ] Polling werkt (elke 5-10 seconden)
- [ ] Nieuwe bestellingen worden getoond
- [ ] Geluid notificatie werkt
  - [ ] **Windows**: winsound.Beep werkt
  - [ ] **macOS**: afplay werkt
- [ ] Levertijd selecteren werkt
- [ ] Bestelling accepteren werkt
- [ ] Status wijzigen werkt
- [ ] Koerier toewijzen werkt
- [ ] Route bekijken (Google Maps) werkt
- [ ] Bon opnieuw afdrukken werkt

#### Rapportage
- [ ] Z-rapport genereren werkt
- [ ] Datum selectie werkt
- [ ] Rapport wordt correct getoond

### 4. Keyboard Shortcuts
- [ ] Ctrl/Cmd+P: Print preview (alleen als niet in text field)
- [ ] Ctrl/Cmd+H: Geschiedenis (alleen als niet in text field)
- [ ] Ctrl/Cmd+N: Nieuwe bestelling (alleen als niet in text field)
- [ ] Ctrl/Cmd+S: Opslaan (alleen als niet in text field)
- [ ] Escape: Annuleren
- [ ] Delete: Verwijderen (alleen als niet in text field)
- [ ] Backspace: Verwijderen (alleen als niet in text field)

### 5. Database Operaties
- [ ] Database wordt aangemaakt als niet bestaat
- [ ] Migraties werken (afhaal kolom, etc.)
- [ ] Foreign keys werken correct
- [ ] Transacties werken (rollback bij errors)
- [ ] Database pad resolutie werkt op beide platforms

### 6. Bestandspaden
- [ ] JSON bestanden worden correct geladen
- [ ] Relatieve paden werken
- [ ] Absolute paden werken
- [ ] Path separators worden correct afgehandeld
  - [ ] **Windows**: `\` separators
  - [ ] **macOS**: `/` separators

### 7. Encoding
- [ ] Speciale tekens (€, é, ñ, ü) worden correct weergegeven
- [ ] **Windows**: CP858 encoding voor printer werkt
- [ ] **macOS**: UTF-8 encoding werkt overal

### 8. Performance Tests

#### Koeriers Toewijzing
- [ ] Toewijzen van 1 bestelling: < 0.5 seconden
- [ ] Toewijzen van 10 bestellingen: < 1 seconde
- [ ] UI blijft responsief tijdens toewijzing
- [ ] Geen UI freeze tijdens toewijzing

#### Tab Switching
- [ ] Tab wisselen: < 0.5 seconden (eerste keer)
- [ ] Tab wisselen (tweede keer): < 0.1 seconden
- [ ] Geen UI freeze tijdens tab switch
- [ ] Zware tabs (Geschiedenis, Koeriers) laden asynchroon

#### Data Laden
- [ ] Menu laden: < 1 seconde
- [ ] Geschiedenis laden: < 2 seconden
- [ ] Klantenlijst laden: < 1 seconde

### 9. Error Handling
- [ ] Database errors worden correct afgehandeld
- [ ] Validatie errors worden getoond
- [ ] Network errors (API) worden afgehandeld
- [ ] File not found errors worden afgehandeld
- [ ] Printer errors worden afgehandeld

### 10. Platform-Specifieke Tests

#### Windows Specifiek
- [ ] win32print werkt
- [ ] Printer naam wordt correct opgehaald
- [ ] winsound.Beep werkt
- [ ] Clipboard monitor werkt (als geïnstalleerd)
- [ ] Path separators (`\`) werken
- [ ] CP858 encoding werkt

#### macOS Specifiek
- [ ] Print preview werkt (geen fysieke printer nodig)
- [ ] afplay geluid werkt
- [ ] Path separators (`/`) werken
- [ ] UTF-8 encoding werkt overal
- [ ] Tkinter clipboard werkt

## Bekende Verschillen

### Print Functionaliteit
- **Windows**: Fysieke printer via win32print
- **macOS**: Alleen print preview (geen fysieke printer)

### Geluid Notificaties
- **Windows**: winsound.Beep()
- **macOS**: afplay of os.system()

### Clipboard Monitor
- **Windows**: win32clipboard (optioneel)
- **macOS**: Tkinter clipboard

## Test Rapportage

Na het testen:
1. Run `test_suite.py` op beide platforms
2. Vergelijk de test reports
3. Noteer verschillen in `TEST_RESULTS.md`
4. Fix bugs die op één platform voorkomen

## Tips voor Testing

1. **Test op schone installatie**: Zorg dat je test op een schone installatie zonder bestaande data
2. **Test edge cases**: Lege velden, zeer lange strings, speciale tekens
3. **Test performance**: Gebruik veel data om performance te testen
4. **Test error scenarios**: Probeer fouten te veroorzaken (verwijder bestanden, etc.)
5. **Documenteer verschillen**: Noteer alle verschillen tussen platforms

## Automatische Tests

Run de test suite:
```bash
# macOS
python3 test_suite.py

# Windows
python test_suite.py
```

De test suite genereert automatisch een rapport met alle bevindingen.

