# PC Installatie Gids - Eerste Keer

## 🖥️ Installatie op Windows PC

### Optie 1: Gebruik de Exe (Aanbevolen - Geen Python Nodig!)

#### Stap 1: Download de Exe

1. Ga naar GitHub Releases: https://github.com/AbdullahGultekin/pizzeria-management-system/releases
2. Download de nieuwste `pizzeria-management-vX.X.X-windows.zip`
3. Pak het zip bestand uit
4. Je hebt nu `main.exe` (of `PizzeriaBestelformulier.exe`)

#### Stap 2: Installeer (Eenvoudig!)

**Geen installatie nodig!** Het is een standalone executable:

1. **Kopieer** het `.exe` bestand naar een map (bijv. `C:\PizzeriaApp\`)
2. **Maak een snelkoppeling** op het bureaublad (optioneel):
   - Rechtsklik op `main.exe` → "Snelkoppeling maken"
   - Sleep naar bureaublad
3. **Dubbelklik** om te starten!

#### Stap 3: Eerste Start

Bij de eerste start maakt de app automatisch aan:
- `pizzeria.db` - Database (leeg, klaar voor gebruik)
- `settings.json` - Instellingen (met defaults)
- `menu.json` - Menu configuratie (als het niet bestaat)
- `extras.json` - Extras configuratie (als het niet bestaat)

**Klaar!** 🎉

---

### Optie 2: Van Broncode (Als je Python hebt)

#### Stap 1: Installeer Python

1. Download Python 3.11+ van https://www.python.org/downloads/
2. **Belangrijk:** Vink "Add Python to PATH" aan tijdens installatie!
3. Herstart je computer

#### Stap 2: Clone Repository

```bash
# Open Command Prompt of PowerShell
cd C:\
git clone https://github.com/AbdullahGultekin/pizzeria-management-system.git
cd pizzeria-management-system
```

**Of download als ZIP:**
1. Ga naar GitHub repository
2. Klik "Code" → "Download ZIP"
3. Pak uit naar `C:\pizzeria-management-system\`

#### Stap 3: Installeer Dependencies

```bash
# Ga naar de project map
cd C:\pizzeria-management-system

# Installeer dependencies
pip install -r requirements.txt

# Voor Windows printer support (optioneel):
pip install pywin32
```

#### Stap 4: Run de Applicatie

```bash
# Start de applicatie
python main.py
```

#### Stap 5: Maak een Exe (Optioneel)

Als je een standalone exe wilt maken:

```bash
# Installeer PyInstaller
pip install pyinstaller

# Bouw de exe
cd scripts\build
build_windows.bat

# Of handmatig:
pyinstaller main.spec --clean
```

De exe staat dan in `dist\main.exe`

---

## 🔄 Updates Installeren

### Voor Exe Gebruikers

**Automatisch (Met Auto-Update Systeem):**
1. Start de applicatie
2. Als er een update is, krijg je automatisch een melding
3. Klik "Download Nu"
4. Download de nieuwe exe
5. **Stop de oude applicatie**
6. **Vervang** het oude `.exe` bestand met het nieuwe
7. Start opnieuw

**Handmatig:**
1. Download nieuwe exe van GitHub Releases
2. Stop de applicatie
3. Vervang oude exe met nieuwe
4. Start opnieuw

**⚠️ Belangrijk:** Je database en instellingen blijven behouden!

### Voor Broncode Gebruikers

**Simpelste manier:**
```bash
cd C:\pizzeria-management-system
git pull origin main
pip install -r requirements.txt
python main.py
```

📖 **Zie [PC Update Gids](docs/PC_UPDATE_GUIDE.md) voor volledige instructies en troubleshooting**

---

## 📁 Bestandsstructuur

Na eerste start heb je:

```
C:\PizzeriaApp\
├── main.exe                    # De applicatie
├── pizzeria.db                 # Database (automatisch aangemaakt)
├── settings.json               # Instellingen (automatisch aangemaakt)
├── menu.json                   # Menu (als het niet bestaat, wordt het aangemaakt)
├── extras.json                 # Extras (als het niet bestaat, wordt het aangemaakt)
├── logs\                       # Log bestanden
│   ├── app.log
│   └── app_errors.log
└── data\backup\                # Backups (optioneel)
```

---

## ⚙️ Configuratie

### Printer Instellingen

1. Start de applicatie
2. Ga naar **Instellingen** → **Printer Instellingen**
3. Selecteer je thermal printer
4. Klik "Opslaan"

### Menu Aanpassen

1. Start de applicatie
2. Ga naar **Admin Modus** (via Modus menu)
3. Ga naar **Menu Beheren** tab
4. Pas menu aan
5. Sla op

---

## 🐛 Troubleshooting

### Applicatie Start Niet

**Probleem:** "Windows cannot access the specified device"
- **Oplossing:** Run als Administrator (rechtsklik → "Als administrator uitvoeren")

**Probleem:** Antivirus blokkeert
- **Oplossing:** Voeg exe toe aan uitzonderingen in antivirus software

**Probleem:** "Missing DLL" errors
- **Oplossing:** Installeer Visual C++ Redistributable:
  https://aka.ms/vs/17/release/vc_redist.x64.exe

### Database Problemen

**Probleem:** Database corrupt
- **Oplossing:** 
  1. Maak backup van `pizzeria.db`
  2. Verwijder `pizzeria.db`
  3. Start applicatie opnieuw (maakt nieuwe database)

**Probleem:** Database niet gevonden
- **Oplossing:** Controleer of je schrijfrechten hebt in de map

### Printer Problemen

**Probleem:** Printer niet gevonden
- **Oplossing:**
  1. Controleer of printer is aangesloten en aan staat
  2. Test print vanuit Windows (Print Test Page)
  3. Controleer printer naam in Instellingen

**Probleem:** Print werkt niet
- **Oplossing:** 
  1. Installeer `pywin32`: `pip install pywin32`
  2. Herstart applicatie

### Update Problemen

**Probleem:** Update check werkt niet
- **Oplossing:**
  1. Controleer internet verbinding
  2. Controleer firewall instellingen
  3. Check logs in `logs\app.log`

---

## 📞 Hulp

Als je problemen hebt:
1. Check `logs\app.log` voor foutmeldingen
2. Check `logs\app_errors.log` voor errors
3. Maak een screenshot van de foutmelding
4. Open een issue op GitHub

---

## ✅ Checklist Eerste Installatie

- [ ] Exe gedownload van GitHub Releases
- [ ] Exe gekopieerd naar gewenste locatie
- [ ] Snelkoppeling gemaakt (optioneel)
- [ ] Applicatie gestart
- [ ] Database aangemaakt (automatisch)
- [ ] Instellingen geconfigureerd
- [ ] Printer ingesteld (als nodig)
- [ ] Menu gecontroleerd/aangepast

**Klaar!** 🎉

---

**Gemaakt:** 2025-12-09  
**Versie:** 1.0.0

