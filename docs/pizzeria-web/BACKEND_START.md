# Backend Start Instructies

## Probleem opgelost

De dependencies zijn geïnstalleerd. De backend kan nu worden gestart.

## Backend starten

```bash
# Activeer virtual environment
source "/Users/abdullahgultekin/Cursor projects/Deskcomputer/.venv/bin/activate"

# Ga naar backend directory
cd pizzeria-web/backend

# Start backend
python run.py
```

De backend zou nu moeten draaien op: **http://localhost:8000**

## Testen

1. **Health check**:
   ```bash
   curl http://localhost:8000/api/health
   ```
   Moet teruggeven: `{"status":"healthy"}`

2. **Public menu endpoint**:
   ```bash
   curl http://localhost:8000/api/v1/menu/public
   ```
   Moet JSON data teruggeven met categories en items.

## Frontend starten

In een **nieuwe terminal**:

```bash
cd pizzeria-web/frontend
npm run dev
```

De frontend zou moeten draaien op: **http://localhost:5173** (of een andere poort)

## Publieke menu pagina

Open in je browser:
- `http://localhost:5173/` of `http://localhost:5173/menu`

Je zou nu de menu pagina moeten zien met alle producten!

## Als er nog problemen zijn

1. Check of de backend draait: `curl http://localhost:8000/api/health`
2. Check backend logs in de terminal waar je `python run.py` hebt gestart
3. Check browser console (F12) voor frontend errors
4. Check Network tab in browser voor API call errors


