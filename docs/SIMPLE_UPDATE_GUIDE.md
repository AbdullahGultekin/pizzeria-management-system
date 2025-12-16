# Simpele Update Gids - Zonder PyInstaller

## 🎯 Overzicht

Er zijn **drie simpele manieren** om updates te doen zonder handmatig PyInstaller te gebruiken:

---

## ✅ Optie 1: Python Mode (Aanbevolen voor Development)

**Gebruik dit als je Python hebt geïnstalleerd!**

### Voordelen:
- ⚡ **Snel** - Geen build tijd
- 🔄 **Automatisch** - Update via git pull
- 🛠️ **Flexibel** - Direct testen van wijzigingen
- 📦 **Geen exe nodig** - Draait direct met Python

### Stappen:

1. **Update code:**
   ```bash
   git pull origin main
   ```

2. **Start applicatie:**
   ```bash
   python main.py
   ```

**Dat is alles!** Geen exe build nodig.

---

## ✅ Optie 2: GitHub Actions (Automatische Exe Builds)

**Gebruik dit voor automatische exe builds bij releases!**

### Voordelen:
- 🤖 **Automatisch** - GitHub bouwt de exe voor je
- 📦 **Geen lokale build** - Alles gebeurt in de cloud
- 🚀 **Bij elke release** - Automatisch beschikbaar

### Stappen:

1. **Maak wijzigingen en push:**
   ```bash
   git add .
   git commit -m "Update: Fix klanten weergave"
   git push origin main
   ```

2. **Maak GitHub Release:**
   - Ga naar GitHub → Releases → "Create a new release"
   - Tag: `v1.1.1` (nieuwe versie)
   - Klik "Publish release"
   - **GitHub Actions bouwt automatisch de exe!** 🎉

3. **Download exe:**
   - Ga naar de release pagina
   - Download `PizzeriaBestelformulier.exe`
   - Klaar!

**Geen PyInstaller nodig op je PC!**

---

## ✅ Optie 3: Auto-Update Systeem (Voor Gebruikers)

**Gebruik dit als je de exe al hebt!**

### Voor Exe Gebruikers:

1. Start de applicatie
2. Ga naar **Help → Controleren op Updates...**
3. Als er een update is:
   - Klik op **"Download Exe"**
   - Download de nieuwe exe
   - Vervang het oude exe bestand
   - Klaar!

### Voor Python Gebruikers:

1. Start de applicatie
2. Ga naar **Help → Controleren op Updates...**
3. Als er een update is:
   - Klik op **"🔄 Automatisch Updaten"**
   - De app update automatisch via git pull
   - Herstart automatisch
   - **Geen exe download nodig!**

---

## 📊 Vergelijking

| Methode | Snelheid | Automatisch | Exe Nodig |
|---------|----------|-------------|-----------|
| **Python Mode** | ⚡⚡⚡ Zeer snel | ✅ Ja | ❌ Nee |
| **GitHub Actions** | ⚡⚡ Snel | ✅✅ Volledig | ✅ Ja (automatisch) |
| **Handmatig PyInstaller** | ⚡ Langzaam | ❌ Nee | ✅ Ja (handmatig) |

---

## 🎯 Aanbeveling

### Voor Development:
**Gebruik Python Mode** - Snel, flexibel, geen build nodig

### Voor Releases:
**Gebruik GitHub Actions** - Automatisch, geen lokale build nodig

### Voor Gebruikers:
**Gebruik Auto-Update** - Eenvoudig, automatische meldingen

---

## 🚀 Quick Start

### Snelste manier (Python):
```bash
git pull origin main
python main.py
```

### Automatische exe (GitHub):
1. Push code naar GitHub
2. Maak release
3. Download exe van GitHub

**Geen PyInstaller nodig!** 🎉










