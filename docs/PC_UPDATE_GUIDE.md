# PC Update Gids - Code Updaten van GitHub

## 🔄 Code Updaten op Windows PC (Zonder PyInstaller)

### Eerste Keer (Als je nog geen repository hebt)

```bash
# 1. Open Command Prompt of PowerShell
# 2. Ga naar gewenste locatie (bijv. C:\)
cd C:\

# 3. Clone de repository
git clone https://github.com/AbdullahGultekin/pizzeria-management-system.git

# 4. Ga naar de project map
cd pizzeria-management-system

# 5. Installeer dependencies (alleen eerste keer)
pip install -r requirements.txt
pip install pywin32

# 6. Start de applicatie
python main.py
```

---

### Updates Ophalen (Als je al een repository hebt)

#### Optie 1: Automatisch via App (Aanbevolen!)

**De app heeft een ingebouwd auto-update systeem:**

1. Start de applicatie
2. Als er een update is, krijg je automatisch een melding (na 3 seconden)
3. Klik op **"🔄 Automatisch Updaten"** knop
4. De app zal:
   - Je lokale gegevens backuppen
   - `git pull origin main` uitvoeren
   - Nieuwe dependencies installeren
   - De app opnieuw starten

**Of handmatig controleren:**
- Ga naar **Help** → **Controleren op Updates...**
- Klik op **"🔄 Automatisch Updaten"** als er een update is

#### Optie 2: Pull Handmatig (Via Command Prompt)

```bash
# 1. Open Command Prompt of PowerShell
# 2. Ga naar je project map
cd C:\pizzeria-management-system

# 3. Haal de laatste wijzigingen op
git pull origin main

# 4. Installeer nieuwe dependencies (als er nieuwe zijn)
pip install -r requirements.txt

# 5. Start de applicatie
python main.py
```

#### Optie 3: Fetch + Merge (Meer controle)

```bash
# 1. Ga naar project map
cd C:\pizzeria-management-system

# 2. Haal updates op (zonder te mergen)
git fetch origin

# 3. Zie wat er is veranderd
git log HEAD..origin/main --oneline

# 4. Merge de updates
git merge origin/main

# 5. Installeer nieuwe dependencies
pip install -r requirements.txt

# 6. Start de applicatie
python main.py
```

#### Optie 4: Reset (Als je lokale wijzigingen wilt overschrijven)

⚠️ **Waarschuwing:** Dit verwijdert alle lokale wijzigingen!

```bash
# 1. Ga naar project map
cd C:\pizzeria-management-system

# 2. Verwijder alle lokale wijzigingen
git reset --hard origin/main

# 3. Haal laatste updates op
git pull origin main

# 4. Installeer dependencies
pip install -r requirements.txt

# 5. Start de applicatie
python main.py
```

---

## 📋 Stap-voor-Stap Voorbeeld

### Scenario: Je hebt al een lokale kopie

```bash
# Open Command Prompt (Win + R, type "cmd", Enter)

# Stap 1: Navigeer naar je project
cd C:\pizzeria-management-system

# Stap 2: Check huidige status
git status

# Stap 3: Haal updates op
git pull origin main

# Stap 4: Als er nieuwe dependencies zijn
pip install -r requirements.txt

# Stap 5: Start applicatie
python main.py
```

---

## 🔍 Handige Commando's

### Check Status
```bash
# Zie welke bestanden zijn gewijzigd
git status

# Zie laatste commits
git log --oneline -5

# Zie welke branch je gebruikt
git branch
```

### Check voor Updates (Zonder te Pullen)
```bash
# Haal updates op zonder te mergen
git fetch origin

# Zie verschil tussen lokaal en remote
git log HEAD..origin/main --oneline
```

### Lokale Wijzigingen Opslaan (Als je wijzigingen hebt)
```bash
# Stash (tijdelijk opslaan) je wijzigingen
git stash

# Haal updates op
git pull origin main

# Herstel je wijzigingen
git stash pop
```

---

## ⚠️ Belangrijke Bestanden (Blijven Lokaal)

Deze bestanden worden **NIET** overschreven bij update:
- `pizzeria.db` - Je database (blijft behouden)
- `settings.json` - Je instellingen (blijft behouden)
- `menu.json` - Menu configuratie (wordt alleen bijgewerkt als je het toestaat)
- `extras.json` - Extras configuratie (wordt alleen bijgewerkt als je het toestaat)
- `logs/` - Log bestanden

---

## 🐛 Problemen Oplossen

### "Your local changes would be overwritten"

**Probleem:** Je hebt lokale wijzigingen die conflicteren met updates

**Oplossing 1: Stash je wijzigingen**
```bash
git stash
git pull origin main
git stash pop
```

**Oplossing 2: Commit je wijzigingen eerst**
```bash
git add .
git commit -m "Mijn lokale wijzigingen"
git pull origin main
```

**Oplossing 3: Overschrijf lokale wijzigingen (⚠️ Let op!)**
```bash
git reset --hard origin/main
git pull origin main
```

### "Failed to connect to GitHub"

**Probleem:** Geen internet of firewall blokkeert

**Oplossing:**
1. Controleer internet verbinding
2. Controleer firewall instellingen
3. Probeer opnieuw: `git pull origin main`

### "Not a git repository"

**Probleem:** Je bent niet in een git repository

**Oplossing:**
```bash
# Check of je in de juiste map bent
cd C:\pizzeria-management-system

# Check of .git folder bestaat
dir .git

# Als .git niet bestaat, clone opnieuw:
cd C:\
git clone https://github.com/AbdullahGultekin/pizzeria-management-system.git
```

### "Permission denied"

**Probleem:** Geen schrijfrechten

**Oplossing:**
- Run Command Prompt als Administrator
- Of verander map locatie naar een map waar je wel rechten hebt

---

## ✅ Quick Reference

**Eerste keer:**
```bash
cd C:\
git clone https://github.com/AbdullahGultekin/pizzeria-management-system.git
cd pizzeria-management-system
pip install -r requirements.txt
python main.py
```

**Updates ophalen:**
```bash
cd C:\pizzeria-management-system
git pull origin main
pip install -r requirements.txt
python main.py
```

**Check voor updates:**
```bash
cd C:\pizzeria-management-system
git fetch origin
git log HEAD..origin/main --oneline
```

---

## 📝 Tips

✅ **Update regelmatig** - Haal updates op voordat je gaat werken  
✅ **Check status eerst** - Gebruik `git status` om te zien wat er is veranderd  
✅ **Backup database** - Maak backup van `pizzeria.db` voor belangrijke updates  
✅ **Lees release notes** - Check GitHub Releases voor belangrijke wijzigingen  

---

**Gemaakt:** 2025-12-09

