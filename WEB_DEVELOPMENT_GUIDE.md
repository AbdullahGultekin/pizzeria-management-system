# Web Development Guide - Pizzeria Management System

## Overzicht

Dit document beschrijft stap-voor-stap hoe we de desktop applicatie omzetten naar een moderne web applicatie.

## 🎯 Doelstellingen

- **Bereikbaarheid**: Toegankelijk vanaf elke computer/tablet/telefoon
- **Multi-user**: Meerdere gebruikers tegelijk
- **Real-time updates**: Live updates voor bestellingen
- **Mobiel vriendelijk**: Werkt op tablets voor kassa gebruik
- **Moderne UI**: Responsive en gebruiksvriendelijk

---

## 📋 Tech Stack Opties

### Optie 1: Python Full-Stack (Aanbevolen voor jouw situatie)

**Voordelen:**
- ✅ Hergebruik van bestaande Python code
- ✅ Zelfde database (SQLite/PostgreSQL)
- ✅ Bekende taal voor jou
- ✅ Snel te ontwikkelen

**Stack:**
- **Backend**: FastAPI of Flask
- **Frontend**: React of Vue.js (of Jinja2 templates)
- **Database**: SQLite (ontwikkeling) → PostgreSQL (productie)
- **Real-time**: WebSockets (Socket.IO of native)

**Wanneer kiezen**: Als je Python code wilt hergebruiken en snel wilt starten.

---

### Optie 2: Modern JavaScript Stack

**Voordelen:**
- ✅ Zeer populair en veel resources
- ✅ Uitstekende real-time mogelijkheden
- ✅ Grote community

**Stack:**
- **Backend**: Node.js + Express of NestJS
- **Frontend**: React of Vue.js
- **Database**: PostgreSQL
- **Real-time**: Socket.IO

**Wanneer kiezen**: Als je een moderne, schaalbare oplossing wilt.

---

### Optie 3: Django Full-Stack

**Voordelen:**
- ✅ Alles-in-één Python framework
- ✅ Admin panel ingebouwd
- ✅ Sterke security features
- ✅ ORM voor database

**Stack:**
- **Backend**: Django + Django REST Framework
- **Frontend**: React of Django Templates
- **Database**: PostgreSQL
- **Real-time**: Django Channels

**Wanneer kiezen**: Als je een complete, enterprise-ready oplossing wilt.

---

## 🏆 Mijn Aanbeveling: **Optie 1 - FastAPI + React**

### Waarom?

1. **Hergebruik code**: Je bestaande Python modules kunnen grotendeels blijven
2. **Snel**: FastAPI is zeer snel en modern
3. **API-first**: Makkelijk om later mobiele apps toe te voegen
4. **Type safety**: FastAPI heeft automatische type checking
5. **Documentatie**: Automatische API documentatie

---

## 📐 Architectuur Overzicht

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  - Kassa Interface (Tablet-friendly)                    │
│  - Admin Dashboard                                       │
│  - Real-time Order Updates                              │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼────────────────────────────────────┐
│              Backend API (FastAPI)                       │
│  - REST API Endpoints                                    │
│  - WebSocket voor real-time                              │
│  - Authentication & Authorization                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Database Layer                              │
│  - SQLite (ontwikkeling)                                 │
│  - PostgreSQL (productie)                                │
│  - Hergebruik bestaande schema                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Stap-voor-Stap Plan

### Fase 1: Project Setup (Week 1)

#### Stap 1.1: Backend Setup
```bash
# Maak nieuwe directory structuur
mkdir pizzeria-web
cd pizzeria-web
mkdir backend frontend

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy python-multipart
pip install python-jose[cryptography] passlib[bcrypt]  # Auth
pip install websockets  # Real-time
```

#### Stap 1.2: Frontend Setup
```bash
cd ../frontend
npx create-react-app . --template typescript
# Of met Vite (sneller):
npm create vite@latest . -- --template react-ts

npm install axios  # HTTP client
npm install socket.io-client  # WebSocket client
npm install react-router-dom  # Routing
npm install @mui/material @emotion/react @emotion/styled  # UI library
```

#### Stap 1.3: Database Migratie
- SQLite schema kopiëren
- SQLAlchemy models maken
- Database migratie scripts

---

### Fase 2: Backend Development (Week 2-3)

#### Stap 2.1: API Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuratie
│   ├── database.py          # Database connectie
│   ├── models/              # SQLAlchemy models
│   │   ├── customer.py
│   │   ├── order.py
│   │   └── menu.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── customer.py
│   │   ├── order.py
│   │   └── menu.py
│   ├── api/                 # API routes
│   │   ├── customers.py
│   │   ├── orders.py
│   │   ├── menu.py
│   │   └── auth.py
│   ├── services/            # Business logic
│   │   ├── order_service.py
│   │   ├── customer_service.py
│   │   └── print_service.py
│   └── websocket/           # WebSocket handlers
│       └── order_updates.py
```

#### Stap 2.2: Core Endpoints
- `GET /api/customers` - Lijst klanten
- `POST /api/customers` - Nieuwe klant
- `GET /api/orders` - Lijst bestellingen
- `POST /api/orders` - Nieuwe bestelling
- `GET /api/menu` - Menu items
- `POST /api/orders/{id}/print` - Print bon

#### Stap 2.3: Real-time Updates
- WebSocket endpoint voor live order updates
- Notificaties voor nieuwe bestellingen

---

### Fase 3: Frontend Development (Week 4-5)

#### Stap 3.1: Component Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── Kassa/
│   │   │   ├── OrderForm.tsx
│   │   │   ├── MenuGrid.tsx
│   │   │   └── CustomerForm.tsx
│   │   ├── Admin/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── OrderHistory.tsx
│   │   │   └── Reports.tsx
│   │   └── Shared/
│   │       ├── Layout.tsx
│   │       └── Navigation.tsx
│   ├── services/
│   │   ├── api.ts           # API client
│   │   └── websocket.ts     # WebSocket client
│   ├── hooks/
│   │   ├── useOrders.ts
│   │   └── useCustomers.ts
│   └── pages/
│       ├── KassaPage.tsx
│       └── AdminPage.tsx
```

#### Stap 3.2: Kassa Interface
- Responsive menu grid
- Customer search/autocomplete
- Order cart
- Print functionaliteit

#### Stap 3.3: Admin Interface
- Dashboard met statistieken
- Order history met filters
- Reports generatie
- Menu management

---

### Fase 4: Integratie & Testing (Week 6)

#### Stap 4.1: Printer Integratie
- Web-based print API
- ESC/POS via backend
- Print preview

#### Stap 4.2: Authentication
- Login systeem
- Role-based access (Kassa vs Admin)
- Session management

#### Stap 4.3: Testing
- API tests
- Frontend component tests
- Integration tests

---

## 🛠️ Technische Details

### Backend: FastAPI Structuur

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Pizzeria Management API")

# CORS voor frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Pizzeria Management API"}

# Import routes
from app.api import customers, orders, menu
app.include_router(customers.router, prefix="/api/customers")
app.include_router(orders.router, prefix="/api/orders")
app.include_router(menu.router, prefix="/api/menu")
```

### Frontend: React Component Voorbeeld

```typescript
// frontend/src/components/Kassa/OrderForm.tsx
import React, { useState } from 'react';
import { useOrders } from '../../hooks/useOrders';

export const OrderForm: React.FC = () => {
  const { createOrder } = useOrders();
  const [customer, setCustomer] = useState(null);
  
  const handleSubmit = async () => {
    await createOrder({
      customerId: customer.id,
      items: cartItems,
    });
  };
  
  return (
    <div>
      {/* Order form UI */}
    </div>
  );
};
```

---

## 📦 Dependencies Overzicht

### Backend (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
websockets==12.0
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "socket.io-client": "^4.6.1",
    "@mui/material": "^5.14.20",
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0"
  }
}
```

---

## 🔐 Security Overwegingen

1. **Authentication**: JWT tokens
2. **Authorization**: Role-based (Kassa/Admin)
3. **Input Validation**: Pydantic schemas
4. **SQL Injection**: SQLAlchemy ORM
5. **CORS**: Configured voor specifieke origins
6. **HTTPS**: Verplicht in productie

---

## 🚢 Deployment Opties

### Optie 1: VPS (DigitalOcean, Hetzner)
- Backend: Gunicorn/Uvicorn
- Frontend: Nginx
- Database: PostgreSQL
- Kosten: ~€10-20/maand

### Optie 2: Cloud Platforms
- **Heroku**: Easy deployment
- **Railway**: Modern, goedkoop
- **Render**: Free tier beschikbaar
- **AWS/GCP**: Enterprise oplossing

### Optie 3: Docker
- Containerize backend en frontend
- Docker Compose voor lokale ontwikkeling
- Makkelijk te deployen

---

## 📊 Migratie Strategie

### Stap 1: Parallel Draaien
- Desktop app blijft werken
- Web app naast desktop
- Database gedeeld (read-only voor web)

### Stap 2: Geleidelijke Overgang
- Nieuwe features alleen in web
- Bestaande features migreren
- Training voor gebruikers

### Stap 3: Volledige Overgang
- Desktop app deprecated
- Alle functionaliteit in web
- Database volledig gemigreerd

---

## 🎨 UI/UX Overwegingen

### Kassa Interface (Tablet)
- Grote knoppen
- Touch-friendly
- Snelle navigatie
- Offline support (PWA)

### Admin Interface (Desktop)
- Dashboard met statistieken
- Data visualisatie
- Export functionaliteit
- Bulk operaties

---

## 📝 Volgende Stappen

1. **Beslissing maken**: Welke tech stack?
2. **Project setup**: Directory structuur aanmaken
3. **Database migratie**: Schema converteren
4. **Eerste API endpoint**: Test endpoint maken
5. **Eerste frontend component**: Basis layout

---

## ❓ Veelgestelde Vragen

**Q: Moeten we alles opnieuw bouwen?**  
A: Nee, veel business logic kan hergebruikt worden. Alleen UI en data access laag moet opnieuw.

**Q: Kan de desktop app blijven werken?**  
A: Ja, we kunnen beide parallel laten draaien tijdens migratie.

**Q: Hoe lang duurt het?**  
A: Met 1 developer: 6-8 weken voor basis functionaliteit. Volledige migratie: 3-4 maanden.

**Q: Wat kost hosting?**  
A: Vanaf €10/maand voor een VPS. Cloud platforms hebben vaak free tiers.

**Q: Moeten we een nieuwe database?**  
A: SQLite kan blijven voor ontwikkeling. Voor productie raden we PostgreSQL aan.

---

## 🎯 Conclusie

**Aanbevolen aanpak:**
1. Start met **FastAPI + React**
2. Gebruik **SQLite** voor ontwikkeling
3. Migreer naar **PostgreSQL** voor productie
4. Implementeer **WebSockets** voor real-time
5. Deploy op **Railway** of **DigitalOcean**

**Voordelen:**
- ✅ Snel te ontwikkelen
- ✅ Hergebruik van Python code
- ✅ Moderne, schaalbare oplossing
- ✅ Goede developer experience

Wil je dat ik begin met het opzetten van de project structuur?


