# GitHub Push Gids - Stap voor Stap

## 📤 Nieuwe Veranderingen naar GitHub Pushen

### Stap 1: Controleer je Wijzigingen

```bash
# Zie welke bestanden zijn gewijzigd
git status

# Zie wat er precies is veranderd
git diff
```

### Stap 2: Voeg Bestanden Toe

```bash
# Voeg alle gewijzigde bestanden toe
git add .

# Of voeg specifieke bestanden toe
git add app.py
git add modules/koeriers.py
```

### Stap 3: Commit je Wijzigingen

```bash
# Maak een commit met een duidelijke beschrijving
git commit -m "Toegevoegd: Auto-update systeem en multi-threading optimalisaties"
```

**Goede commit berichten:**
- `"Toegevoegd: Auto-update systeem"`
- `"Gefixt: Database connection pooling errors"`
- `"Verbeterd: Performance koeriers pagina"`
- `"Update: Versie 1.1.0"`

### Stap 4: Push naar GitHub

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

# Push voor de eerste keer
git push -u origin main
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

```bash
# 1. Check status
git status

# 2. Voeg alle wijzigingen toe
git add .

# 3. Commit
git commit -m "Toegevoegd: Multi-threading optimalisaties"

# 4. Push
git push origin main

# 5. Als je een nieuwe versie maakt:
#    - Update VERSION in app.py
#    - Commit en push
#    - Maak tag en push
git tag v1.1.0
git push origin v1.1.0
```

## ⚠️ Belangrijke Bestanden NIET Pushen

Deze bestanden staan in `.gitignore` en worden NIET gepusht:
- `pizzeria.db` - Database (lokaal blijven)
- `*.log` - Log bestanden
- `__pycache__/` - Python cache
- `dist/` - Build output
- `build/` - Build temp files

## 🐛 Problemen Oplossen

### "Permission denied"
```bash
# Controleer of je ingelogd bent op GitHub
# Gebruik GitHub CLI of SSH keys
```

### "Updates were rejected"
```bash
# Haal eerst de laatste wijzigingen op
git pull origin main

# Los eventuele conflicten op
# Push dan opnieuw
git push origin main
```

### "Remote origin already exists"
```bash
# Verwijder oude remote
git remote remove origin

# Voeg nieuwe remote toe
git remote add origin https://github.com/AbdullahGultekin/pizzeria-management-system.git
```

## 📝 Best Practices

✅ **Commit vaak** - Kleine commits zijn beter dan grote  
✅ **Duidelijke berichten** - Beschrijf wat je hebt gedaan  
✅ **Test eerst** - Test lokaal voordat je pusht  
✅ **Update versie** - Update versie nummer bij belangrijke wijzigingen  
✅ **Maak releases** - Gebruik GitHub Releases voor belangrijke updates  

---

**Gemaakt:** 2025-12-09

