# Debug Guide - Lege Pagina

## Probleem: Lege Webpagina

Als je een lege pagina ziet, volg deze stappen:

### Stap 1: Check Browser Console

1. Open browser (F12 of Cmd+Option+I)
2. Ga naar "Console" tab
3. Kijk voor rode errors

**Veelvoorkomende errors:**
- `Cannot read property 'categories' of null` → Menu data is null
- `Module not found` → Import probleem
- `Network Error` → Backend niet bereikbaar

### Stap 2: Check Network Tab

1. Ga naar "Network" tab in DevTools
2. Refresh pagina (F5)
3. Check API calls:
   - `/api/v1/menu` → Moet 200 OK zijn
   - `/api/v1/auth/me` → Moet 200 OK zijn

### Stap 3: Check Backend

```bash
# Check of backend draait
curl http://localhost:8000/api/health

# Check menu endpoint
curl http://localhost:8000/api/v1/menu \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Stap 4: Check Frontend Logs

In terminal waar frontend draait, kijk voor:
- Compilation errors
- Runtime errors
- Warnings

## Oplossingen

### Oplossing 1: Menu is Leeg

Als menu endpoint leeg terugkomt:
1. Log in als admin
2. Voeg menu items toe via admin dashboard
3. Of voeg direct toe via database

### Oplossing 2: Import Errors

```bash
cd pizzeria-web/frontend
rm -rf node_modules
npm install
npm run dev
```

### Oplossing 3: Backend Errors

```bash
cd pizzeria-web/backend
# Check logs in terminal
# Restart backend
python run.py
```

### Oplossing 4: CORS Errors

Check of backend CORS correct is geconfigureerd:
- `BACKEND_CORS_ORIGINS` moet `http://localhost:3000` bevatten

## Debug Checklist

- [ ] Browser console heeft geen errors
- [ ] Network tab toont succesvolle API calls
- [ ] Backend draait op port 8000
- [ ] Frontend draait op port 3000
- [ ] Menu endpoint retourneert data
- [ ] Authentication werkt
- [ ] Component imports zijn correct

## Test Commands

```bash
# Test backend health
curl http://localhost:8000/api/health

# Test menu (na login)
curl http://localhost:8000/api/v1/menu \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check frontend build
cd pizzeria-web/frontend
npm run build
```

## Veelvoorkomende Problemen

### 1. Menu is null/undefined
**Oorzaak:** API retourneert geen data
**Oplossing:** Check backend, voeg menu items toe

### 2. Component crashes
**Oorzaak:** Missing null checks
**Oplossing:** Error boundary toegevoegd, check console

### 3. Styling issues
**Oorzaak:** Material-UI niet geladen
**Oplossing:** Check imports, reinstall dependencies

### 4. API errors
**Oorzaak:** Backend niet bereikbaar of CORS
**Oplossing:** Check backend status, CORS config


