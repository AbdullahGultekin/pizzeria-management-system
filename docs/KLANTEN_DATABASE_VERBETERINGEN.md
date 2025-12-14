# Klantendatabase Verbeteringen

## Huidige Structuur

De huidige `klanten` tabel heeft:
- ✅ Basis contactgegevens (telefoon, naam, adres)
- ✅ CRM functionaliteit (notities, voorkeur_levering)
- ✅ Statistieken (totaal_bestellingen, totaal_besteed, laatste_bestelling)
- ✅ Loyaliteitsprogramma (volle_kaart)

## Voorgestelde Verbeteringen

### 1. **Timestamps** (Aanbevolen: Hoog)
Toevoegen van `created_at` en `updated_at` voor audit trail:
```sql
created_at TEXT DEFAULT CURRENT_TIMESTAMP,
updated_at TEXT DEFAULT CURRENT_TIMESTAMP
```

**Voordelen:**
- Weten wanneer klant is aangemaakt
- Weten wanneer laatste update was
- Audit trail voor compliance

### 2. **Adres Historie** (Aanbevolen: Hoog)
Nieuwe tabel `klant_adressen` voor meerdere adressen per klant:
```sql
CREATE TABLE klant_adressen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klant_id INTEGER NOT NULL,
    straat TEXT NOT NULL,
    huisnummer TEXT,
    postcode TEXT,
    plaats TEXT NOT NULL,
    is_huidig INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
)
```

**Voordelen:**
- Meerdere adressen per klant (thuis, werk, etc.)
- Historie van adreswijzigingen
- Betere tracking van bezorgadressen

### 3. **Postcode Apart** (Aanbevolen: Medium)
Postcode en gemeente scheiden:
```sql
postcode TEXT,
gemeente TEXT  -- in plaats van "plaats" die beide bevat
```

**Voordelen:**
- Betere validatie
- Makkelijker sorteren/filteren
- Betere adresvalidatie

### 4. **Email Veld** (Aanbevolen: Medium)
```sql
email TEXT,
email_geverifieerd INTEGER DEFAULT 0
```

**Voordelen:**
- Marketing mogelijkheden
- Betere communicatie
- Digitale facturen

### 5. **Soft Deletes** (Aanbevolen: Medium)
```sql
deleted_at TEXT NULL,
is_actief INTEGER DEFAULT 1
```

**Voordelen:**
- Gegevens niet echt verwijderen
- Mogelijkheid tot herstel
- Betere data integriteit

### 6. **Klant Status** (Aanbevolen: Low)
```sql
status TEXT DEFAULT 'actief'  -- actief, inactief, geblokkeerd, etc.
```

**Voordelen:**
- Betere klantsegmentatie
- Marketing mogelijkheden
- Betere rapportage

### 7. **Contact Historie** (Aanbevolen: Low)
Nieuwe tabel `klant_contact_historie`:
```sql
CREATE TABLE klant_contact_historie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klant_id INTEGER NOT NULL,
    contact_type TEXT,  -- 'telefoon', 'email', 'bezoek', etc.
    opmerking TEXT,
    datum_tijd TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
)
```

**Voordelen:**
- Volledige contact historie
- Betere klantenservice
- Marketing inzichten

### 8. **Tags/Categorieën** (Aanbevolen: Low)
Nieuwe tabel `klant_tags`:
```sql
CREATE TABLE klant_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klant_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
)
```

**Voordelen:**
- Klantsegmentatie
- Marketing campagnes
- Betere organisatie

## Implementatie Prioriteit

### Fase 1 (Direct implementeren):
1. ✅ Timestamps (created_at, updated_at)
2. ✅ Postcode apart (postcode, gemeente)

### Fase 2 (Binnenkort):
3. ✅ Email veld
4. ✅ Soft deletes

### Fase 3 (Later):
5. ✅ Adres historie
6. ✅ Klant status
7. ✅ Contact historie
8. ✅ Tags/categorieën

## Migratie Strategie

1. **Backup maken** van huidige database
2. **Nieuwe kolommen toevoegen** met ALTER TABLE
3. **Data migreren** (bijv. postcode uit plaats halen)
4. **Code aanpassen** om nieuwe velden te gebruiken
5. **Testen** met echte data

## Code Aanpassingen Nodig

- `database.py`: Schema updates
- `repositories/customer_repository.py`: Nieuwe velden ondersteunen
- `business/customer_handler.py`: Validatie updates
- `ui/customer_form_enhanced.py`: UI updates voor nieuwe velden

