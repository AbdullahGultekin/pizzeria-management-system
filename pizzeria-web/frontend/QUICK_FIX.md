# Quick Fix - Lege Pagina

## Probleem: Alleen React Router Warnings

Als je alleen React Router warnings ziet maar geen andere console logs, betekent dit dat:

1. **De component wordt niet gemount** - Check of je ingelogd bent
2. **Er is een JavaScript error** - Check console voor rode errors
3. **De pagina laadt niet** - Check Network tab

## Stappen om te Debuggen

### Stap 1: Check of je ingelogd bent

1. Ga naar: http://localhost:3000
2. Zie je de login pagina?
3. Log in met: `kassa` / `kassa123`
4. Word je doorgestuurd naar `/kassa`?

### Stap 2: Check Browser Console

1. Open DevTools (F12)
2. Ga naar **Console** tab
3. **Filter op "Error"** (klik op error filter)
4. Zijn er rode errors?

### Stap 3: Check Network Tab

1. Ga naar **Network** tab
2. Refresh pagina (F5)
3. Zoek naar:
   - `/api/v1/menu` → Status?
   - `/api/v1/auth/me` → Status?

### Stap 4: Check React DevTools

1. Installeer React DevTools extensie
2. Open React DevTools tab
3. Check component tree
4. Zie je `KassaPage` component?

## Mogelijke Oplossingen

### Oplossing 1: Hard Refresh

```
Cmd+Shift+R (Mac) of Ctrl+Shift+R (Windows)
```

### Oplossing 2: Clear Cache

1. Open DevTools
2. Rechts klik op refresh knop
3. Select "Empty Cache and Hard Reload"

### Oplossing 3: Check Backend

```bash
# Test backend
curl http://localhost:8000/api/health

# Moet teruggeven: {"status":"healthy"}
```

### Oplossing 4: Restart Frontend

```bash
# Stop frontend (Ctrl+C)
cd pizzeria-web/frontend
npm run dev
```

## Wat te Zoeken in Console

**Goed (zou moeten zien):**
```
🚀 KassaPage mounted, loading menu...
📡 Fetching menu from API...
✅ Menu loaded successfully: {...}
📊 KassaPage state: {...}
```

**Slecht (probleem):**
```
❌ Error loading menu: ...
Cannot read property 'categories' of null
Module not found: ...
```

## Als Pagina Nog Steeds Leeg Is

1. **Screenshot van console** (alle errors)
2. **Screenshot van Network tab** (failed requests)
3. **Check of backend draait** (terminal logs)

Stuur deze info door!


