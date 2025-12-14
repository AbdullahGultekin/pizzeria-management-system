# Stapsgewijze Instructies: EXE Uploaden naar GitHub Release

## Stap 1: Ga naar de Release Pagina

1. Open je browser
2. Ga naar: https://github.com/AbdullahGultekin/pizzeria-management-system/releases
3. Klik op release **v1.1.1** (of de release waar je naar wilt uploaden)

## Stap 2: Edit de Release

1. Op de release pagina, rechtsboven zie je een **"Edit release"** knop
2. Klik op **"Edit release"**

## Stap 3: Scroll naar "Attach binaries"

1. Je ziet nu de release edit pagina
2. Scroll naar beneden, voorbij:
   - Release title
   - Description textarea
   - "Set as the latest release" checkbox
   - "Set as a pre-release" checkbox
3. Je komt bij een sectie met de titel: **"Attach binaries by dropping them here or selecting them"**

   Dit is een groot grijs/vierkant gebied met:
   - Een gestippelde border
   - Tekst: "Attach binaries by dropping them here or selecting them"
   - Soms een upload icoon

## Stap 4: Upload de EXE

**Methode A: Drag & Drop (Eenvoudigst)**
1. Open Windows Verkenner
2. Ga naar: `c:\Users\abdul\Cursor projects\pizzeria-management-system\dist\`
3. Sleep `PizzeriaBestelformulier.exe` naar het "Attach binaries" gebied op de GitHub pagina
4. Wacht tot upload klaar is (je ziet een progress bar)

**Methode B: Klik om te selecteren**
1. Klik op het "Attach binaries" gebied
2. Er opent een bestandskeuze dialoog
3. Navigeer naar: `c:\Users\abdul\Cursor projects\pizzeria-management-system\dist\`
4. Selecteer `PizzeriaBestelformulier.exe`
5. Klik "Open"
6. Wacht tot upload klaar is

## Stap 5: Update Release

1. Na de upload zie je het bestand in de "Attach binaries" sectie
2. Scroll helemaal naar beneden
3. Klik op de groene **"Update release"** knop (rechtsonder)

## Stap 6: Verifieer

1. Je wordt teruggebracht naar de release pagina
2. Scroll naar beneden naar de **"Assets"** sectie
3. Je zou nu moeten zien: `PizzeriaBestelformulier.exe` met de grootte (bijv. 22 MB)

## Visuele Locatie

```
Release Edit Pagina:
┌─────────────────────────────────────┐
│ Release title: [v1.1.1]            │
│                                     │
│ Description:                        │
│ [Text area]                         │
│                                     │
│ ☐ Set as the latest release         │
│ ☐ Set as a pre-release              │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Attach binaries by dropping    │ │ ← HIER!
│ │ them here or selecting them    │ │
│ │                                 │ │
│ │ [Upload icon]                   │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [Update release] [Cancel]           │
└─────────────────────────────────────┘
```

## Troubleshooting

### "Attach binaries" sectie niet zichtbaar?
- Zorg dat je op de **Edit release** pagina bent (niet alleen de release view)
- Scroll helemaal naar beneden
- Refresh de pagina (F5)

### Upload werkt niet?
- Controleer of je de juiste rechten hebt (je moet owner/collaborator zijn)
- Probeer een andere browser
- Controleer bestandsgrootte (max 2GB)

### Bestand niet zichtbaar na upload?
- Refresh de pagina
- Check de "Assets" sectie onderaan de release pagina
