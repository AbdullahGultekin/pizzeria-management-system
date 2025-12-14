# GitHub Actions Workflow Fix

## Probleem
De workflow uploadt alleen assets wanneer een **nieuwe release wordt gemaakt**, niet wanneer de workflow handmatig wordt getriggerd.

## Oplossing
De workflow is aangepast om:
1. ✅ Assets te uploaden bij nieuwe releases (zoals voorheen)
2. ✅ Assets te uploaden aan de **laatste release** wanneer handmatig getriggerd
3. ✅ Automatisch de laatste release tag te vinden

## Hoe te Gebruiken

### Optie 1: Handmatig Triggeren (Voor Bestaande Release)

1. Ga naar **Actions** tab in GitHub
2. Klik op **"Build Windows Executable"** workflow
3. Klik **"Run workflow"** → **"Run workflow"**
4. De workflow:
   - Bouwt de EXE
   - Vindt automatisch de laatste release (v1.1.1)
   - Uploadt de EXE naar die release

### Optie 2: Nieuwe Release Maken (Automatisch)

1. Maak een nieuwe release op GitHub (bijv. v1.1.2)
2. De workflow wordt automatisch getriggerd
3. De EXE wordt automatisch geüpload

## Test na Upload

Na de workflow run:
1. Check de release: https://github.com/AbdullahGultekin/pizzeria-management-system/releases/tag/v1.1.1
2. Je zou nu moeten zien: `PizzeriaBestelformulier.exe` in de Assets sectie
3. Test de update check: `python test_update_check.py`
4. De `download_url` zou nu gevuld moeten zijn!

## Wat is Aangepast

**`.github/workflows/build-windows.yml`:**
- ✅ Nieuwe step toegevoegd om laatste release tag te vinden
- ✅ Nieuwe step om assets te uploaden aan bestaande release bij handmatige trigger
- ✅ Werkt nu voor zowel nieuwe releases als bestaande releases

## Belangrijk

- De workflow gebruikt `gh` CLI om de laatste release te vinden
- Zorg dat de workflow de juiste permissions heeft (contents: write)
- Na upload zou automatische download moeten werken!
