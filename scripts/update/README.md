# Update Scripts

Deze folder bevat scripts voor het updaten van het Pizzeria Management System.

## Beschikbare Scripts

### `update_safe.bat` (Windows) ⭐ AANBEVOLEN
**Veilig update script dat lokale gegevens beschermt:**
1. Maakt automatisch backup van lokale data
2. Haalt laatste wijzigingen van GitHub op
3. Controleert en herstelt lokale gegevens indien nodig
4. Update Python dependencies
5. Optioneel: Start applicatie

**Gebruik:**
```bash
scripts\update\update_safe.bat
```

**Beschermt automatisch:**
- ✅ Database (pizzeria.db)
- ✅ Instellingen (settings.json)
- ✅ Log bestanden
- ✅ Backup bestanden

---

### `update.bat` (Windows)
Basis update script (zonder automatische data bescherming):
1. Laatste wijzigingen van GitHub haalt
2. Python dependencies update
3. Optioneel: Nieuwe .exe bouwt

**Gebruik:**
```bash
scripts\update\update.bat
```

**⚠️ Let op:** Dit script beschermt lokale gegevens niet automatisch. Gebruik `update_safe.bat` voor belangrijke updates.

---

## Handmatige Update

Zie `docs/UPDATE_GUIDE.md` voor algemene update instructies.
Zie `docs/VEILIG_UPDATE_GUIDE.md` voor gedetailleerde instructies over het beschermen van lokale gegevens.


