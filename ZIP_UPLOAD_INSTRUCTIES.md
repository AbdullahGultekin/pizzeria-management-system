# ZIP Upload Instructies

## Probleem Oplost
GitHub ondersteunt geen directe upload van `.exe` bestanden via de web interface. Daarom hebben we de EXE in een ZIP verpakt.

## Stap 1: Upload het ZIP Bestand

1. **Ga naar de release edit pagina:**
   https://github.com/AbdullahGultekin/pizzeria-management-system/releases/edit/v1.1.1

2. **Scroll naar "Attach binaries"** (onderaan de pagina)

3. **Upload het ZIP bestand:**
   - Sleep `PizzeriaBestelformulier.zip` vanuit Verkenner naar het "Attach binaries" gebied
   - OF klik op het gebied en selecteer het ZIP bestand
   - Locatie: `dist\PizzeriaBestelformulier.zip`

4. **Wacht tot upload klaar is** (je ziet een progress indicator)

5. **Klik "Update release"** (onderaan)

## Stap 2: Verifieer

Na upload:
1. Ga terug naar de release pagina
2. Scroll naar "Assets" sectie
3. Je zou nu moeten zien: `PizzeriaBestelformulier.zip`

## Stap 3: Test Update Checker

```powershell
python test_update_check.py
```

De update checker zou nu het ZIP bestand moeten vinden!

## Belangrijk: Gebruikers Instructies

Wanneer gebruikers de update downloaden:
- Ze krijgen een ZIP bestand
- Ze moeten het ZIP bestand uitpakken
- Ze krijgen dan `PizzeriaBestelformulier.exe`

**Tip voor toekomstige releases:**
- Overweeg om de GitHub Actions workflow te gebruiken
- Die kan direct .exe uploaden via de API (geen ZIP nodig)
- Of gebruik het `upload_exe_to_release.py` script met een token

## Automatische ZIP Extractie (Toekomstige Verbetering)

We kunnen de update checker verbeteren om automatisch ZIP bestanden uit te pakken, maar dat vereist extra code. Voor nu werkt het met handmatig uitpakken.
