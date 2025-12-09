# Deployment Guide - Pizzeria Web Application

## Overzicht

Deze guide helpt je om de pizzeria web applicatie te deployen en te starten.

## Architectuur

- **Backend**: FastAPI (Python) op poort 8000
- **Frontend**: React + Vite op poort 5173 (development) of 3002 (production)
- **Database**: SQLite (standaard) of PostgreSQL (productie)
- **Real-time**: WebSockets voor live updates

## Vereisten

### Backend
- Python 3.8+
- pip
- Virtual environment (aanbevolen)

### Frontend
- Node.js 16+
- npm of yarn

## Installatie

### 1. Backend Setup

```bash
# Navigeer naar backend directory
cd pizzeria-web/backend

# Maak virtual environment (aanbevolen)
python -m venv venv

# Activeer virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Installeer dependencies
pip install -r requirements.txt

# Importeer menu data (eerste keer)
python import_menu.py
```

### 2. Frontend Setup

```bash
# Navigeer naar frontend directory
cd pizzeria-web/frontend

# Installeer dependencies
npm install
```

## Starten (Development)

### Backend Starten

```bash
cd pizzeria-web/backend
source venv/bin/activate  # of venv\Scripts\activate op Windows
python run.py
```

Backend draait op: `http://localhost:8000`
API docs: `http://localhost:8000/api/docs`

### Frontend Starten

```bash
cd pizzeria-web/frontend
npm run dev
```

Frontend draait op: `http://localhost:5173`

## Productie Deployment

### Backend (Production)

1. **Environment Variables**:
   ```bash
   # Maak .env bestand
   DEBUG=False
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///./pizzeria.db  # of PostgreSQL URL
   ```

2. **Start met Uvicorn**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

3. **Met systemd (Linux)**:
   ```ini
   [Unit]
   Description=Pizzeria Backend
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/pizzeria-web/backend
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

### Frontend (Production)

1. **Build**:
   ```bash
   cd pizzeria-web/frontend
   npm run build
   ```

2. **Serve met Nginx**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       root /path/to/pizzeria-web/frontend/dist;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }

       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Of serve met Node.js**:
   ```bash
   npm install -g serve
   serve -s dist -l 3002
   ```

## Database Setup

### SQLite (Standaard)
Geen extra configuratie nodig. Database wordt automatisch aangemaakt.

### PostgreSQL (Productie)
1. Installeer PostgreSQL
2. Maak database:
   ```sql
   CREATE DATABASE pizzeria;
   ```
3. Update `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/pizzeria
   ```

## Printer Configuratie

### Windows (Direct Print)
1. Zorg dat printer is aangesloten en ingeschakeld
2. Ga naar Admin Dashboard > Instellingen
3. Selecteer printer uit dropdown
4. Klik op "Opslaan"

### Print Queue (Cross-Platform)
Als direct print niet werkt:
1. Print jobs worden automatisch in queue gezet
2. Desktop client kan jobs ophalen en printen
3. (Optioneel) Maak desktop client voor print queue

## Security Checklist

- [ ] Wijzig `SECRET_KEY` in productie
- [ ] Gebruik HTTPS in productie
- [ ] Configureer CORS correct
- [ ] Gebruik sterke wachtwoorden voor admin accounts
- [ ] Houd dependencies up-to-date
- [ ] Configureer rate limiting
- [ ] Gebruik environment variables voor secrets

## Monitoring

### Logs
- Backend logs: Check console output of log files
- Frontend errors: Check browser console

### Health Check
```bash
curl http://localhost:8000/api/health
```

## Troubleshooting

### Backend start niet
- Check Python versie: `python --version`
- Check dependencies: `pip list`
- Check poort 8000 is beschikbaar

### Frontend start niet
- Check Node.js versie: `node --version`
- Verwijder `node_modules` en `package-lock.json`, dan `npm install`
- Check poort 5173 is beschikbaar

### Database errors
- Check database file permissions
- Check database bestaat
- Run `import_menu.py` opnieuw

### Printer werkt niet
- Check printer is aangesloten
- Check printer naam exact overeenkomt
- Check Windows printer drivers
- Gebruik print queue als alternatief

## Backup

### Database Backup
```bash
# SQLite
cp pizzeria.db pizzeria.db.backup

# PostgreSQL
pg_dump pizzeria > backup.sql
```

### Menu Data Backup
```bash
cp menu.json menu.json.backup
cp extras.json extras.json.backup
```

## Updates

1. Pull laatste changes
2. Update dependencies:
   ```bash
   # Backend
   pip install -r requirements.txt --upgrade
   
   # Frontend
   npm update
   ```
3. Rebuild frontend: `npm run build`
4. Restart services

## Support

Voor problemen of vragen:
- Check logs voor error messages
- Check API docs: `http://localhost:8000/api/docs`
- Check browser console voor frontend errors


