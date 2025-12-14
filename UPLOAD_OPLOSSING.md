# Upload Oplossing voor 102 MB ZIP

## Probleem
Het uploaden van een 102 MB bestand via Python requests geeft timeout errors.

## Beste Oplossing: GitHub CLI

### Stap 1: Installeer GitHub CLI
1. Download van: https://cli.github.com/
2. Installeer de Windows versie
3. Open een nieuwe PowerShell

### Stap 2: Login
```powershell
gh auth login
```
- Kies: GitHub.com
- Kies: HTTPS
- Kies: Login with a web browser
- Volg de instructies

### Stap 3: Upload
```powershell
cd "c:\Users\abdul\Cursor projects\pizzeria-management-system"
gh release upload v1.1.1 "dist\PizzeriaBestelformulier.zip" --repo AbdullahGultekin/pizzeria-management-system --clobber
```

De `--clobber` flag overschrijft bestaande assets automatisch.

## Alternatief: Bestand Splitsen

Als GitHub CLI niet werkt, kunnen we het bestand splitsen in kleinere delen (elk < 25 MB) en die apart uploaden. Maar dit is niet ideaal voor gebruikers.

## Waarom Python requests faalt

- 102 MB is te groot voor een enkele HTTP request via Python
- SSL/TLS handshake timeouts
- GitHub servers kunnen de verbinding afbreken bij langzame uploads
- GitHub CLI gebruikt betere chunked upload mechanismen

## Aanbeveling

**Gebruik GitHub CLI** - dit is de meest betrouwbare methode voor grote bestanden.
