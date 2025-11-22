# Security & Integration Guide - Pizzeria Web Application

## 🔐 Beveiliging: Welke Taal is het Beste?

### Overzicht van Security Features per Taal

#### 1. **Python (FastAPI/Django) - ⭐⭐⭐⭐⭐ AANBEVOLEN**

**Security Voordelen:**
- ✅ **Automatische input validation** via Pydantic (FastAPI) of Django Forms
- ✅ **SQL Injection bescherming** via ORM (SQLAlchemy/Django ORM)
- ✅ **XSS bescherming** ingebouwd in templates
- ✅ **CSRF protection** standaard in Django, makkelijk in FastAPI
- ✅ **Rate limiting** via libraries (slowapi, django-ratelimit)
- ✅ **Type safety** met type hints voorkomt veel bugs
- ✅ **Security headers** makkelijk te configureren
- ✅ **JWT tokens** goed ondersteund
- ✅ **OAuth2** ingebouwd in FastAPI

**Waarom Python voor jou:**
- Je kent Python al (bestaande codebase)
- Bestaande business logic kan hergebruikt worden
- Sterke security libraries
- Makkelijk te onderhouden

**Security Best Practices in Python:**
```python
# FastAPI - Automatische validation
from pydantic import BaseModel, EmailStr, validator

class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr  # Automatisch email validation
    phone: str = Field(..., regex=r'^\+?[0-9]{10,15}$')
    
    @validator('name')
    def name_must_not_contain_sql(cls, v):
        # Automatische SQL injection preventie
        if any(char in v for char in [';', '--', 'DROP', 'DELETE']):
            raise ValueError('Ongeldige karakters')
        return v

# SQL Injection bescherming via ORM
from sqlalchemy.orm import Session

def get_customer(db: Session, customer_id: int):
    # Veilig - geen SQL injection mogelijk
    return db.query(Customer).filter(Customer.id == customer_id).first()
    # NIET: db.execute(f"SELECT * FROM customers WHERE id = {customer_id}") ❌
```

---

#### 2. **Node.js (Express/NestJS) - ⭐⭐⭐⭐**

**Security Voordelen:**
- ✅ Goede security libraries (helmet, express-validator)
- ✅ JWT tokens goed ondersteund
- ⚠️ **Let op**: Meer security configuratie nodig dan Python
- ⚠️ **Let op**: NPM packages kunnen security vulnerabilities hebben

**Nadelen voor jou:**
- Moet JavaScript/TypeScript leren
- Bestaande Python code niet direct bruikbaar
- Meer security configuratie vereist

---

#### 3. **PHP (Laravel) - ⭐⭐⭐**

**Security Voordelen:**
- ✅ Goede security features
- ✅ CSRF protection ingebouwd
- ⚠️ **Let op**: PHP heeft historisch security issues gehad
- ⚠️ **Let op**: Minder modern dan Python/Node.js

---

### 🏆 **Mijn Aanbeveling: Python (FastAPI)**

**Waarom FastAPI voor Security:**

1. **Automatische Input Validation**
   - Pydantic valideert alle input automatisch
   - Type checking voorkomt bugs
   - Geen handmatige validation nodig

2. **SQL Injection Bescherming**
   - SQLAlchemy ORM voorkomt SQL injection
   - Parameterized queries standaard

3. **Moderne Security Standards**
   - OAuth2 ingebouwd
   - JWT tokens
   - Password hashing (bcrypt)
   - HTTPS enforcement

4. **Security Headers**
   ```python
   from fastapi.middleware.trustedhost import TrustedHostMiddleware
   from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
   
   app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
   app.add_middleware(HTTPSRedirectMiddleware)  # Force HTTPS
   ```

5. **Rate Limiting**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/api/orders")
   @limiter.limit("10/minute")  # Max 10 requests per minuut
   async def create_order(request: Request):
       ...
   ```

---

## 🖨️ Integratie met Bestaande Kassa/Printer

### Scenario: Web App + Desktop Kassa

Je hebt twee opties:

### **Optie 1: Web App als Hoofdsysteem, Desktop als Printer Client** ⭐ AANBEVOLEN

**Hoe het werkt:**
```
┌─────────────────────────────────────────┐
│         Web Application                  │
│  - Orders worden hier gemaakt            │
│  - Database staat hier                   │
│  - API voor printer communicatie        │
└──────────────┬──────────────────────────┘
               │ HTTP API
               │
┌──────────────▼──────────────────────────┐
│    Desktop Kassa (Printer Client)      │
│  - Lightweight applicatie               │
│  - Luistert naar print requests         │
│  - Print naar lokale printer            │
└─────────────────────────────────────────┘
```

**Voordelen:**
- ✅ Web app is de "single source of truth"
- ✅ Meerdere kassa's kunnen dezelfde printer gebruiken
- ✅ Orders zijn altijd gesynchroniseerd
- ✅ Desktop app blijft werken voor printing

**Implementatie:**

**Backend (FastAPI):**
```python
# backend/app/api/print.py
from fastapi import APIRouter, HTTPException
from app.services.print_service import PrintService

router = APIRouter()
print_service = PrintService()

@router.post("/api/print/receipt/{order_id}")
async def print_receipt(order_id: int):
    """
    Stuur print request naar beschikbare printer clients.
    """
    order = await get_order(order_id)
    receipt_data = generate_receipt(order)
    
    # Stuur naar alle geregistreerde printer clients
    result = await print_service.send_to_printer(receipt_data)
    
    if result:
        return {"status": "success", "printed": True}
    else:
        return {"status": "error", "message": "Geen printer beschikbaar"}
```

**Desktop Printer Client (Python):**
```python
# printer_client.py
import requests
import time
from win32print import OpenPrinter, StartDocPrinter, WritePrinter, EndDocPrinter

class PrinterClient:
    def __init__(self, api_url: str, printer_name: str):
        self.api_url = api_url
        self.printer_name = printer_name
        self.running = True
    
    def listen_for_print_jobs(self):
        """Luister naar print requests van web app"""
        while self.running:
            try:
                # Poll API voor print jobs
                response = requests.get(
                    f"{self.api_url}/api/print/queue",
                    headers={"X-Printer-Name": self.printer_name}
                )
                
                if response.status_code == 200:
                    jobs = response.json()
                    for job in jobs:
                        self.print_receipt(job['data'])
                
                time.sleep(2)  # Check elke 2 seconden
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
    
    def print_receipt(self, receipt_data: str):
        """Print receipt naar lokale printer"""
        try:
            hPrinter = OpenPrinter(self.printer_name)
            StartDocPrinter(hPrinter, 1, ("Receipt", None, None))
            WritePrinter(hPrinter, receipt_data.encode('utf-8'))
            EndDocPrinter(hPrinter)
            print(f"Receipt printed to {self.printer_name}")
        except Exception as e:
            print(f"Print error: {e}")
```

---

### **Optie 2: Web App + Directe Printer API** 

**Hoe het werkt:**
```
┌─────────────────────────────────────────┐
│         Web Application                  │
│  - Orders worden hier gemaakt            │
│  - Print via Web Print API              │
└──────────────┬──────────────────────────┘
               │
               │ Web Print API / CUPS
               │
┌──────────────▼──────────────────────────┐
│    Lokale Printer (via server)         │
│  - Printer staat op server              │
│  - Web app print direct                 │
└─────────────────────────────────────────┘
```

**Implementatie met Web Print API:**
```python
# Backend print service
from win32print import OpenPrinter, StartDocPrinter, WritePrinter

class PrintService:
    def __init__(self, printer_name: str):
        self.printer_name = printer_name
    
    async def print_receipt(self, receipt_data: str):
        """Print receipt direct naar Windows printer"""
        try:
            hPrinter = OpenPrinter(self.printer_name)
            StartDocPrinter(hPrinter, 1, ("Receipt", None, None))
            WritePrinter(hPrinter, receipt_data.encode('utf-8'))
            EndDocPrinter(hPrinter)
            return True
        except Exception as e:
            logger.error(f"Print error: {e}")
            return False
```

**⚠️ Let op:** Dit werkt alleen als:
- Web app draait op Windows server
- Printer is aangesloten op de server
- Of printer is netwerkprinter

---

### **Optie 3: Hybrid - Web App + Desktop Sync** ⭐⭐⭐ BESTE OPLOSSING

**Hoe het werkt:**
```
┌─────────────────────────────────────────┐
│         Web Application                  │
│  - Hoofdsysteem                         │
│  - Database                             │
│  - API                                  │
└──────────────┬──────────────────────────┘
               │
               │ Sync (WebSocket/HTTP)
               │
┌──────────────▼──────────────────────────┐
│    Desktop Kassa (Enhanced)             │
│  - Kan lokaal werken (offline mode)     │
│  - Sync met web app                     │
│  - Print naar lokale printer            │
└─────────────────────────────────────────┘
```

**Voordelen:**
- ✅ Werkt offline (desktop kan standalone werken)
- ✅ Sync wanneer verbinding beschikbaar is
- ✅ Beste van beide werelden
- ✅ Geen data verlies bij internet uitval

**Implementatie:**
```python
# Desktop app sync service
class SyncService:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.local_db = "pizzeria_local.db"
        self.syncing = False
    
    def sync_orders(self):
        """Sync lokale orders naar web app"""
        local_orders = self.get_local_orders()
        
        for order in local_orders:
            if not order.synced:
                try:
                    response = requests.post(
                        f"{self.api_url}/api/orders/sync",
                        json=order.to_dict(),
                        headers={"Authorization": f"Bearer {self.token}"}
                    )
                    if response.status_code == 200:
                        order.mark_as_synced()
                except requests.exceptions.ConnectionError:
                    # Offline - bewaar voor later
                    logger.info("Offline mode - order saved locally")
    
    def sync_from_server(self):
        """Haal updates op van web app"""
        try:
            response = requests.get(
                f"{self.api_url}/api/orders/sync",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                server_orders = response.json()
                self.update_local_db(server_orders)
        except requests.exceptions.ConnectionError:
            logger.info("Offline mode - using local data")
```

---

## 🔒 Complete Security Checklist

### 1. **Authentication & Authorization**

```python
# FastAPI met JWT tokens
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

# Role-based access
def require_role(required_role: str):
    def role_checker(current_user: str = Depends(get_current_user)):
        user = get_user(current_user)
        if user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Gebruik
@app.post("/api/admin/reports")
async def admin_reports(user: str = Depends(require_role("admin"))):
    ...
```

### 2. **Input Validation & Sanitization**

```python
from pydantic import BaseModel, validator, EmailStr
import html

class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., regex=r'^\+?[0-9]{10,15}$')
    address: str = Field(..., max_length=200)
    
    @validator('name', 'address')
    def sanitize_input(cls, v):
        # HTML escape om XSS te voorkomen
        return html.escape(v.strip())
    
    @validator('phone')
    def validate_phone(cls, v):
        # Alleen cijfers en + toestaan
        cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
        if len(cleaned) < 10:
            raise ValueError('Ongeldig telefoonnummer')
        return cleaned
```

### 3. **SQL Injection Prevention**

```python
# ✅ GOED - Gebruik ORM
from sqlalchemy.orm import Session

def get_customer(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.id == customer_id).first()

# ✅ GOED - Parameterized queries
def get_customer_raw(db: Session, customer_id: int):
    result = db.execute(
        text("SELECT * FROM customers WHERE id = :id"),
        {"id": customer_id}
    )
    return result.fetchone()

# ❌ SLECHT - NOOIT DOEN
def get_customer_bad(db: Session, customer_id: int):
    # SQL INJECTION VULNERABILITY!
    db.execute(f"SELECT * FROM customers WHERE id = {customer_id}")
```

### 4. **XSS Prevention**

```python
# Backend - HTML escape
from markupsafe import escape

@app.post("/api/customers")
async def create_customer(customer: CustomerCreate):
    # Automatisch ge-escaped door Pydantic validator
    name = customer.name  # Al ge-escaped
    
    # Of handmatig
    safe_name = escape(customer.name)
    ...

# Frontend - React doet dit automatisch
function CustomerName({ name }) {
    return <div>{name}</div>; // Automatisch ge-escaped
}
```

### 5. **CSRF Protection**

```python
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings(secret_key=SECRET_KEY)

@app.post("/api/orders")
async def create_order(
    request: Request,
    csrf_protect: CsrfProtect = Depends()
):
    await csrf_protect.validate_csrf(request)
    ...
```

### 6. **Rate Limiting**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/orders")
@limiter.limit("10/minute")  # Max 10 per minuut
async def create_order(request: Request):
    ...

@app.post("/api/login")
@limiter.limit("5/hour")  # Max 5 login pogingen per uur
async def login(request: Request):
    ...
```

### 7. **HTTPS Enforcement**

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Force HTTPS in productie
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "www.yourdomain.com"]
    )
```

### 8. **Security Headers**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Alleen jouw domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Extra security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

### 9. **Password Security**

```python
from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password met bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def generate_secure_token() -> str:
    """Generate secure random token"""
    return secrets.token_urlsafe(32)
```

### 10. **Logging & Monitoring**

```python
import logging
from logging.handlers import RotatingFileHandler

# Security event logging
security_logger = logging.getLogger("security")

@app.post("/api/login")
async def login(credentials: LoginRequest):
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        security_logger.warning(
            f"Failed login attempt for {credentials.username} from {request.client.host}"
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    security_logger.info(f"Successful login for {credentials.username}")
    ...
```

---

## 🎯 **Aanbevolen Architectuur**

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  - HTTPS only                                            │
│  - JWT tokens in httpOnly cookies                        │
│  - Input validation client-side                          │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS (TLS 1.3)
┌────────────────────▼────────────────────────────────────┐
│              Backend API (FastAPI)                      │
│  - Rate limiting                                         │
│  - Input validation (Pydantic)                           │
│  - Authentication (JWT)                                  │
│  - SQL Injection protection (SQLAlchemy)                │
│  - Security headers                                      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Database (PostgreSQL)                      │
│  - Encrypted connections                                │
│  - Role-based access                                    │
│  - Regular backups                                      │
└─────────────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│         Printer Client (Desktop App)                    │
│  - Authenticated API calls                              │
│  - Local printer access                                 │
│  - Offline mode support                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 **Security Checklist voor Productie**

- [ ] HTTPS enforced (TLS 1.3)
- [ ] JWT tokens met expiration
- [ ] Password hashing (bcrypt, min 12 rounds)
- [ ] Rate limiting op alle endpoints
- [ ] Input validation (Pydantic)
- [ ] SQL injection prevention (ORM)
- [ ] XSS prevention (HTML escaping)
- [ ] CSRF protection
- [ ] Security headers (HSTS, CSP, etc.)
- [ ] Role-based access control
- [ ] Logging van security events
- [ ] Regular security updates
- [ ] Database encryption at rest
- [ ] Backup strategy
- [ ] Environment variables voor secrets
- [ ] No secrets in code
- [ ] Regular security audits

---

## 🏆 **Finale Aanbeveling**

**Voor jouw situatie raad ik aan:**

1. **Backend: FastAPI (Python)**
   - Beste security features
   - Hergebruik bestaande code
   - Automatische validation
   - Moderne standaarden

2. **Frontend: React + TypeScript**
   - Type safety
   - Moderne UI libraries
   - Goede security practices

3. **Database: PostgreSQL**
   - Enterprise-grade security
   - Encrypted connections
   - Role-based access

4. **Printer Integratie: Hybrid Model**
   - Web app als hoofdsysteem
   - Desktop app als printer client
   - Offline mode support

5. **Deployment: HTTPS + Security Headers**
   - Let's Encrypt voor SSL
   - Security headers middleware
   - Rate limiting
   - Regular backups

**Wil je dat ik begin met het opzetten van een beveiligde FastAPI backend met alle security features?**


