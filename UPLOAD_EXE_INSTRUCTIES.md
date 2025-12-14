# Instructies: EXE Uploaden naar GitHub Release

## Stap 1: Maak een GitHub Personal Access Token

1. Ga naar: https://github.com/settings/tokens
2. Klik op **"Generate new token (classic)"**
3. Geef de token een naam (bijv. "Release Uploader")
4. Selecteer scope: **`repo`** (volledige repository toegang)
5. Klik **"Generate token"**
6. **KOPIEER DE TOKEN** (je ziet hem maar 1 keer!)

## Stap 2: Upload de EXE

### Optie A: Via Script (Aanbevolen)

**In PowerShell:**
```powershell
# Set je token als environment variable
$env:GITHUB_TOKEN="jouw_token_hier"

# Run het upload script
python upload_exe_to_release.py
```

**Of direct:**
```powershell
python upload_exe_to_release.py
# Voer dan je token in wanneer gevraagd
```

### Optie B: Handmatig via GitHub Website

1. Ga naar: https://github.com/AbdullahGultekin/pizzeria-management-system/releases/tag/v1.1.1
2. Klik op **"Edit release"** (rechtsboven)
3. Scroll naar beneden naar **"Attach binaries by dropping them here or selecting them"**
4. Sleep `dist\PizzeriaBestelformulier.exe` naar het upload veld
   - OF klik "selecting them" en kies het bestand
5. Wacht tot upload klaar is
6. Klik **"Update release"**

## Stap 3: Verifieer

Na upload, test of het werkt:
```powershell
python test_update_check.py
```

Je zou nu moeten zien:
- `Download URL: https://github.com/.../releases/download/v1.1.1/PizzeriaBestelformulier.exe`
- `Update available: True`

## Troubleshooting

### "Release niet gevonden"
- Controleer of release tag exact `v1.1.1` is (met 'v' vooraan)

### "Upload gefaald - 401/403"
- Token heeft niet de juiste permissions
- Maak nieuwe token met `repo` scope

### "Bestand te groot"
- GitHub heeft limiet van 2GB per asset
- Je EXE is ~22MB, dus dit zou moeten werken

### "Timeout"
- Probeer opnieuw, of gebruik handmatige upload (Optie B)
