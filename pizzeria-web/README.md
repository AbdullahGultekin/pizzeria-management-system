# Pizzeria Management System - Web Application

Moderne web applicatie voor pizzeria management met FastAPI backend en React frontend.

## Project Structuur

```
pizzeria-web/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Configuration
│   │   ├── models/   # Database models
│   │   ├── schemas/  # Pydantic schemas
│   │   └── services/ # Business logic
│   └── requirements.txt
└── frontend/         # React frontend (to be created)
```

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Backend draait op: http://localhost:8000
API docs: http://localhost:8000/api/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend draait op: http://localhost:3000

## Features

### ✅ Geïmplementeerd
- FastAPI backend setup
- Database models (Customer, Order, Menu)
- Authentication (JWT)
- Customer API endpoints
- Security features (rate limiting, CORS, headers)
- Input validation (Pydantic)

### 🚧 In ontwikkeling
- Order API endpoints
- Menu API endpoints
- WebSocket voor real-time updates
- React frontend
- Printer integration

## Security

- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ Rate limiting
- ✅ CORS protection
- ✅ Security headers
- ✅ Input validation & sanitization
- ✅ SQL injection prevention (ORM)

## Development

Zie individuele README files:
- `backend/README.md` - Backend setup
- `frontend/README.md` - Frontend setup (coming soon)


