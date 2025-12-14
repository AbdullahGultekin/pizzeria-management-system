# GitHub CLI Installatie en Gebruik

## Wat is GitHub CLI?

GitHub CLI (`gh`) is een officiële command-line tool van GitHub die het uploaden van grote bestanden veel betrouwbaarder maakt dan via Python scripts.

## Stap 1: Download GitHub CLI

1. Ga naar: **https://cli.github.com/**
2. Klik op **"Download for Windows"**
3. Het downloadt automatisch `gh_windows_amd64.msi`

## Stap 2: Installeer GitHub CLI

1. Dubbelklik op het gedownloade `.msi` bestand
2. Volg de installatie wizard:
   - Klik "Next" op alle schermen
   - Accepteer de licentie
   - Klik "Install"
   - Wacht tot installatie klaar is
   - Klik "Finish"

## Stap 3: Verifieer Installatie

Open een **nieuwe PowerShell** (belangrijk: sluit de oude en open een nieuwe!) en test:

```powershell
gh --version
```

Je zou moeten zien: `gh version X.X.X (YYYY-MM-DD)`

Als je een fout krijgt, controleer of PowerShell opnieuw is gestart.

## Stap 4: Login met GitHub

```powershell
gh auth login
```

Volg de instructies:

1. **What account do you want to log into?**
   - Kies: `GitHub.com`
   - Druk Enter

2. **What is your preferred protocol for Git operations?**
   - Kies: `HTTPS`
   - Druk Enter

3. **How would you like to authenticate GitHub CLI?**
   - Kies: `Login with a web browser`
   - Druk Enter

4. **Paste your authentication token:**
   - Druk Enter (we gebruiken web browser login)

5. Een browser venster opent automatisch
   - Klik "Authorize github"
   - Of kopieer de code die wordt getoond en plak deze in de browser

6. Als je bent ingelogd, zie je: "✓ Authentication complete"

## Stap 5: Upload de ZIP naar GitHub

```powershell
cd "c:\Users\abdul\Cursor projects\pizzeria-management-system"
gh release upload v1.1.1 "dist\PizzeriaBestelformulier.zip" --repo AbdullahGultekin/pizzeria-management-system --clobber
```

**Uitleg:**
- `v1.1.1` = de release tag
- `dist\PizzeriaBestelformulier.zip` = het bestand om te uploaden
- `--repo AbdullahGultekin/pizzeria-management-system` = je repository
- `--clobber` = overschrijf bestaande assets automatisch

## Stap 6: Verifieer Upload

Na de upload, check de release pagina:
https://github.com/AbdullahGultekin/pizzeria-management-system/releases/tag/v1.1.1

Je zou `PizzeriaBestelformulier.zip` moeten zien in de "Assets" sectie.

## Troubleshooting

### "gh: command not found"
- **Oplossing**: Sluit PowerShell volledig en open een nieuwe
- Of voeg GitHub CLI toe aan PATH handmatig

### "Authentication failed"
- **Oplossing**: Run opnieuw `gh auth login`
- Kies "Login with a web browser" optie

### "Release not found"
- **Oplossing**: Controleer of release v1.1.1 bestaat
- Check: https://github.com/AbdullahGultekin/pizzeria-management-system/releases

### "Upload timeout"
- **Oplossing**: Check je internet verbinding
- Probeer later opnieuw
- GitHub CLI is veel betrouwbaarder dan Python requests voor grote bestanden

### "File too large"
- **Oplossing**: Via GitHub CLI is er geen 25 MB limiet
- Als dit toch gebeurt, check of het bestand echt te groot is (> 2 GB)

## Handige GitHub CLI Commands

```powershell
# Check login status
gh auth status

# List releases
gh release list --repo AbdullahGultekin/pizzeria-management-system

# View release details
gh release view v1.1.1 --repo AbdullahGultekin/pizzeria-management-system

# Download release asset
gh release download v1.1.1 --repo AbdullahGultekin/pizzeria-management-system
```

## Voordelen van GitHub CLI

✅ **Geen 25 MB limiet** (zoals web interface)  
✅ **Betrouwbaarder** voor grote bestanden (102 MB+)  
✅ **Automatische retry** bij netwerk problemen  
✅ **Progress indicator** tijdens upload  
✅ **Eenvoudig te gebruiken** via command line  

## Klaar!

Na installatie en login kun je de ZIP uploaden met één commando. Dit is veel betrouwbaarder dan Python scripts voor grote bestanden.
