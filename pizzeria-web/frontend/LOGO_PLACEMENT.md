# Logo Plaatsing Instructies

## Logo Bestand

Het logo bestand moet geplaatst worden in:
```
pizzeria-web/frontend/public/LOGO-MAGNEET.jpg
```

## Stappen

1. **Plaats het logo bestand** in de `public` directory:
   ```bash
   # Als je het logo hebt, plaats het hier:
   pizzeria-web/frontend/public/LOGO-MAGNEET.jpg
   ```

2. **Alternatieve namen** die ook werken:
   - `LOGO-MAGNEET.png`
   - `logo.jpg`
   - `logo.png`
   - `napoli-logo.jpg`
   - `napoli-logo.png`

3. **Na plaatsing** wordt het logo automatisch geladen op:
   - Contact pagina (`/contact`)
   - Menu pagina (`/menu` en `/`)
   - Alle andere pagina's die het logo gebruiken

## Huidige Implementatie

Het logo wordt gebruikt in:
- **ContactPage.tsx**: Header met logo, naam en contactgegevens
- **PublicMenuPage.tsx**: Header met logo (als toegevoegd)

## Formaat

- **Aanbevolen formaat**: JPG of PNG
- **Aanbevolen grootte**: Minimaal 200x200 pixels (voor scherpe weergave)
- **Aspect ratio**: Vierkant (1:1) werkt het beste vanwege de ronde vorm

## Testen

Na het plaatsen van het logo:
1. Start de frontend: `npm run dev`
2. Navigeer naar: `http://localhost:5173/contact`
3. Het logo zou zichtbaar moeten zijn in de header

## Als Logo Niet Zichtbaar Is

1. Check of het bestand in `public/` directory staat
2. Check de bestandsnaam (moet exact overeenkomen)
3. Check browser console voor 404 errors
4. Refresh de pagina (Ctrl+F5 of Cmd+Shift+R)

