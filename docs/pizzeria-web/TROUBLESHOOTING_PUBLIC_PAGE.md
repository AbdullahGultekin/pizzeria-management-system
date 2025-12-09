# Troubleshooting - Publieke Menu Pagina

## Probleem: Pagina is leeg of niet zichtbaar

### Stap 1: Controleer of backend draait

```bash
# Terminal 1 - Backend
cd pizzeria-web/backend
source venv/bin/activate
python run.py
```

De backend moet draaien op: **http://localhost:8000**

Test of de backend werkt:
```bash
curl http://localhost:8000/api/v1/menu/public
```

### Stap 2: Controleer of frontend draait

```bash
# Terminal 2 - Frontend
cd pizzeria-web/frontend
npm run dev
```

De frontend moet draaien op: **http://localhost:5173** (of een andere poort)

### Stap 3: Controleer browser console

Open de browser developer tools (F12) en kijk naar:
- **Console tab**: Zijn er JavaScript errors?
- **Network tab**: Worden API calls gemaakt? Zijn er 404 of 500 errors?

### Stap 4: Controleer menu data

De backend moet menu data hebben. Controleer of menu items in de database staan:

```bash
cd pizzeria-web/backend
python -c "from app.core.database import SessionLocal; from app.models.menu import MenuItem; db = SessionLocal(); items = db.query(MenuItem).all(); print(f'Aantal items: {len(items)}')"
```

Als er geen items zijn, importeer het menu:
```bash
cd pizzeria-web/backend
python import_menu.py
```

### Stap 5: Controleer CORS instellingen

Zorg dat de backend CORS correct is geconfigureerd in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Stap 6: Controleer API URL

In `frontend/src/services/api.ts` moet de API URL correct zijn:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
```

### Stap 7: Test de publieke endpoints direct

Test of de publieke endpoints werken:
```bash
# Menu endpoint
curl http://localhost:8000/api/v1/menu/public

# Extras endpoint
curl http://localhost:8000/api/v1/extras/public
```

### Veelvoorkomende problemen:

1. **Backend niet gestart**: Start de backend eerst
2. **Menu data niet geïmporteerd**: Voer `import_menu.py` uit
3. **CORS errors**: Controleer CORS configuratie
4. **Verkeerde API URL**: Controleer `VITE_API_URL` in `.env` of gebruik default
5. **Database errors**: Controleer of database bestaat en toegankelijk is

### Debug stappen:

1. Open browser console (F12)
2. Ga naar Network tab
3. Refresh de pagina
4. Kijk welke requests falen
5. Check de error messages in de console

### Snelle test:

1. Ga naar: `http://localhost:5173/`
2. Je zou de menu pagina moeten zien
3. Als je een lege pagina ziet, check de browser console voor errors


