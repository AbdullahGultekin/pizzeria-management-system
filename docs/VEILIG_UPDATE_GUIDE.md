# Veilige Update Gids - Lokale Gegevens Beschermen

## 🛡️ Overzicht

Deze gids legt uit hoe je het systeem kunt updaten **zonder lokale gegevens te verliezen**.

## 📋 Welke Lokale Gegevens Worden Beschermd?

De volgende bestanden bevatten **jouw lokale data** en worden automatisch beschermd:

- ✅ **pizzeria.db** - Database met alle bestellingen en klanten
- ✅ **settings.json** - Jouw instellingen (printer, categorie volgorde, etc.)
- ✅ **app.log** - Log bestanden
- ✅ **app_errors.log** - Error logs
- ✅ **pizzeria_backup.db** - Backup bestanden

Deze bestanden staan in `.gitignore` en worden **niet** naar GitHub geüpload.

---

## 🚀 Methode 1: Veilig Update Script (Aanbevolen)

### Gebruik het veilige update script:

```bash
scripts\update\update_safe.bat
```

### Wat doet dit script?

1. ✅ **Backup maken** van alle lokale gegevens
2. ✅ **Stashen** van lokale code wijzigingen
3. ✅ **Git pull** uitvoeren (laatste wijzigingen ophalen)
4. ✅ **Controleren** of lokale gegevens intact zijn
5. ✅ **Herstellen** indien nodig

### Stappen:

1. Sluit de applicatie (als deze draait)
2. Open PowerShell of Command Prompt
3. Voer uit: `scripts\update\update_safe.bat`
4. Volg de instructies op het scherm

**Je lokale gegevens blijven volledig intact!**

---

## 🔧 Methode 2: Handmatige Veilige Update

Als je het handmatig wilt doen:

### Stap 1: Backup maken

```bash
# Maak backup folder
mkdir data\backup\manual_backup

# Kopieer belangrijke bestanden
copy pizzeria.db data\backup\manual_backup\
copy settings.json data\backup\manual_backup\
```

### Stap 2: Stashen van lokale wijzigingen

```bash
git stash push -m "Backup before update"
```

### Stap 3: Pull van GitHub

```bash
git pull origin main
```

### Stap 4: Controleren

Controleer of je lokale bestanden nog bestaan:
- `pizzeria.db` - moet nog bestaan
- `settings.json` - moet nog bestaan

Als ze ontbreken, herstel ze vanuit de backup:
```bash
copy data\backup\manual_backup\pizzeria.db pizzeria.db
copy data\backup\manual_backup\settings.json settings.json
```

---

## ⚠️ Wat Gebeurt Er Bij Conflicten?

### Scenario 1: Code Bestanden (app.py, etc.)

Als er conflicten zijn in code bestanden:
1. Git zal je waarschuwen
2. Je kunt kiezen om:
   - Jouw wijzigingen te behouden
   - GitHub wijzigingen te accepteren
   - Beide te mergen

**Lokale data bestanden worden NIET beïnvloed!**

### Scenario 2: Data Bestanden (menu.json, extras.json)

Als `menu.json` of `extras.json` zijn gewijzigd:
- Deze bestanden **kunnen** worden geüpdatet van GitHub
- Dit is meestal gewenst (nieuwe menu items, etc.)
- Jouw lokale instellingen in `settings.json` blijven intact

---

## 🔍 Verificatie Na Update

Na een update, controleer:

1. **Database intact?**
   ```bash
   # Start de applicatie en controleer of bestellingen nog zichtbaar zijn
   python main.py
   ```

2. **Instellingen intact?**
   - Controleer printer instellingen
   - Controleer categorie volgorde

3. **Logs intact?**
   - Controleer `app.log` en `app_errors.log`

---

## 📦 Backup Bestanden

Backup bestanden worden opgeslagen in:
```
data\backup\update_backup\
```

Je kunt deze oude backups verwijderen als je zeker weet dat alles werkt.

---

## ❓ Veelgestelde Vragen

### Vraag: Wordt mijn database overschreven?

**Antwoord:** Nee! `pizzeria.db` staat in `.gitignore` en wordt nooit naar GitHub geüpload of overschreven tijdens updates.

### Vraag: Wat als ik per ongeluk `git reset --hard` gebruik?

**Antwoord:** Gebruik het veilige update script. Als je toch `git reset --hard` gebruikt, herstel dan vanuit de backup in `data\backup\update_backup\`.

### Vraag: Kan ik mijn lokale wijzigingen behouden?

**Antwoord:** Ja! Het update script stasht je lokale wijzigingen. Je kunt ze later terugzetten met:
```bash
git stash pop
```

### Vraag: Wat als de update faalt?

**Antwoord:** Het script herstelt automatisch je lokale gegevens als de update faalt.

---

## 🆘 Problemen Oplossen

### Probleem: "Git pull failed"

**Oplossing:**
1. Controleer internet verbinding
2. Probeer opnieuw: `git pull origin main`
3. Als het nog steeds faalt, gebruik: `git fetch origin` en dan `git merge origin/main`

### Probleem: Database lijkt leeg na update

**Oplossing:**
1. Controleer of `pizzeria.db` nog bestaat
2. Als niet, herstel vanuit backup:
   ```bash
   copy data\backup\update_backup\pizzeria.db pizzeria.db
   ```

### Probleem: Instellingen zijn weg

**Oplossing:**
1. Herstel vanuit backup:
   ```bash
   copy data\backup\update_backup\settings.json settings.json
   ```

---

## ✅ Best Practices

1. **Gebruik altijd het veilige update script** voor belangrijke updates
2. **Maak regelmatig backups** van je database (gebruik de backup functie in de app)
3. **Test na update** of alles nog werkt
4. **Lees release notes** als die beschikbaar zijn

---

**Laatste update:** 2025-01-27











