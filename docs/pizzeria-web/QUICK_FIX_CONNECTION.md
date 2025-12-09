# Quick Fix: ERR_CONNECTION_REFUSED

## Status Check

✅ **Backend draait** op `http://localhost:8000`
❌ **Frontend moet nog gestart worden**

## Oplossing

### Optie 1: Frontend Starten (Aanbevolen)

Open een **nieuwe terminal** en voer uit:

```bash
cd "/Users/abdullahgultekin/Cursor projects/Deskcomputer/pizzeria-web/frontend"
npm run dev
```

Wacht tot je ziet:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

Open dan in je browser: **http://localhost:5173**

### Optie 2: Check Frontend Logs

Als frontend niet start, check de logs:

```bash
tail -50 /tmp/frontend.log
```

### Optie 3: Herstart Alles

Als er problemen zijn, stop alles en start opnieuw:

```bash
# Stop alles
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

# Start backend (Terminal 1)
cd pizzeria-web/backend
source "/Users/abdullahgultekin/Cursor projects/Deskcomputer/.venv/bin/activate"
python run.py

# Start frontend (Terminal 2 - NIEUWE TERMINAL)
cd pizzeria-web/frontend
npm run dev
```

## Welke URL moet je gebruiken?

- **Publieke Menu:** http://localhost:5173/ of http://localhost:5173/menu
- **Admin Dashboard:** http://localhost:5173/admin
- **Kassa:** http://localhost:5173/kassa
- **Status Check:** http://localhost:5173/status

## Als het nog steeds niet werkt

1. **Check of frontend draait:**
   ```bash
   lsof -ti:5173
   ```
   Als dit niets teruggeeft, draait frontend niet.

2. **Check frontend errors:**
   ```bash
   cd pizzeria-web/frontend
   npm run dev
   ```
   Kijk naar errors in de terminal.

3. **Check backend:**
   ```bash
   curl http://localhost:8000/api/health
   ```
   Moet `{"status":"healthy"}` teruggeven.

4. **Check poorten:**
   ```bash
   lsof -i:8000  # Backend
   lsof -i:5173  # Frontend
   ```

## Snelle Test

Test of alles werkt:

```bash
# Test backend
curl http://localhost:8000/api/health

# Test frontend (als het draait)
curl http://localhost:5173
```

Beide moeten een response geven (geen ERR_CONNECTION_REFUSED).


