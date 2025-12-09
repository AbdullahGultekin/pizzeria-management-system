# Pizzeria Management System - Executable Build

## ✅ Executable Gemaakt

Het executable bestand is succesvol gemaakt en staat in de `dist` folder:

**📁 Locatie:** `dist\PizzeriaBestelformulier.exe`  
**📦 Grootte:** ~20 MB  
**🖥️ Platform:** Windows (64-bit)

## 🚀 Gebruik

### Direct Gebruik
1. Ga naar de `dist` folder
2. Dubbelklik op `PizzeriaBestelformulier.exe`
3. De applicatie start automatisch

### Op Nieuwe PC Installeren
Het .exe bestand is standalone - je hoeft **geen Python te installeren**!

1. Kopieer `PizzeriaBestelformulier.exe` naar de gewenste locatie
2. Optioneel: Maak een snelkoppeling op het bureaublad
3. Dubbelklik om te starten

## 📋 Vereisten

- **Windows 10/11** (64-bit)
- **Geen Python installatie nodig!**
- De applicatie maakt automatisch de benodigde bestanden aan (database, settings, etc.)

## 🔧 Opnieuw Bouwen

Als je wijzigingen hebt gemaakt en een nieuwe .exe wilt maken:

### Optie 1: Gebruik het batch script
```batch
build_windows.bat
```

### Optie 2: Handmatig
```powershell
# Installeer PyInstaller (als het nog niet geïnstalleerd is)
pip install pyinstaller

# Bouw de executable
pyinstaller pizzeria.spec --clean
```

Het nieuwe .exe bestand wordt in de `dist` folder geplaatst.

## 📝 Belangrijke Bestanden

De volgende bestanden worden automatisch aangemaakt bij eerste gebruik:
- `pizzeria.db` - Database met bestellingen en klanten
- `settings.json` - Applicatie instellingen
- `menu.json` - Menu configuratie (wordt meegenomen in .exe)
- `extras.json` - Extras configuratie (wordt meegenomen in .exe)

## ⚠️ Opmerkingen

- **Eerste start:** De applicatie kan iets langer duren bij de eerste start (ongeveer 5-10 seconden)
- **Antivirus:** Sommige antivirus software kan het .exe bestand als verdacht markeren. Dit is normaal voor PyInstaller executables. Voeg het toe aan uitzonderingen indien nodig.
- **Firewall:** De clipboard monitor heeft geen netwerktoegang nodig, maar als je firewall waarschuwingen geeft, kun je deze negeren.

## 🐛 Problemen Oplossen

### Applicatie start niet
- Controleer of je Windows 10/11 (64-bit) gebruikt
- Probeer als administrator te draaien
- Controleer Windows Event Viewer voor foutmeldingen

### Foutmeldingen bij start
- Zorg dat je schrijfrechten hebt in de map waar de .exe staat
- Controleer of er voldoende schijfruimte is

### Database problemen
- Verwijder `pizzeria.db` en start opnieuw (let op: dit verwijdert alle data!)
- Maak een backup van `pizzeria.db` voordat je wijzigingen maakt

## 📦 Distributie

Om de applicatie te distribueren naar andere PC's:
1. Kopieer alleen `PizzeriaBestelformulier.exe`
2. Het bestand is standalone - geen extra bestanden nodig
3. De database en instellingen worden automatisch aangemaakt bij eerste gebruik

---

**Gemaakt op:** $(Get-Date -Format "dd-MM-yyyy HH:mm")  
**Versie:** 1.0.0

