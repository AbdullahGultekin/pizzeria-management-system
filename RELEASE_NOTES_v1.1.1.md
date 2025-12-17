# Release v1.1.1 - Koeriers en Klantendatabase Verbeteringen

## 🎯 Belangrijkste Verbeteringen

### Koeriers Pagina
- ✅ **Correcte berekening definitief**: Alleen extra's (km, uur, extra bedrag) worden getoond, geen subtotaal of startgeld
- ✅ **Snellere refresh**: Alleen nieuwe bestellingen worden toegevoegd, bestaande blijven staan
- ✅ **Automatische updates**: Bestaande bestellingen worden bijgewerkt als koerier toewijzing verandert
- ✅ **Verbeterde performance**: Incrementele updates in plaats van volledige herlaad

### Klantendatabase Professionalisering
- ✅ **Timestamps**: `created_at` en `updated_at` velden toegevoegd
- ✅ **Postcode scheiding**: Postcode en plaats zijn nu gescheiden velden
- ✅ **Email veld**: Email adres veld toegevoegd
- ✅ **Actief status**: `is_actief` veld voor actieve/inactieve klanten
- ✅ **Telefoon normalisatie**: Alle telefoonnummers worden opgeslagen in E.164 formaat (+32123456789)
- ✅ **Automatische adres updates**: Bij zelfde telefoonnummer wordt altijd laatste adres opgeslagen
- ✅ **Naam validatie**: Cijfers en punten zijn nu toegestaan in naamveld

### Database Migraties
- ✅ **Automatische migraties**: Nieuwe kolommen worden automatisch toegevoegd bij opstarten
- ✅ **Data behoud**: Bestaande data blijft volledig behouden
- ✅ **Backwards compatible**: Oude databases worden automatisch geüpgraded

## 🔧 Technische Details

### Nieuwe Database Velden (klanten tabel)
- `created_at`: Aanmaakdatum van klant record
- `updated_at`: Laatste wijzigingsdatum
- `email`: Email adres van klant
- `postcode`: Postcode (gescheiden van plaats)
- `is_actief`: Actief status (1 = actief, 0 = inactief)

### Verbeterde Functionaliteit
- Telefoonnummers worden genormaliseerd naar E.164 formaat
- Duplicaten worden automatisch gedetecteerd en gemerged
- Bestaande bestellingen blijven behouden bij database updates

## 📝 Scripts Toegevoegd

- `scripts/normalize_klanten_database.py`: Normaliseer bestaande klantendata
- `scripts/check_duplicate_customers.py`: Analyseer duplicaten
- `scripts/merge_duplicate_customers.py`: Merge duplicaten automatisch

## 🚀 Installatie

### Voor Broncode Gebruikers
```bash
git pull origin main
```

### Voor Exe Gebruikers
Download de nieuwste `main.exe` van deze release.

## ⚠️ Belangrijk

- **Database migraties**: Worden automatisch uitgevoerd bij eerste opstarten na update
- **Backup aanbevolen**: Maak altijd een backup voor grote updates
- **Geen data verlies**: Alle bestaande data blijft behouden

## 🐛 Bug Fixes

- Fix: Koeriers definitief berekening toonde verkeerde totalen
- Fix: Naam validatie blokkeerde geldige namen met cijfers
- Fix: Koeriers pagina laadde volledig opnieuw bij elke refresh

## 📚 Documentatie

- `docs/KLANTEN_DATABASE_VERBETERINGEN.md`: Volledige documentatie over klantendatabase verbeteringen
- `docs/AUTO_UPDATE_VERIFICATIE.md`: Auto-update systeem documentatie
- `docs/PC_UPDATE_GUIDE.md`: PC update gids

---

**Versie**: 1.1.1  
**Datum**: 2025-01-09  
**Compatibiliteit**: Backwards compatible met v1.1.0

