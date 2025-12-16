# Update Gids - Pizzeria Management System

## 📋 Overzicht

Er zijn **twee manieren** om het systeem te updaten, afhankelijk van hoe je de applicatie gebruikt:

1. **Python Development Mode** (aanbevolen voor dagelijks gebruik)
2. **Executable Mode** (alleen nodig voor distributie)

---

## 🚀 Optie 1: Python Development Mode (Aanbevolen)

**Gebruik dit als je Python geïnstalleerd hebt op je computer.**

### Voordelen:
- ✅ Snelle updates (geen rebuild nodig)
- ✅ Directe toegang tot logs en debugging
- ✅ Makkelijker om aanpassingen te maken
- ✅ Geen lange build tijd

### Update Stappen:

1. **Pull de laatste wijzigingen van GitHub:**
   ```bash
   git pull origin main
   ```

2. **Update dependencies (als er nieuwe zijn):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start de applicatie:**
   ```bash
   python main.py
   ```
   
   Of gebruik het start script:
   ```bash
   scripts\start\start_pizzeria.bat
   ```

**Dat is alles!** De applicatie draait nu met de laatste updates.

---

## 📦 Optie 2: Executable Mode (Voor Distributie)

**Gebruik dit alleen als je een .exe bestand nodig hebt voor distributie naar andere computers.**

### Wanneer gebruiken:
- Je wilt de applicatie delen met anderen die geen Python hebben
- Je wilt een standalone .exe bestand
- Je distribueert naar meerdere computers

### Update Stappen:

1. **Pull de laatste wijzigingen:**
   ```bash
   git pull origin main
   ```

2. **Bouw een nieuwe .exe:**
   ```bash
   pyinstaller pizzeria.spec --clean --noconfirm
   ```

3. **Het nieuwe .exe bestand staat in:**
   ```
   dist\PizzeriaBestelformulier.exe
   ```

**Let op:** Dit proces duurt 2-5 minuten.

---

## 🔄 Automatische Update Script

Je kunt ook het update script gebruiken:

### Windows:
```bash
scripts\update\update.bat
```

Dit script doet automatisch:
1. Git pull (laatste wijzigingen ophalen)
2. Dependencies updaten
3. Optioneel: Nieuwe .exe bouwen

---

## ❓ Welke Methode Moet Ik Gebruiken?

### Gebruik **Python Mode** als:
- ✅ Je Python hebt geïnstalleerd
- ✅ Je de applicatie zelf gebruikt
- ✅ Je regelmatig updates doet
- ✅ Je aanpassingen wilt maken

### Gebruik **Executable Mode** als:
- ✅ Je de applicatie deelt met anderen
- ✅ Andere computers geen Python hebben
- ✅ Je een standalone bestand nodig hebt
- ✅ Je zelden updates doet

---

## 📝 Best Practices

### Voor Development:
1. Werk altijd in Python mode
2. Test wijzigingen direct met `python main.py`
3. Maak alleen een .exe als je klaar bent met testen

### Voor Productie:
1. Test eerst in Python mode
2. Maak dan een .exe voor distributie
3. Test de .exe voordat je deze deelt

---

## 🔧 Troubleshooting

### Probleem: Git pull geeft conflicten
**Oplossing:**
```bash
git stash
git pull origin main
git stash pop
```

### Probleem: Dependencies zijn verouderd
**Oplossing:**
```bash
pip install -r requirements.txt --upgrade
```

### Probleem: .exe build faalt
**Oplossing:**
1. Controleer of PyInstaller geïnstalleerd is: `pip install pyinstaller`
2. Controleer of alle bestanden aanwezig zijn (menu.json, extras.json)
3. Probeer opnieuw met `--clean` flag

---

## 📅 Update Frequentie

- **Dagelijks/Wekelijks:** Gebruik Python mode (git pull + python main.py)
- **Maandelijks/Per Release:** Maak een nieuwe .exe voor distributie

---

**Laatste update:** 2025-01-27












