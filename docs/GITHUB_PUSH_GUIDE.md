# GitHub Push Gids - Stap voor Stap

## 📤 Nieuwe Veranderingen naar GitHub Pushen

Deze gids legt uit hoe je wijzigingen naar GitHub pusht. Werkt op Windows (PowerShell), Mac en Linux.

---

## 🚀 Snelle Start (Windows PowerShell)

Open PowerShell in je project map en voer deze commando's uit:

```powershell
# 1. Controleer welke bestanden zijn gewijzigd
git status

# 2. Voeg alle wijzigingen toe
git add .

# 3. Maak een commit met beschrijving
git commit -m "Toegevoegd: Nieuw knop en naam normalisatie"

# 4. Push naar GitHub
git push origin main
```

---

## 📋 Stap-voor-Stap Instructies

### Stap 1: Open Terminal/PowerShell

**Windows:**
- Druk op `Windows + X` en kies "Windows PowerShell"
- Of zoek naar "PowerShell" in het start menu
- Navigeer naar je project map:
  ```powershell
  cd "C:\Users\abdul\Cursor projects\pizzeria-management-system"
  ```

**Mac/Linux:**
- Open Terminal
- Navigeer naar je project map:
  ```bash
  cd ~/path/to/pizzeria-management-system
  ```

### Stap 2: Controleer je Wijzigingen

```bash
# Zie welke bestanden zijn gewijzigd
git status
```

Dit toont:
- ✅ **Groen**: Bestanden die al zijn toegevoegd (staged)
- 🔴 **Rood**: Bestanden die nog niet zijn toegevoegd (unstaged)
- ❓ **Grijs**: Bestanden die niet worden getrackt (nieuwe bestanden)

**Zie wat er precies is veranderd:**
```bash
# Zie alle wijzigingen
git diff

# Zie alleen toegevoegde bestanden
git diff --staged
```

### Stap 3: Voeg Bestanden Toe

```bash
# Voeg ALLE gewijzigde bestanden toe
git add .

# Of voeg specifieke bestanden toe
git add app.py
git add ui/customer_form_enhanced.py
git add repositories/customer_repository.py
```

**Tip**: Gebruik `git add .` om alle wijzigingen toe te voegen (veilig - alleen bestanden die al getrackt worden).

### Stap 4: Commit je Wijzigingen

```bash
# Maak een commit met een duidelijke beschrijving
git commit -m "Toegevoegd: Nieuw knop en naam normalisatie"
```

**Goede commit berichten:**
- ✅ `"Toegevoegd: Nieuw knop voor klantgegevens wissen"`
- ✅ `"Gefixt: Update check 404 warning"`
- ✅ `"Verbeterd: Klanten alfabetisch sorteren"`
- ✅ `"Update: Versie 1.1.0"`
- ✅ `"Toegevoegd: Naam normalisatie bij opslaan klanten"`

**Slechte commit berichten:**
- ❌ `"wijzigingen"`
- ❌ `"fix"`
- ❌ `"update"`

### Stap 5: Push naar GitHub

```bash
# Push naar GitHub (main branch)
git push origin main
```

**Als je voor het eerst pusht:**
```bash
# Controleer of je remote repository is ingesteld
git remote -v

# Als er geen remote is, voeg deze toe:
git remote add origin https://github.com/AbdullahGultekin/pizzeria-management-system.git

# Push voor de eerste keer (met tracking)
git push -u origin main
```

**Als je een andere branch gebruikt:**
```bash
# Controleer welke branch je gebruikt
git branch

# Push naar de juiste branch
git push origin master  # Als je master gebruikt
git push origin develop  # Als je develop gebruikt
```

### Stap 5: Maak een Release (Optioneel)

Als je een nieuwe versie hebt gemaakt:

```bash
# Update versie in app.py eerst!
# Bijvoorbeeld: VERSION = "1.1.0"

# Commit de versie update
git add app.py
git commit -m "Update: Versie 1.1.0"
git push origin main

# Maak een tag voor de release
git tag v1.1.0
git push origin v1.1.0
```

**Of via GitHub Website:**
1. Ga naar je repository
2. Klik "Releases" → "Create a new release"
3. Tag: `v1.1.0`
4. Title: `Release v1.1.0`
5. Beschrijf de wijzigingen
6. Klik "Publish release"

## 🔄 Volledige Workflow Voorbeeld

### Normale Push (Dagelijks Gebruik)

```powershell
# 1. Check status
git status

# 2. Voeg alle wijzigingen toe
git add .

# 3. Commit met duidelijke beschrijving
git commit -m "Toegevoegd: Nieuw knop voor klantgegevens wissen"

# 4. Push naar GitHub
git push origin main
```

### Push met Versie Update

```powershell
# 1. Update versie in app.py (bijv. VERSION = "1.1.0")
# 2. Voeg wijzigingen toe
git add app.py
git add .

# 3. Commit versie update
git commit -m "Update: Versie 1.1.0"

# 4. Push naar GitHub
git push origin main

# 5. Maak een tag voor de release
git tag v1.1.0
git push origin v1.1.0

# 6. Maak daarna een release op GitHub (zie GITHUB_RELEASES_GUIDE.md)
```

### Push na Wijzigingen van Anderen

```powershell
# 1. Haal eerst de laatste wijzigingen op
git pull origin main

# 2. Los eventuele conflicten op (als die er zijn)
# 3. Voeg je eigen wijzigingen toe
git add .

# 4. Commit
git commit -m "Mijn wijzigingen"

# 5. Push
git push origin main
```

## ⚠️ Belangrijke Bestanden NIET Pushen

Deze bestanden staan in `.gitignore` en worden NIET gepusht:
- `pizzeria.db` - Database (lokaal blijven)
- `*.log` - Log bestanden
- `__pycache__/` - Python cache
- `dist/` - Build output
- `build/` - Build temp files

## 🐛 Problemen Oplossen

### Probleem: "Permission denied" of "Authentication failed"

**Oplossing 1: Gebruik Personal Access Token**
1. Ga naar GitHub → Settings → Developer settings → Personal access tokens
2. Maak een nieuwe token met `repo` rechten
3. Gebruik de token als wachtwoord bij `git push`

**Oplossing 2: Gebruik GitHub CLI**
```powershell
# Installeer GitHub CLI (als je die nog niet hebt)
# Download van: https://cli.github.com/

# Login met GitHub CLI
gh auth login

# Push dan normaal
git push origin main
```

**Oplossing 3: Gebruik SSH Keys**
```powershell
# Genereer SSH key (als je die nog niet hebt)
ssh-keygen -t ed25519 -C "jouw-email@example.com"

# Voeg SSH key toe aan GitHub (Settings → SSH and GPG keys)
# Verander remote URL naar SSH
git remote set-url origin git@github.com:AbdullahGultekin/pizzeria-management-system.git
```

### Probleem: "Updates were rejected" of "failed to push"

**Oplossing:**
```powershell
# Haal eerst de laatste wijzigingen op
git pull origin main

# Als er conflicten zijn, los deze op
# Push dan opnieuw
git push origin main
```

**Als je zeker weet dat je lokale versie correct is:**
```powershell
# ⚠️ PAS OP: Dit overschrijft remote wijzigingen!
git push --force origin main
```

### Probleem: "Remote origin already exists"

**Oplossing:**
```powershell
# Controleer huidige remote
git remote -v

# Verwijder oude remote
git remote remove origin

# Voeg nieuwe remote toe
git remote add origin https://github.com/AbdullahGultekin/pizzeria-management-system.git

# Verifieer
git remote -v
```

### Probleem: "Branch 'main' does not exist"

**Oplossing:**
```powershell
# Controleer welke branch je gebruikt
git branch

# Als je 'master' gebruikt:
git push origin master

# Of maak 'main' branch:
git checkout -b main
git push -u origin main
```

### Probleem: "Nothing to commit"

**Oplossing:**
- Je hebt geen wijzigingen om te committen
- Controleer met `git status` of er wijzigingen zijn
- Zorg dat je bestanden hebt opgeslagen in je editor

## 📝 Best Practices

✅ **Commit vaak** - Kleine commits zijn beter dan grote  
✅ **Duidelijke berichten** - Beschrijf wat je hebt gedaan  
✅ **Test eerst** - Test lokaal voordat je pusht  
✅ **Update versie** - Update versie nummer bij belangrijke wijzigingen  
✅ **Maak releases** - Gebruik GitHub Releases voor belangrijke updates  
✅ **Pull eerst** - Haal laatste wijzigingen op voordat je pusht  
✅ **Review wijzigingen** - Gebruik `git diff` om te zien wat je pusht  

## 🔍 Handige Git Commando's

```powershell
# Zie commit geschiedenis
git log

# Zie laatste commits
git log --oneline -10

# Zie welke bestanden zijn gewijzigd in laatste commit
git show --name-only

# Verwijder laatste commit (maar behoud wijzigingen)
git reset --soft HEAD~1

# Verwijder laatste commit (en wijzigingen)
git reset --hard HEAD~1

# Zie verschillen tussen lokale en remote
git diff origin/main

# Update lokale repository met remote
git fetch origin

# Zie alle branches
git branch -a
```

## 📚 Gerelateerde Gidsen

- **Releases maken**: Zie `docs/GITHUB_RELEASES_GUIDE.md`
- **GitHub setup**: Zie `docs/GITHUB_SETUP.md`

---

**Laatste update:** 2025-12-12  
**Gemaakt:** 2025-12-09

