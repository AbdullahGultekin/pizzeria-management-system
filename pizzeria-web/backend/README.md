# Pizzeria Management System - Backend API

FastAPI backend voor het Pizzeria Management System.

## Setup

### 1. Install dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

De API is beschikbaar op:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/           # API routes
│   ├── core/          # Core configuration
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── websocket/     # WebSocket handlers
├── requirements.txt
└── README.md
```

## Features

- ✅ FastAPI with automatic API documentation
- ✅ SQLAlchemy ORM
- ✅ JWT authentication
- ✅ Rate limiting
- ✅ CORS support
- ✅ Security headers
- ✅ Input validation (Pydantic)
- ✅ SQL injection prevention

## API Endpoints

### Customers
- `GET /api/v1/customers` - List customers
- `GET /api/v1/customers/{id}` - Get customer
- `POST /api/v1/customers` - Create customer
- `PUT /api/v1/customers/{id}` - Update customer
- `GET /api/v1/customers/phone/{phone}` - Get by phone

## Development

```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run with specific host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000
```


