kl# Auto-Update Systeem - Gebruikershandleiding

## 📋 Overzicht

Het Pizzeria Management System heeft nu een **automatisch update systeem** dat:
- ✅ Automatisch controleert op nieuwe versies bij opstarten
- ✅ Je waarschuwt wanneer er een update beschikbaar is
- ✅ **Automatisch updaten via git pull** (zonder exe te bouwen!) 🎉
- ✅ Of download exe bestand als je dat liever hebt
- ✅ **GitHub Actions** automatisch nieuwe exe's bouwt bij elke release

## 🚀 Nieuwe Workflow (Veel Simpeler!)

### Voor Jou (Ontwikkelaar):

**Oude manier:**
1. Maak wijzigingen
2. Push naar GitHub
3. Op PC: Pull van GitHub handmatig
4. Run PyInstaller handmatig
5. Test de exe
6. Deel de exe

**Nieuwe manier (Twee opties):**

#### Optie A: Automatische Git Update (Zonder Exe) 🔄
1. Maak wijzigingen
2. Update versie in `app.py` (bijv. `VERSION = "1.1.0"`)
3. Commit en push naar GitHub
4. **Gebruikers krijgen automatisch melding en kunnen direct updaten!**
5. Geen exe build nodig voor Python gebruikers! 🎉

#### Optie B: Exe Release (Voor Distributie) 📦
1. Maak wijzigingen
2. Update versie in `app.py` (bijv. `VERSION = "1.1.0"`)
3. Commit en push naar GitHub
4. Maak een **GitHub Release** met tag (bijv. `v1.1.0`)
5. **GitHub Actions bouwt automatisch de exe!** 🎉

### GitHub Release Maken:

**Optie 1: Via GitHub Website**
1. Ga naar je repository op GitHub
2. Klik op "Releases" → "Create a new release"
3. Tag: `v1.1.0` (gebruik je nieuwe versie nummer)
4. Title: `Release v1.1.0`
5. Beschrijf de wijzigingen
6. Klik "Publish release"
7. **GitHub Actions bouwt automatisch de exe!**

**Optie 2: Via Git Command**
```bash
# Update versie in app.py eerst!
git add app.py
git commit -m "Update naar versie 1.1.0"
git tag v1.1.0
git push origin main
git push origin v1.1.0
```

## 📥 Voor Gebruikers:

### Automatische Update Check:

1. **Bij opstarten:** De app controleert automatisch op updates (na 3 seconden)
2. **Als er een update is:** Je krijgt een melding met:
   - Huidige versie vs. nieuwe versie
   - Release notes
   - **🔄 Automatisch Updaten** knop (als je in een git repository werkt)
   - **📥 Download Exe** knop (als je een exe gebruikt)

### Twee Update Methoden:

#### Methode 1: Automatisch Updaten (Aanbevolen voor Developers) 🔄

**Werkt alleen als je de app draait vanuit een git repository!**

1. Klik op **"🔄 Automatisch Updaten"** in de update melding
2. Bevestig de update
3. De app doet automatisch:
   - ✅ Backup van je lokale gegevens
   - ✅ `git pull` om laatste wijzigingen op te halen
   - ✅ Herstart de app met nieuwe versie
4. **Klaar!** Je database en instellingen blijven behouden

**Voordelen:**
- ⚡ Snel (geen download nodig)
- 🛡️ Veilig (automatische backup)
- 🔄 Direct beschikbaar (geen exe build nodig)

#### Methode 2: Exe Download (Voor Standalone Gebruikers) 📥

1. Klik op **"📥 Download Exe"** in de update melding
2. Download de nieuwe `.exe` of `.zip` bestand
3. **Vervang** het oude `.exe` bestand met het nieuwe
4. Start de app opnieuw

**⚠️ Belangrijk:** Je database (`pizzeria.db`) en instellingen blijven behouden!

### Handmatig Controleren:

1. Open de app
2. Ga naar **Help** → **Controleren op Updates...**
3. De app controleert op updates
4. Als er een update is, krijg je dezelfde opties als hierboven

## 🔧 Technische Details

### GitHub Actions Workflow:

De workflow (`.github/workflows/build-windows.yml`) doet automatisch:
1. Checkout de code
2. Installeer Python en dependencies
3. Update versie in `app.py` (van tag)
4. Bouw de exe met PyInstaller
5. Maak een zip bestand
6. Upload naar GitHub Release

### Update Checker:

- Controleert GitHub Releases API
- Vergelijkt versie nummers
- Vindt automatisch de juiste download voor je platform
- Werkt in de achtergrond (blokkeert niet)

## 📝 Versie Nummering

Gebruik **Semantic Versioning**:
- **Major** (1.0.0 → 2.0.0): Grote wijzigingen
- **Minor** (1.0.0 → 1.1.0): Nieuwe features
- **Patch** (1.0.0 → 1.0.1): Bug fixes

**Voorbeeld:**
- `1.0.0` - Eerste release
- `1.0.1` - Bug fix
- `1.1.0` - Nieuwe feature (bijv. auto-update)
- `2.0.0` - Grote refactor

## 🐛 Troubleshooting

### Update Check Werkt Niet:

1. Controleer internet verbinding
2. Controleer of GitHub API bereikbaar is
3. Check logs in `logs/app.log`

### GitHub Actions Build Faalt:

1. Check de "Actions" tab op GitHub
2. Bekijk de build logs
3. Controleer of `main.spec` correct is
4. Controleer of alle dependencies in `requirements.txt` staan

### Exe Download Werkt Niet:

1. Controleer of de release is gepubliceerd (niet draft)
2. Controleer of de exe asset is geüpload
3. Probeer handmatig te downloaden van GitHub Releases pagina

## 🎯 Voordelen

✅ **Geen handmatige builds meer** - GitHub doet het automatisch  
✅ **Gebruikers krijgen automatisch meldingen** - Geen verouderde versies  
✅ **Eenvoudigere workflow** - Minder stappen  
✅ **Betere versie controle** - Duidelijke versie nummers  
✅ **Release notes** - Gebruikers zien wat er nieuw is  

---

**Gemaakt:** 2025-12-09  
**Versie:** 1.0.0

