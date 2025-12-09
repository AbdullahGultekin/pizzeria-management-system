# Testing Steps - Lege Pagina Oplossen

## Stap 1: Check Browser Console

1. Open browser DevTools (F12 of Cmd+Option+I)
2. Ga naar **Console** tab
3. Kijk voor **rode errors**
4. Kopieer eventuele errors

**Wat te zoeken:**
- `Cannot read property 'categories' of null`
- `Module not found`
- `Network Error`
- `401 Unauthorized`

## Stap 2: Check Network Requests

1. Ga naar **Network** tab
2. Refresh pagina (F5)
3. Check deze requests:
   - `GET /api/v1/menu` → Status moet 200 zijn
   - `GET /api/v1/auth/me` → Status moet 200 zijn

**Als requests falen:**
- 401 → Token probleem, log opnieuw in
- 404 → Backend endpoint bestaat niet
- 500 → Backend error, check backend logs
- CORS error → Backend CORS config checken

## Stap 3: Check Backend

```bash
# In backend terminal, check logs
# Je zou moeten zien:
# INFO: GET /api/v1/menu HTTP/1.1" 200 OK
```

## Stap 4: Test Menu Endpoint Direct

```bash
# Test menu endpoint (vervang TOKEN met je JWT token)
curl http://localhost:8000/api/v1/menu \
  -H "Authorization: Bearer TOKEN"
```

**Verwacht resultaat:**
```json
{
  "categories": [...],
  "items": [...]
}
```

**Als leeg:**
```json
{
  "categories": [],
  "items": []
}
```
→ Menu is leeg, voeg items toe via admin

## Stap 5: Check Frontend Console Logs

In browser console, je zou moeten zien:
```
Menu loaded: {categories: [...], items: [...]}
KassaPage state: {menu: {...}, loading: false, ...}
```

## Oplossingen

### Probleem: Menu is Leeg (categories: [], items: [])

**Oplossing:** Voeg menu items toe

1. Log in als admin
2. Ga naar admin dashboard
3. Voeg menu items toe
4. Of voeg direct toe via database/API

### Probleem: Network Error

**Oplossing:** Backend niet bereikbaar

1. Check of backend draait: `curl http://localhost:8000/api/health`
2. Check backend logs voor errors
3. Restart backend: `python run.py`

### Probleem: 401 Unauthorized

**Oplossing:** Token probleem

1. Log uit
2. Log opnieuw in
3. Check localStorage voor token

### Probleem: Component Crashes

**Oplossing:** Error boundary toegevoegd

1. Check console voor error details
2. Error boundary zou error moeten tonen
3. Check component imports

## Quick Fixes

### Fix 1: Refresh Everything

```bash
# Stop beide servers (Ctrl+C)
# Restart backend
cd pizzeria-web/backend
python run.py

# Restart frontend (nieuwe terminal)
cd pizzeria-web/frontend
npm run dev
```

### Fix 2: Clear Browser Cache

1. Hard refresh: Cmd+Shift+R (Mac) of Ctrl+Shift+R (Windows)
2. Of clear cache in browser settings

### Fix 3: Check Imports

```bash
cd pizzeria-web/frontend
# Check voor compilation errors
npm run build
```

## Debug Output

De pagina logt nu debug info naar console:
- Menu data
- Component state
- API responses

**Check browser console voor deze logs!**

## Success Criteria

Pagina werkt als:
- ✅ Geen errors in console
- ✅ Menu wordt geladen (check console log)
- ✅ UI elementen zijn zichtbaar
- ✅ API calls zijn succesvol (200 OK)

## Als Nog Steeds Leeg

1. **Check console logs** - Wat staat er?
2. **Check network tab** - Welke requests falen?
3. **Check backend logs** - Zijn er errors?
4. **Test API direct** - Werkt menu endpoint?

Stuur me de console errors en network tab screenshots!


