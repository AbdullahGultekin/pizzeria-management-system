# Opstart Commando's

## Backend Starten

### Terminal 1 - Backend
```bash
# Navigeer naar de backend directory
cd "/Users/abdullahgultekin/Cursor projects/Deskcomputer/pizzeria-web/backend"

# Activeer virtual environment (als je er een gebruikt)
source venv/bin/activate

# Start de backend server
python run.py
```

De backend draait op: **http://localhost:8000**
- API docs: http://localhost:8000/docs
- Publieke menu endpoint: http://localhost:8000/api/v1/menu/public

---

## Frontend Starten

### Terminal 2 - Frontend
```bash
# Navigeer naar de frontend directory
cd "/Users/abdullahgultekin/Cursor projects/Deskcomputer/pizzeria-web/frontend"

# Installeer dependencies (alleen eerste keer of na updates)
npm install

# Start de development server
npm run dev
```

De frontend draait op: **http://localhost:5173** (of een andere poort als 5173 bezet is)

---

## Snelle Start (Beide in één keer)

### Option 1: Twee aparte terminals
**Terminal 1:**
```bash
cd "/Users/abdullahgultekin/Cursor projects/Deskcomputer/pizzeria-web/backend" && source venv/bin/activate && python run.py
```

**Terminal 2:**
```bash
cd "/Users/abdullahgultekin/Cursor projects/Deskcomputer/pizzeria-web/frontend" && npm run dev
```

### Option 2: Met background process (macOS/Linux)
```bash
# Start backend in achtergrond
cd "/Users/abdullahgultekin/Cursor projects/Deskcomputer/pizzeria-web/backend" && source venv/bin/activate && python run.py &

# Start frontend
cd "/Users/abdullahgultekin/Cursor projects/Deskcomputer/pizzeria-web/frontend" && npm run dev
```

---

## Stoppen

- **Backend**: Druk op `Ctrl+C` in de backend terminal
- **Frontend**: Druk op `Ctrl+C` in de frontend terminal

---

## Troubleshooting

### Backend start niet:
1. Controleer of alle dependencies geïnstalleerd zijn:
   ```bash
   cd pizzeria-web/backend
   pip install -r requirements.txt
   ```

2. Controleer of poort 8000 vrij is:
   ```bash
   lsof -i :8000
   ```

### Frontend start niet:
1. Controleer of node_modules geïnstalleerd zijn:
   ```bash
   cd pizzeria-web/frontend
   npm install
   ```

2. Controleer of poort 5173 vrij is:
   ```bash
   lsof -i :5173
   ```

### Database errors:
- Zorg dat de database bestaat: `pizzeria-web/backend/pizzeria.db`
- Als de database niet bestaat, wordt deze automatisch aangemaakt bij eerste start


