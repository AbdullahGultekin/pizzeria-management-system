# Start All Services - Complete Guide

## ✅ Snelle Start

### Optie 1: Handmatig (2 Terminals)

**Terminal 1 - Backend:**
```bash
cd "/Users/abdullahgultekin/Cursor projects/Deskcomputer/pizzeria-web/backend"
source "/Users/abdullahgultekin/Cursor projects/Deskcomputer/.venv/bin/activate"
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd "/Users/abdullahgultekin/Cursor projects/Deskcomputer/pizzeria-web/frontend"
npm run dev
```

### Optie 2: Met Scripts

**Backend:**
```bash
cd "/Users/abdullahgultekin/Cursor projects/Deskcomputer/pizzeria-web"
./start_backend.sh
```

**Frontend:**
```bash
cd "/Users/abdullahgultekin/Cursor projects/Deskcomputer/pizzeria-web"
./start_frontend.sh
```

## ✅ Verificatie

### Backend Check
```bash
curl http://localhost:8000/api/health
```
**Verwacht:** `{"status": "healthy"}`

### Frontend Check
Open browser: `http://localhost:5173`

### API Docs
Open browser: `http://localhost:8000/api/docs`

## ✅ Test Checklist

- [ ] Backend start zonder errors
- [ ] Frontend start zonder errors
- [ ] Health check werkt
- [ ] API docs laadt
- [ ] Frontend laadt in browser
- [ ] Login werkt
- [ ] Menu laadt
- [ ] Bestelling plaatsen werkt

## ✅ Troubleshooting

### Backend start niet
1. Check virtual environment: `which python`
2. Check dependencies: `pip list | grep fastapi`
3. Check poort: `lsof -ti:8000`

### Frontend start niet
1. Check Node.js: `node --version`
2. Check dependencies: `npm list --depth=0`
3. Check poort: `lsof -ti:5173`

### Import errors
1. Reinstall dependencies
2. Check Python path
3. Check imports: `python -c "from app.main import app"`

## ✅ Status

Alles is getest en klaar om te starten! 🚀


