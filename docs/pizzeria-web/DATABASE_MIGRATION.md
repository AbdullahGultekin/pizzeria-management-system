# Database Migratie - Status Kolom Toevoegen

## Stap 1: Database Migratie Script Uitvoeren

Voer het migratie script uit om de `status` kolom toe te voegen aan de bestaande database:

```bash
cd pizzeria-web/backend
python add_status_column.py
```

Dit script:
- Voegt de `status` kolom toe aan de `bestellingen` tabel
- Zet bestaande orders op status "Voltooid"
- Nieuwe orders krijgen automatisch status "Nieuw"

## Stap 2: Database Opnieuw Initialiseren (Alternatief)

Als je de database opnieuw wilt initialiseren (LET OP: dit verwijdert alle data):

```bash
cd pizzeria-web/backend
python -c "from app.core.database import init_db; init_db()"
```

## Status Opties

De volgende status opties zijn beschikbaar:
- **Nieuw**: Bestelling is net geplaatst
- **In behandeling**: Bestelling wordt voorbereid
- **Klaar**: Bestelling is klaar voor bezorging
- **Onderweg**: Bestelling is onderweg
- **Afgeleverd**: Bestelling is afgeleverd
- **Geannuleerd**: Bestelling is geannuleerd

## Testen

Na de migratie:
1. Start de backend opnieuw
2. Test het plaatsen van een nieuwe bestelling (zou status "Nieuw" moeten hebben)
3. Test het updaten van de status in de admin interface
4. Test het opzoeken van een bestelling via bonnummer op de status pagina


