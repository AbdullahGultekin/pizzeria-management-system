# GitHub Releases Aanmaken - Stap voor Stap Gids

Deze gids legt uit hoe je een release aanmaakt in GitHub voor het Pizzeria Management System.

## Wat is een GitHub Release?

Een GitHub Release is een manier om specifieke versies van je software te markeren en beschikbaar te maken voor gebruikers. Releases kunnen bestanden bevatten (zoals .exe bestanden) en release notes.

## Stap-voor-Stap Instructies

### Stap 1: Ga naar je Repository

1. Open je browser en ga naar: https://github.com/AbdullahGultekin/pizzeria-management-system
2. Zorg dat je ingelogd bent met je GitHub account

### Stap 2: Navigeer naar Releases

1. Klik op de knop **"Releases"** in de rechterzijbalk van je repository
   - Of ga direct naar: https://github.com/AbdullahGultekin/pizzeria-management-system/releases
2. Je ziet een pagina met alle bestaande releases (of een lege pagina als er nog geen zijn)

### Stap 3: Maak een Nieuwe Release

1. Klik op de knop **"Create a new release"** (of **"Draft a new release"**)
2. Je komt nu op de release creation pagina

### Stap 4: Vul de Release Informatie In

#### 4.1. Kies een Tag

- **Tag version**: Klik op "Choose a tag" dropdown
- Als je nog geen tags hebt:
  - Typ een nieuwe tag naam, bijv.: `v1.0.0`
  - Klik op "Create new tag: v1.0.0 on publish"
- **Belangrijk**: Tag namen moeten beginnen met `v` gevolgd door versienummer (bijv. `v1.0.0`, `v1.1.0`, `v2.0.0`)

#### 4.2. Kies een Branch

- **Target**: Selecteer de branch waar je release vandaan komt
- Meestal is dit `main` of `master`

#### 4.3. Release Titel

- **Release title**: Bijv. "Version 1.0.0" of "Pizzeria Management System v1.0.0"
- Dit is wat gebruikers zien als titel

#### 4.4. Beschrijving (Release Notes)

- **Describe this release**: Schrijf hier wat er nieuw is in deze versie
- Voorbeelden:
  ```
  ## Nieuwe Features
  - Nieuw klantgegevens formulier
  - Automatische naam normalisatie
  - Alfabetische sortering van klanten
  
  ## Bug Fixes
  - Opgeloste update check warning
  - Verbeterde error handling
  ```

### Stap 5: Upload Bestanden (Optioneel maar Aanbevolen)

Als je een .exe bestand of andere bestanden wilt toevoegen:

1. Scroll naar beneden naar **"Attach binaries by dropping them here or selecting them"**
2. Sleep je bestanden naar het upload gebied, of klik om te bladeren
3. **Aanbevolen bestanden**:
   - `PizzeriaBestelformulier.exe` (Windows executable)
   - `pizzeria-management-v1.0.0-windows.zip` (zip bestand met alle benodigde bestanden)

### Stap 6: Publiceer de Release

**BELANGRIJK**: Er zijn twee opties:

#### Optie A: Draft Release (Niet Zichtbaar)
- Vink **"Set as a pre-release"** aan als je een beta versie maakt
- Vink **"Set as the latest release"** uit als je een draft wilt
- Klik **"Save draft"** - Dit maakt de release NIET zichtbaar voor de update checker!

#### Optie B: Publiceer Direct (Aanbevolen)
- Laat **"Set as a pre-release"** UIT (tenzij het een beta is)
- Laat **"Set as the latest release"** AAN
- Klik **"Publish release"** - Dit maakt de release zichtbaar voor iedereen!

### Stap 7: Verifieer de Release

1. Na het publiceren ga je terug naar de releases pagina
2. Je zou je nieuwe release moeten zien in de lijst
3. Test de update check in je applicatie - de warning zou nu weg moeten zijn!

## Belangrijke Tips

### ✅ DO's

- **Gebruik semantische versienummers**: `v1.0.0`, `v1.1.0`, `v2.0.0`
- **Publiceer releases** (niet alleen drafts) - anders werkt de update check niet
- **Upload .exe bestanden** zodat gebruikers kunnen downloaden
- **Schrijf duidelijke release notes** zodat gebruikers weten wat er nieuw is

### ❌ DON'Ts

- **Maak geen draft releases** als je wilt dat de update check werkt
- **Vergeet niet te publiceren** - drafts zijn niet zichtbaar via de API
- **Gebruik geen spaties in tag namen** - gebruik `v1.0.0` niet `v 1.0.0`

## Versienummering

Gebruik [Semantic Versioning](https://semver.org/):

- **MAJOR** (v2.0.0): Grote wijzigingen, mogelijk niet backwards compatible
- **MINOR** (v1.1.0): Nieuwe features, backwards compatible
- **PATCH** (v1.0.1): Bug fixes, backwards compatible

Voorbeelden:
- `v1.0.0` - Eerste release
- `v1.0.1` - Kleine bug fix
- `v1.1.0` - Nieuwe feature toegevoegd
- `v2.0.0` - Grote wijziging

## Troubleshooting

### Probleem: Update check geeft nog steeds 404

**Oplossingen**:
1. Controleer of de release **gepubliceerd** is (niet draft)
2. Controleer of de repository **publiek** is
3. Wacht een paar minuten - GitHub API kan vertraging hebben
4. Controleer de tag naam - moet beginnen met `v`

### Probleem: Release is niet zichtbaar

**Oplossingen**:
1. Zorg dat je op **"Publish release"** hebt geklikt, niet "Save draft"
2. Controleer of de release niet als "pre-release" is gemarkeerd (tenzij je dat wilt)
3. Refresh de releases pagina

### Probleem: Update check werkt niet

**Oplossingen**:
1. Controleer de repository naam in `utils/updater.py` of `settings.json`
2. Zorg dat er minstens één **gepubliceerde** release is
3. Controleer of de tag naam begint met `v` (bijv. `v1.0.0`)

## Automatische Releases (Geavanceerd)

Je kunt ook automatisch releases maken via GitHub Actions. Dit is handig als je CI/CD gebruikt, maar dat is optioneel.

## Hulp Nodig?

- GitHub Releases Documentatie: https://docs.github.com/en/repositories/releasing-projects-on-github
- GitHub Support: https://support.github.com/



