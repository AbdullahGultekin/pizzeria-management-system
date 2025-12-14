# 🚀 Quick Start Gids

## Voor Ontwikkelaar (Mac/Linux)

### Eerste Keer Setup

```bash
# 1. Clone repository
git clone https://github.com/AbdullahGultekin/pizzeria-management-system.git
cd pizzeria-management-system

# 2. Installeer dependencies
pip install -r requirements.txt

# 3. Start applicatie
python main.py
```

### Wijzigingen Pushen naar GitHub

```bash
# 1. Check wat er is veranderd
git status

# 2. Voeg wijzigingen toe
git add .

# 3. Commit
git commit -m "Beschrijving van je wijzigingen"

# 4. Push
git push origin main

# 5. Als je een nieuwe versie maakt:
#    - Update VERSION in app.py
#    - Commit en push
#    - Maak release tag
git tag v1.1.0
git push origin v1.1.0
```

📖 **Zie [GitHub Push Gids](docs/GITHUB_PUSH_GUIDE.md) voor details**

---

## Voor PC Gebruiker (Windows)

### Eerste Keer Installatie

**Optie 1: Exe (Aanbevolen - Geen Python Nodig!)**

1. Download van [GitHub Releases](https://github.com/AbdullahGultekin/pizzeria-management-system/releases)
2. Pak zip uit
3. Dubbelklik op `main.exe`
4. **Klaar!** 🎉

**Optie 2: Van Broncode**

1. Download repository als ZIP
2. Pak uit naar `C:\pizzeria-management-system\`
3. Run `scripts\setup_windows.bat`
4. Start met `python main.py`

### Updates Installeren

**Voor Exe Gebruikers:**
- App controleert automatisch op updates
- Je krijgt een melding als er een update is
- Klik "Download Nu" en vervang de oude exe

**Voor Broncode Gebruikers:**
```bash
cd C:\pizzeria-management-system
git pull origin main
pip install -r requirements.txt
python main.py
```

📖 **Zie [PC Update Gids](docs/PC_UPDATE_GUIDE.md) voor volledige instructies**

---

## 📚 Meer Documentatie

- [GitHub Push Gids](docs/GITHUB_PUSH_GUIDE.md) - Hoe wijzigingen pushen
- [PC Installatie Gids](docs/PC_INSTALLATIE_GUIDE.md) - Volledige installatie instructies
- [Auto-Update Gids](docs/AUTO_UPDATE_GUIDE.md) - Auto-update systeem uitleg

---

**Laatste update:** 2025-12-09

