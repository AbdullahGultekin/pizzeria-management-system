# Setup Instructies - Pizzeria Web Application

## 🚀 Quick Start

### Stap 1: Backend Setup

```bash
# Ga naar backend directory
cd pizzeria-web/backend

# Maak virtual environment
python -m venv venv

# Activeer virtual environment
# Op macOS/Linux:
source venv/bin/activate
# Op Windows:
venv\Scripts\activate

# Installeer dependencies
pip install -r requirements.txt

# Maak .env file (kopieer van .env.example)
cp .env.example .env

# Start de server
python run.py
```

Backend draait nu op: **http://localhost:8000**
API Documentatie: **http://localhost:8000/api/docs**

### Stap 2: Test de API

Open je browser en ga naar:
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/health

### Stap 3: Test Login

Gebruik de API docs om te testen:

1. Ga naar `/api/v1/auth/login`
2. Klik op "Try it out"
3. Gebruik deze credentials:
   - **username**: `admin` of `kassa`
   - **password**: `admin123` of `kassa123`
4. Klik "Execute"
5. Je krijgt een JWT token terug

### Stap 4: Test Customer Endpoints

1. Kopieer de JWT token van de login response
2. Ga naar `/api/v1/customers`
3. Klik op "Authorize" (bovenaan de pagina)
4. Plak je token in het veld: `Bearer <jouw-token>`
5. Klik "Authorize"
6. Test de customer endpoints

## 📁 Project Structuur

```
pizzeria-web/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   │   ├── auth.py    # Authentication
│   │   │   └── customers.py
│   │   ├── core/          # Core config
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── dependencies.py
│   │   ├── models/        # Database models
│   │   │   ├── customer.py
│   │   │   ├── order.py
│   │   │   └── menu.py
│   │   └── schemas/       # Pydantic schemas
│   │       └── customer.py
│   ├── requirements.txt
│   ├── run.py
│   └── README.md
└── frontend/              # (Wordt later toegevoegd)
```

## 🔐 Default Credentials

**⚠️ BELANGRIJK: Verander deze in productie!**

- **Admin**: 
  - Username: `admin`
  - Password: `admin123`
  
- **Kassa**: 
  - Username: `kassa`
  - Password: `kassa123`

## 🛠️ Development

### Backend herstarten

```bash
# In backend directory
python run.py
```

De server heeft auto-reload, dus wijzigingen worden automatisch geladen.

### Database

De database wordt automatisch aangemaakt bij eerste start in `pizzeria.db`.

## 📝 Volgende Stappen

1. ✅ Backend is klaar en werkend
2. 🚧 Order API endpoints toevoegen
3. 🚧 Menu API endpoints toevoegen
4. 🚧 React frontend opzetten
5. 🚧 Printer integration

## ❓ Problemen?

### Port 8000 al in gebruik?

```bash
# Gebruik een andere port
uvicorn app.main:app --port 8001
```

### Dependencies niet geïnstalleerd?

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Database errors?

Verwijder `pizzeria.db` en start opnieuw - de database wordt automatisch aangemaakt.

## 🎯 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Customers
- `GET /api/v1/customers` - List customers
- `GET /api/v1/customers/{id}` - Get customer
- `POST /api/v1/customers` - Create customer
- `PUT /api/v1/customers/{id}` - Update customer
- `GET /api/v1/customers/phone/{phone}` - Get by phone

## 🔒 Security Features

- ✅ JWT Authentication
- ✅ Password hashing (bcrypt)
- ✅ Rate limiting
- ✅ CORS protection
- ✅ Security headers
- ✅ Input validation
- ✅ SQL injection prevention


