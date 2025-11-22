# Test Startup - Verificatie

## ✅ Backend Test

### Import Test
```bash
cd pizzeria-web/backend
python -c "from app.main import app; print('✅ Backend imports OK')"
```

### Start Test
```bash
cd pizzeria-web/backend
python run.py
# Druk Ctrl+C na 5 seconden om te testen
```

**Verwachte output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## ✅ Frontend Test

### Build Test
```bash
cd pizzeria-web/frontend
npm run build
```

**Verwachte output:**
```
✓ built in XXXms
```

### Dev Server Test
```bash
cd pizzeria-web/frontend
npm run dev
# Druk Ctrl+C na 5 seconden om te testen
```

**Verwachte output:**
```
  VITE v5.x.x  ready in xxx ms
  ➜  Local:   http://localhost:5173/
```

## ✅ Quick Start Scripts

### Backend Starten
```bash
./pizzeria-web/start_backend.sh
```

### Frontend Starten
```bash
./pizzeria-web/start_frontend.sh
```

## ✅ Health Check

### Backend Health
```bash
curl http://localhost:8000/api/health
```

**Verwachte response:**
```json
{"status": "healthy"}
```

### Frontend Check
```bash
curl http://localhost:5173
```

**Verwachte response:**
HTML pagina (status 200)

## ✅ API Endpoints Test

### Test Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

**Verwachte response:**
```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

### Test Menu (Public)
```bash
curl http://localhost:8000/api/v1/menu/public
```

**Verwachte response:**
```json
{
  "categories": [...],
  "items": [...]
}
```

## ✅ Frontend Routes Test

1. **Login**: `http://localhost:5173/login`
2. **Kassa**: `http://localhost:5173/kassa`
3. **Admin**: `http://localhost:5173/admin`
4. **Publiek Menu**: `http://localhost:5173/menu`
5. **Order Status**: `http://localhost:5173/status`

## ✅ Database Check

```bash
cd pizzeria-web/backend
python -c "
from app.core.database import SessionLocal, engine
from app.models import Order, Customer, MenuItem
print('✅ Database connection OK')
"
```

## Troubleshooting

### Backend start niet
1. Check Python versie: `python --version` (moet 3.8+ zijn)
2. Check dependencies: `pip list | grep fastapi`
3. Check poort 8000: `lsof -ti:8000`

### Frontend start niet
1. Check Node.js: `node --version` (moet 16+ zijn)
2. Check dependencies: `npm list --depth=0`
3. Check poort 5173: `lsof -ti:5173`

### Import errors
1. Check virtual environment: `which python`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check imports: `python -c "from app.main import app"`

## Status

✅ Backend imports: OK
✅ Frontend build: OK
✅ Quick start scripts: OK
✅ Health checks: OK

Alles is klaar om te starten!


