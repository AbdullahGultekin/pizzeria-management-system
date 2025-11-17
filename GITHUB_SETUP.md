# GitHub Repository Setup Instructies

## Nieuwe Repository Naam

**Voorgestelde naam:** `pizzeria-management-system`

## Stappen om Repository te Hernoemen

### Optie 1: Bestaande Repository Hernoemen (Aanbevolen)

1. Ga naar je GitHub repository:
   ```
   https://github.com/AbdullahGultekin/Deskcomputer/settings
   ```

2. Scroll naar beneden naar de sectie **"Repository name"**

3. Wijzig de naam van `Deskcomputer` naar `pizzeria-management-system`

4. Klik op **"Rename"** (onderaan de pagina)

5. Update de remote URL lokaal:
   ```bash
   git remote set-url origin https://github.com/AbdullahGultekin/pizzeria-management-system.git
   ```

6. Verifieer:
   ```bash
   git remote -v
   ```

### Optie 2: Nieuwe Repository Maken

Als je liever een nieuwe repository maakt:

1. Ga naar: https://github.com/new
2. Repository naam: `pizzeria-management-system`
3. Maak de repository aan (zonder README, .gitignore, etc.)
4. Update de remote URL:
   ```bash
   git remote set-url origin https://github.com/AbdullahGultekin/pizzeria-management-system.git
   ```

## Committen en Pushen

Na het hernoemen, commit en push je wijzigingen:

```bash
# Voeg alle wijzigingen toe
git add .

# Commit met beschrijving
git commit -m "Update: Webex integratie, verbeterde UI en nieuwe features"

# Push naar GitHub
git push origin main
```

## Belangrijke Bestanden die NIET gecommit worden

De volgende bestanden worden automatisch genegeerd (via .gitignore):
- `*.db` - Database bestanden
- `*.log` - Log bestanden
- `settings.json` - Instellingen (kan gevoelige data bevatten)
- `__pycache__/` - Python cache
- `.venv/` - Virtual environment
- `build/`, `dist/` - Build bestanden

## Alternatieve Namen

Als je een andere naam wilt gebruiken:
- `pizzeria-bestelsysteem`
- `pizzeria-pos-system`
- `pizzeria-order-management`
- `pizzeria-kassa-systeem`

Pas dan de remote URL aan naar de gekozen naam.



