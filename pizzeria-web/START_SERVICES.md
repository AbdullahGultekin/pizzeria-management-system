# Services Starten - Quick Guide

## Probleem: ERR_CONNECTION_REFUSED

Dit betekent dat de backend of frontend niet draait. Hier is hoe je ze start:

## Stap 1: Backend Starten

Open een terminal en voer uit:

```bash
# Ga naar backend directory
cd pizzeria-web/backend

# Activeer virtual environment
source "/Users/abdullahgultekin/Cursor projects/Deskcomputer/.venv/bin/activate"

# Start backend
python run.py
```

Je zou moeten zien:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Backend draait nu op:** `http://localhost:8000`

## Stap 2: Frontend Starten

Open een **nieuwe terminal** en voer uit:

```bash
# Ga naar frontend directory
cd pizzeria-web/frontend

# Start frontend
npm run dev
```

Je zou moeten zien:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Frontend draait nu op:** `http://localhost:5173`

## Stap 3: Testen

1. Open browser: `http://localhost:5173`
2. Je zou de publieke menu pagina moeten zien

## Troubleshooting

### Backend start niet
- Check of poort 8000 vrij is: `lsof -ti:8000`
- Als poort bezet is: `lsof -ti:8000 | xargs kill -9`
- Check backend logs: `tail -f /tmp/backend.log`

### Frontend start niet
- Check of poort 5173 vrij is: `lsof -ti:5173`
- Als poort bezet is: `lsof -ti:5173 | xargs kill -9`
- Check frontend logs: `tail -f /tmp/frontend.log`
- Probeer: `npm install` als er dependency errors zijn

### Beide services starten in één keer

Je kunt ook een script maken om beide te starten. Maak `start_all.sh`:

```bash
#!/bin/bash

# Start backend
cd pizzeria-web/backend
source "/Users/abdullahgultekin/Cursor projects/Deskcomputer/.venv/bin/activate"
python run.py &
BACKEND_PID=$!

# Wacht even
sleep 3

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Druk Ctrl+C om beide te stoppen"

# Wacht op Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
```

Maak het uitvoerbaar:
```bash
chmod +x start_all.sh
./start_all.sh
```

## Snelle Commands

### Check of services draaien:
```bash
# Backend
curl http://localhost:8000/api/health

# Frontend
curl http://localhost:5173
```

### Stop alle services:
```bash
# Stop backend
lsof -ti:8000 | xargs kill -9

# Stop frontend
lsof -ti:5173 | xargs kill -9
```

### Check logs:
```bash
# Backend logs
tail -f /tmp/backend.log

# Frontend logs
tail -f /tmp/frontend.log
```


