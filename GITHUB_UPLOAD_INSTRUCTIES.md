# GitHub Upload Instructies (Grote Bestanden)

## Probleem
GitHub web interface heeft een **25 MB limiet** voor bestand uploads. De EXE ZIP is **102 MB**, dus te groot voor web upload.

## Oplossing: GitHub API Upload

Gebruik de GitHub API om grote bestanden te uploaden (geen limiet).

## Stap 1: Maak een GitHub Personal Access Token

1. Ga naar: https://github.com/settings/tokens
2. Klik **"Generate new token (classic)"**
3. Geef een naam: `Upload Release Assets`
4. Selecteer scope: **`repo`** (volledige controle over repositories)
5. Klik **"Generate token"**
6. **Kopieer de token** (je ziet hem maar 1x!)

## Stap 2: Stel de token in

### Optie A: Tijdelijk (alleen deze sessie)
```powershell
$env:GITHUB_TOKEN="jouw_token_hier"
```

### Optie B: Permanent (aanbevolen)
```powershell
[System.Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "jouw_token", "User")
```
Dan PowerShell opnieuw starten.

## Stap 3: Upload het bestand

```powershell
cd "c:\Users\abdul\Cursor projects\pizzeria-management-system"
python upload_exe_to_github.py
```

Het script zal:
- De release vinden
- Controleren of er al een asset is
- De nieuwe ZIP uploaden
- De download URL tonen

## Alternatief: GitHub CLI

Als je GitHub CLI hebt geïnstalleerd:

```powershell
# Install GitHub CLI (als je het nog niet hebt)
# Download van: https://cli.github.com/

# Login
gh auth login

# Upload asset
gh release upload v1.1.1 "dist\PizzeriaBestelformulier.zip" --repo AbdullahGultekin/pizzeria-management-system
```

## Belangrijk

- **Token beveiliging**: Deel je token NOOIT publiekelijk
- **API cache**: Wacht 2-5 minuten na upload voordat de API cache bijwerkt
- **Grootte limiet**: Via API is er geen 25 MB limiet

## Troubleshooting

### "GITHUB_TOKEN niet gevonden"
- Zorg dat je de token hebt ingesteld (zie Stap 2)
- Start PowerShell opnieuw als je permanent hebt ingesteld

### "Release niet gevonden"
- Controleer of release v1.1.1 bestaat
- Controleer of de repository naam correct is

### "Upload gefaald"
- Controleer of de token de juiste permissies heeft (`repo` scope)
- Controleer of het bestand bestaat en niet te groot is voor je internetverbinding
