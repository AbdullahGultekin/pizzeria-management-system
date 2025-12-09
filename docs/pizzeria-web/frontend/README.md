# Pizzeria Management System - Frontend

React + TypeScript frontend voor het Pizzeria Management System.

## Setup

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Configure environment (optional)

Create `.env` file:
```
VITE_API_URL=http://localhost:8000/api/v1
```

### 3. Start development server

```bash
npm run dev
```

Frontend draait op: **http://localhost:3000**

## Features

- ✅ React + TypeScript
- ✅ Material-UI voor moderne UI
- ✅ React Router voor navigatie
- ✅ Axios voor API calls
- ✅ Authentication context
- ✅ Protected routes
- ✅ Role-based access

## Pages

- `/login` - Login pagina
- `/kassa` - Kassa interface (voor kassa gebruikers)
- `/admin` - Admin dashboard (alleen voor admin)

## Development

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Test Accounts

- **Admin**: `admin` / `admin123`
- **Kassa**: `kassa` / `kassa123`
