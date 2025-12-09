# 🔍 Troubleshooting Login Probleem

## Stap 1: Controleer of Backend Draait

**De backend server moet draaien op poort 8000.**

### Check of backend draait:
```bash
# In een terminal, controleer of poort 8000 in gebruik is:
lsof -i :8000
```

### Als backend NIET draait, start deze:
```bash
cd "/Users/abdullahgultekin/Cursor projects/Deskcomputer/pizzeria-web/backend"
source venv/bin/activate
python run.py
```

Je zou moeten zien:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Stap 2: Test Backend Direct

Open in browser: http://localhost:8000

Je zou moeten zien:
```json
{
  "message": "Pizzeria Management System API",
  "version": "1.0.0",
  "docs": "/api/docs"
}
```

---

## Stap 3: Test Login Endpoint Direct

In een nieuwe terminal:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Verwacht resultaat:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "role": "admin"
  }
}
```

**Als dit werkt:** Het probleem zit in de frontend-backend verbinding.

**Als dit NIET werkt:** Het probleem zit in de backend authenticatie.

---

## Stap 4: Controleer Browser Console

1. Open http://localhost:3000
2. Druk op `F12` of `Cmd+Option+I` (Mac) om Developer Tools te openen
3. Ga naar de "Console" tab
4. Probeer in te loggen
5. Kijk naar error messages

**Veelvoorkomende errors:**
- `Network Error` → Backend draait niet of verkeerde URL
- `CORS error` → CORS configuratie probleem
- `401 Unauthorized` → Verkeerde credentials of password hashing probleem
- `500 Internal Server Error` → Backend error (check backend logs)

---

## Stap 5: Controleer Frontend API URL

De frontend moet verbinden met: `http://localhost:8000/api/v1`

Check in browser:
1. Open Developer Tools (F12)
2. Ga naar "Network" tab
3. Probeer in te loggen
4. Kijk naar de request URL

**Verwacht:** `POST http://localhost:8000/api/v1/auth/login`

---

## Stap 6: Controleer Backend Logs

In de terminal waar de backend draait, kijk naar logs wanneer je probeert in te loggen.

**Verwacht:**
```
INFO:     127.0.0.1:xxxxx - "POST /api/v1/auth/login HTTP/1.1" 200 OK
```

**Als je ziet:**
```
INFO:     127.0.0.1:xxxxx - "POST /api/v1/auth/login HTTP/1.1" 401 UNAUTHORIZED
```
→ Verkeerde credentials of password hashing probleem

```
INFO:     127.0.0.1:xxxxx - "POST /api/v1/auth/login HTTP/1.1" 500 INTERNAL SERVER ERROR
```
→ Backend error (check de error message in de logs)

---

## Mogelijke Oplossingen

### Probleem: Backend draait niet
**Oplossing:** Start de backend server (zie Stap 1)

### Probleem: CORS Error
**Oplossing:** Check `backend/app/core/config.py` - `BACKEND_CORS_ORIGINS` moet `http://localhost:3000` bevatten

### Probleem: Password Hashing Error
**Oplossing:** 
```bash
cd backend
source venv/bin/activate
pip install bcrypt==4.0.1
# Herstart backend
```

### Probleem: Verkeerde API URL
**Oplossing:** Check `frontend/src/api/client.ts` - `API_BASE_URL` moet `http://localhost:8000/api/v1` zijn

---

## Test Credentials

- **Username:** `admin`
- **Password:** `admin123`

Of:
- **Username:** `kassa`
- **Password:** `kassa123`

