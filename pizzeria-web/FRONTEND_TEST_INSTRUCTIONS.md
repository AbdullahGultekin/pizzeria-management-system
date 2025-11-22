# Frontend Test Instructies

## 🚀 Quick Start

### Stap 1: Backend Starten

```bash
cd pizzeria-web/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Backend moet draaien op: **http://localhost:8000**

### Stap 2: Frontend Starten

Open een **nieuwe terminal**:

```bash
cd pizzeria-web/frontend
npm install
npm run dev
```

Frontend start op: **http://localhost:3000**

## ✅ Test Checklist

### 1. Login Testen

1. Open browser: http://localhost:3000
2. Je ziet de login pagina
3. Test met:
   - **Username**: `admin`
   - **Password**: `admin123`
4. Klik "Inloggen"
5. Je wordt doorgestuurd naar `/admin`

### 2. Kassa Interface Testen

1. Log uit (klik "Uitloggen")
2. Log in met:
   - **Username**: `kassa`
   - **Password**: `kassa123`
3. Je wordt doorgestuurd naar `/kassa`
4. Je ziet het menu (als backend werkt)

### 3. API Connectie Testen

1. Open browser console (F12)
2. Ga naar Network tab
3. Log in
4. Check of API calls worden gemaakt:
   - `/api/v1/auth/login` - Login
   - `/api/v1/menu` - Menu ophalen

### 4. Protected Routes Testen

1. Log uit
2. Probeer direct naar `/admin` te gaan
3. Je wordt doorgestuurd naar `/login`
4. Log in als `kassa`
5. Probeer naar `/admin` te gaan
6. Je wordt doorgestuurd naar `/kassa` (geen admin rechten)

## 🐛 Troubleshooting

### Frontend start niet

```bash
# Check Node.js versie (moet 18+ zijn)
node --version

# Verwijder node_modules en installeer opnieuw
rm -rf node_modules package-lock.json
npm install
```

### API calls falen

1. Check of backend draait: http://localhost:8000/api/health
2. Check browser console voor errors
3. Check CORS errors - backend moet CORS toestaan voor localhost:3000

### Login werkt niet

1. Check backend logs voor errors
2. Check of token wordt opgeslagen in localStorage
3. Open browser DevTools > Application > Local Storage
4. Check of `token` en `user` aanwezig zijn

### Menu laadt niet

1. Check backend: http://localhost:8000/api/v1/menu
2. Check of je ingelogd bent (token in localStorage)
3. Check browser console voor errors

## 📝 Test Scenarios

### Scenario 1: Complete Flow

1. ✅ Start backend
2. ✅ Start frontend
3. ✅ Log in als admin
4. ✅ Navigeer naar kassa
5. ✅ Log uit
6. ✅ Log in als kassa
7. ✅ Check menu wordt geladen

### Scenario 2: Error Handling

1. ✅ Stop backend
2. ✅ Probeer in te loggen
3. ✅ Check error message wordt getoond
4. ✅ Start backend opnieuw
5. ✅ Log in opnieuw

### Scenario 3: Token Expiry

1. ✅ Log in
2. ✅ Verwijder token uit localStorage
3. ✅ Probeer API call te maken
4. ✅ Check of je wordt doorgestuurd naar login

## 🎯 Wat te Testen

- [ ] Login functionaliteit
- [ ] Logout functionaliteit
- [ ] Protected routes
- [ ] Role-based access
- [ ] Menu API call
- [ ] Error handling
- [ ] Token storage
- [ ] Auto-redirect na login
- [ ] Navigation tussen pages

## 📊 Expected Behavior

### Login Page
- Toont login formulier
- Toont test accounts info
- Toont error bij foutieve login
- Redirect naar juiste pagina na login

### Kassa Page
- Toont menu categories
- Toont menu items count
- Toont logout button
- Werkt alleen voor kassa/admin users

### Admin Page
- Toont admin dashboard
- Toont navigatie naar kassa
- Toont logout button
- Werkt alleen voor admin users

## 🔍 Debug Tips

1. **Browser Console**: Check voor JavaScript errors
2. **Network Tab**: Check API calls en responses
3. **Local Storage**: Check token en user data
4. **Backend Logs**: Check server-side errors
5. **React DevTools**: Check component state

## ✅ Success Criteria

Frontend werkt correct als:
- ✅ Login/logout werkt
- ✅ Menu wordt geladen van API
- ✅ Protected routes werken
- ✅ Role-based access werkt
- ✅ Geen console errors
- ✅ API calls zijn succesvol


