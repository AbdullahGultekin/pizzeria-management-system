# API Cache Notitie

## Situatie
De GitHub pagina toont assets (PizzeriaBestelformulier.zip), maar de API geeft nog 0 assets terug.

## Oorzaak
Dit is **normaal** - GitHub's API heeft een cache die enkele minuten kan duren om bij te werken na het uploaden van assets.

## Oplossing

### Optie 1: Wacht een paar minuten
- GitHub API cache update: 1-5 minuten
- Test daarna opnieuw: `python test_update_check.py`

### Optie 2: Test direct in de EXE
- Start de EXE
- Als er een update is, zou "Download Nu" nu moeten werken
- De download functie gebruikt dezelfde API, maar kan soms eerder werken

### Optie 3: Forceer API refresh
- Maak een kleine wijziging aan de release (bijv. edit description)
- Dit kan de API cache triggeren

## Verificatie

Na een paar minuten, test opnieuw:
```powershell
python check_release_assets.py
```

Je zou nu moeten zien:
- Assets count: 1 (of meer)
- Download URL gevuld in test_update_check.py

## Belangrijk

- De assets **zijn** geüpload (je ziet ze op GitHub)
- De API cache moet alleen nog bijwerken
- Dit is tijdelijk en lost zichzelf op
