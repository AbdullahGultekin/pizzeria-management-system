# GitHub Release Aanmaken - v1.1.1

## 📋 Stappen om Release aan te maken

### Optie 1: Via GitHub Web Interface (Aanbevolen)

1. **Ga naar GitHub Releases:**
   ```
   https://github.com/AbdullahGultekin/pizzeria-management-system/releases/new
   ```

2. **Vul de volgende informatie in:**
   - **Tag version**: `v1.1.1`
   - **Release title**: `Release v1.1.1 - Koeriers en Klantendatabase Verbeteringen`
   - **Description**: Kopieer de inhoud van `RELEASE_NOTES_v1.1.1.md`

3. **Klik op "Publish release"**

### Optie 2: Via Script (Met GitHub Token)

1. **Maak een GitHub Personal Access Token:**
   - Ga naar: https://github.com/settings/tokens
   - Klik op "Generate new token (classic)"
   - Geef het token de naam: "Release Creator"
   - Selecteer scope: `repo` (volledige controle over repositories)
   - Klik op "Generate token"
   - **Kopieer het token** (je ziet het maar één keer!)

2. **Export het token:**
   ```bash
   export GITHUB_TOKEN=your_token_here
   ```

3. **Run het script:**
   ```bash
   ./create_release.sh
   ```

### Optie 3: Via Git Tag (Handmatig)

```bash
# Maak tag
git tag -a v1.1.1 -m "Release v1.1.1 - Koeriers en Klantendatabase Verbeteringen"

# Push tag naar GitHub
git push origin v1.1.1

# Ga daarna naar GitHub en maak release van de tag
# https://github.com/AbdullahGultekin/pizzeria-management-system/releases/new
```

## 📝 Release Notes

De release notes staan in `RELEASE_NOTES_v1.1.1.md`. Kopieer deze naar de GitHub release description.

## ✅ Na het aanmaken van de Release

1. **Update checker zal automatisch de nieuwe release detecteren**
2. **Exe gebruikers kunnen de nieuwe versie downloaden**
3. **Broncode gebruikers kunnen `git pull` doen**

## 🔍 Verificatie

Na het aanmaken van de release, test of het werkt:

```bash
python3 -c "
from utils.updater import UpdateChecker
from app import PizzeriaApp

checker = UpdateChecker(PizzeriaApp.VERSION)
has_update = checker.check_for_updates()
if has_update:
    info = checker.get_update_info()
    print(f'✅ Update gevonden: {info.get(\"latest_version\")}')
else:
    print('ℹ️  Geen update gevonden (wacht even, GitHub API kan vertraging hebben)')
"
```

