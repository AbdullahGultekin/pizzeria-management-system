# Quick Start Guide

## Snelle Start (Development)

### 1. Backend Starten

```bash
cd pizzeria-web/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python import_menu.py  # Eerste keer: importeer menu data
python run.py
```

✅ Backend draait op: `http://localhost:8000`

### 2. Frontend Starten

```bash
cd pizzeria-web/frontend
npm install
npm run dev
```

✅ Frontend draait op: `http://localhost:5173`

## Eerste Gebruik

### 1. Login
- Ga naar `http://localhost:5173/login`
- Default credentials (check `app/api/auth.py`):
  - Username: `admin`
  - Password: `admin` (wijzig in productie!)

### 2. Admin Dashboard
- Bekijk bestellingen
- Beheer menu
- Bekijk rapportages
- Configureer printer

### 3. Kassa Interface
- Selecteer klant
- Voeg producten toe
- Plaats bestelling (automatisch print)

### 4. Publieke Website
- Ga naar `http://localhost:5173/menu`
- Bekijk menu
- Plaats bestelling

## Belangrijke Endpoints

- **API Docs**: `http://localhost:8000/api/docs`
- **Health Check**: `http://localhost:8000/api/health`
- **Frontend**: `http://localhost:5173`

## Troubleshooting

### Backend start niet
```bash
# Check Python versie (moet 3.8+ zijn)
python --version

# Check dependencies
pip install -r requirements.txt
```

### Frontend start niet
```bash
# Check Node.js versie (moet 16+ zijn)
node --version

# Verwijder node_modules en installeer opnieuw
rm -rf node_modules package-lock.json
npm install
```

### Database errors
```bash
# Run menu import opnieuw
cd pizzeria-web/backend
python import_menu.py
```

### Printer werkt niet
1. Check printer is aangesloten
2. Ga naar Admin > Instellingen
3. Selecteer printer uit dropdown
4. Klik op "Opslaan"

## Volgende Stappen

1. **Configureer printer** in Admin > Instellingen
2. **Importeer menu data** als nog niet gedaan
3. **Test bestelling plaatsen** vanuit Kassa
4. **Test publieke website** door bestelling te plaatsen
5. **Check real-time updates** in Admin dashboard

## Productie Deployment

Zie `DEPLOYMENT_GUIDE.md` voor volledige deployment instructies.

## Features

Zie `FEATURES_OVERVIEW.md` voor volledige lijst van features.

## Support

- API Docs: `http://localhost:8000/api/docs`
- Check logs voor errors
- Check browser console voor frontend errors
