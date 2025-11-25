# Product Requirements Document (PRD)
## Pizzeria Management System

**Version:** 1.0.0  
**Date:** 2024  
**Status:** Production Ready

---

## 1. Executive Summary

### 1.1 Product Overview
Het Pizzeria Management System is een uitgebreide oplossing voor het beheren van pizzeria operaties, bestaande uit twee complementaire applicaties:
- **Desktop Applicatie**: Tkinter-gebaseerde desktop applicatie voor lokale kassa operaties
- **Web Applicatie**: Moderne web applicatie met FastAPI backend en React frontend voor online bestellingen en beheer

### 1.2 Business Objectives
- Automatiseren van bestelprocessen
- Verbeteren van klantenservice door online bestellingen
- Efficiënt beheer van klanten, menu's en voorraad
- Real-time tracking van bestellingen
- Genereren van rapportages en analytics
- Integratie met printers voor automatische bonnen

### 1.3 Target Users
- **Kassamedewerkers**: Plaatsen van bestellingen, klantbeheer
- **Administrators**: Menu beheer, rapportages, instellingen
- **Klanten**: Online bestellingen plaatsen, order status volgen
- **Koeriers**: Bezorging beheer

---

## 2. Product Architecture

### 2.1 System Components

#### 2.1.1 Desktop Application
- **Technology**: Python 3.8+, Tkinter
- **Database**: SQLite (pizzeria.db)
- **Key Features**:
  - Order management
  - Customer management
  - Menu management
  - Inventory tracking
  - Receipt printing (Windows)
  - Delivery driver management
  - Reporting

#### 2.1.2 Web Application
- **Backend**: FastAPI (Python)
  - RESTful API
  - WebSocket support voor real-time updates
  - JWT authentication
  - Rate limiting
  - CORS protection
- **Frontend**: React 18 + TypeScript
  - Material-UI components
  - Vite build tool
  - React Router voor navigatie
- **Database**: SQLAlchemy (SQLite/PostgreSQL ready)

### 2.2 Technology Stack

**Desktop:**
- Python 3.8+
- Tkinter (GUI)
- SQLite (database)
- PyInstaller (executable building)

**Web Backend:**
- FastAPI
- SQLAlchemy (ORM)
- Pydantic (validation)
- python-jose (JWT)
- bcrypt (password hashing)
- SlowAPI (rate limiting)
- WebSockets

**Web Frontend:**
- React 18
- TypeScript
- Material-UI (MUI)
- Vite
- React Router
- Axios
- date-fns

---

## 3. Functional Requirements

### 3.1 Authentication & Authorization

#### 3.1.1 User Roles
- **Admin**: Volledige toegang tot alle functies
- **Kassa**: Beperkte toegang voor bestellingen plaatsen
- **Publiek**: Alleen online bestellingen plaatsen

#### 3.1.2 Authentication Features
- JWT token-based authentication
- Secure password hashing (bcrypt)
- Role-based access control (RBAC)
- Protected routes in frontend
- Rate limiting voor API endpoints
- Session management

**Acceptance Criteria:**
- Gebruikers kunnen inloggen met gebruikersnaam en wachtwoord
- Tokens verlopen na configuratie periode
- Ongeautoriseerde toegang wordt geblokkeerd
- Wachtwoorden worden veilig opgeslagen (gehashed)

### 3.2 Customer Management

#### 3.2.1 Customer CRUD Operations
- Create: Nieuwe klanten aanmaken
- Read: Klanten zoeken en bekijken
- Update: Klantgegevens wijzigen
- Delete: Klanten verwijderen (met validatie)

#### 3.2.2 Customer Features
- Klant zoeken op telefoonnummer
- Klant statistieken (totaal bestellingen, totaal besteed)
- Klant selectie in Kassa interface
- Adres validatie en suggesties
- Telefoonnummer validatie
- Klant geschiedenis weergave

**Data Model:**
- Naam
- Telefoonnummer
- Email (optioneel)
- Adres (straat, huisnummer, postcode, gemeente)
- Opmerkingen

**Acceptance Criteria:**
- Klanten kunnen worden aangemaakt met verplichte velden
- Duplicate telefoonnummers worden gedetecteerd
- Adres suggesties werken correct
- Klant statistieken worden accuraat berekend

### 3.3 Order Management

#### 3.3.1 Order Creation
- Bestellingen plaatsen vanuit Kassa interface
- Online bestellingen van publieke website
- Product selectie met opties
- Winkelwagen functionaliteit
- Quantity management
- Prijs berekening (inclusief opties)

#### 3.3.2 Order Status Tracking
Status workflow:
1. **Nieuw**: Nieuwe bestelling
2. **In behandeling**: Wordt bereid
3. **Klaar**: Klaar voor bezorging/afhaling
4. **Onderweg**: Wordt bezorgd
5. **Afgeleverd**: Succesvol afgeleverd
6. **Geannuleerd**: Bestelling geannuleerd

#### 3.3.3 Order Features
- Order history voor Kassa gebruikers
- Order details weergave
- Order zoeken en filteren
- Real-time order updates via WebSockets
- Bonnummer generatie
- Order status wijzigen
- Order annuleren

**Data Model:**
- Order ID (bonnummer)
- Customer ID
- Status
- Totaal prijs
- Order items (producten met opties)
- Timestamps (created, updated)
- Delivery method (bezorging/afhaling)
- Courier ID (optioneel)

**Acceptance Criteria:**
- Bestellingen kunnen worden geplaatst met alle producten en opties
- Prijzen worden correct berekend
- Status updates worden real-time doorgegeven
- Order history is accuraat en filterbaar

### 3.4 Menu Management

#### 3.4.1 Menu CRUD Operations
- Menu items beheren (Create, Read, Update, Delete)
- Categorieën beheren
- Product beschikbaarheid toggle
- Menu import van JSON
- Prijs beheer

#### 3.4.2 Menu Features
- Publieke menu weergave (alleen beschikbare items)
- Product categorisatie
- Product zoekfunctie
- Product opties configuratie
- Menu sortering

**Data Model:**
- Product ID
- Naam
- Beschrijving
- Prijs
- Categorie
- Beschikbaarheid (boolean)
- Opties (vlees, bijgerecht, sauzen, garnering)
- Afbeelding (optioneel)

**Acceptance Criteria:**
- Menu items kunnen worden toegevoegd, gewijzigd en verwijderd
- Beschikbaarheid toggle werkt correct
- Publieke menu toont alleen beschikbare items
- Product opties worden correct weergegeven

### 3.5 Product Options

#### 3.5.1 Option Types
- **Vlees**: Vlees opties voor producten
- **Bijgerecht**: Bijgerechten (duplicate toegestaan voor specifieke producten)
- **Sauzen**: Saus opties
- **Garnering**: Garnering opties

#### 3.5.2 Option Features
- Dynamische product opties
- Live prijs berekening
- Product modal met opties
- Option pricing
- Duplicate bijgerechten toestaan

**Acceptance Criteria:**
- Product opties worden correct weergegeven
- Prijzen worden live berekend bij optie selectie
- Duplicate bijgerechten werken voor specifieke producten

### 3.6 Shopping Cart

#### 3.6.1 Cart Features
- Winkelwagen functionaliteit
- Quantity management (verhogen/verlagen)
- Product opties weergave
- Totaal berekening
- Cart sidebar (publieke pagina)
- Product verwijderen uit cart

**Acceptance Criteria:**
- Producten kunnen worden toegevoegd aan winkelwagen
- Quantity kan worden aangepast
- Totaal wordt correct berekend
- Cart wordt opgeslagen tijdens sessie

### 3.7 Printer Integration

#### 3.7.1 Printer Features
- Printer service (Windows direct print + queue)
- Print job queue voor desktop client
- ESC/POS receipt formatting
- QR code support
- Printer configuratie UI
- Automatisch printen na bestelling plaatsen
- Print knop in Admin dashboard

#### 3.7.2 Receipt Format
- Bonnummer
- Klantgegevens
- Producten met opties
- Totaal prijs
- Datum/tijd
- QR code (optioneel)
- Custom footer text

**Acceptance Criteria:**
- Bonnen worden automatisch geprint na bestelling
- Receipt formatting is correct
- QR codes worden gegenereerd indien geconfigureerd
- Print queue werkt voor desktop client

### 3.8 Reports & Analytics

#### 3.8.1 Report Types
- **Daily Reports**: Dagelijkse rapportages
- **Monthly Reports**: Maandelijkse rapportages
- **Z-Reports**: Dagafsluiting rapporten
- **Product Statistics**: Product populariteit
- **Hourly Breakdowns**: Uur per uur analyse
- **Courier Breakdowns**: Koerier prestaties
- **Revenue Tracking**: Omzet tracking

#### 3.8.2 Analytics Features
- Totaal bestellingen
- Totaal omzet
- Vandaag bestellingen
- Per status breakdown
- Product populariteit
- Hourly trends
- Courier performance

**Acceptance Criteria:**
- Rapporten worden correct gegenereerd
- Data is accuraat en up-to-date
- Rapporten kunnen worden geëxporteerd (toekomstig)

### 3.9 Real-time Updates

#### 3.9.1 WebSocket Features
- WebSocket support
- Live order updates
- Status change notifications
- Admin dashboard real-time sync
- Connection management

**Acceptance Criteria:**
- Order updates worden real-time doorgegeven
- WebSocket verbindingen zijn stabiel
- Reconnect logic werkt correct

### 3.10 Inventory Management (Desktop)

#### 3.10.1 Inventory Features
- Ingrediënten beheer
- Voorraad tracking
- Voorraad mutaties
- Recepturen beheer
- Low stock alerts (toekomstig)

**Acceptance Criteria:**
- Voorraad kan worden bijgewerkt
- Mutaties worden gelogd
- Recepturen kunnen worden beheerd

### 3.11 Delivery Management

#### 3.11.1 Courier Features
- Koeriers beheer
- Order toewijzing aan koeriers
- Delivery tracking
- Courier performance analytics

**Acceptance Criteria:**
- Koeriers kunnen worden beheerd
- Orders kunnen worden toegewezen aan koeriers
- Delivery status wordt bijgehouden

### 3.12 Public Customer Website

#### 3.12.1 Public Features
- Online menu weergave
- Product categorisatie
- Shopping cart
- Customer data form
- Order placement
- Order status tracking
- Real-time status updates

**Acceptance Criteria:**
- Publieke website is toegankelijk zonder login
- Menu wordt correct weergegeven
- Bestellingen kunnen worden geplaatst
- Order status kan worden getrackt

### 3.13 Admin Dashboard

#### 3.13.1 Dashboard Features
- Bestellingen overzicht met filters
- Statistieken (totaal, omzet, vandaag, nieuw)
- Status management
- Menu beheer
- Rapportages
- Printer instellingen
- Real-time updates

**Acceptance Criteria:**
- Dashboard toont accurate statistieken
- Filters werken correct
- Real-time updates worden weergegeven

### 3.14 Kassa Interface

#### 3.14.1 Kassa Features
- Product selectie
- Customer search
- Shopping cart
- Order placement
- Product zoekfunctie
- Keyboard shortcuts
- Automatisch printen

**Acceptance Criteria:**
- Kassa interface is gebruiksvriendelijk
- Keyboard shortcuts werken
- Bestellingen worden automatisch geprint

---

## 4. Non-Functional Requirements

### 4.1 Performance
- API response time < 200ms voor standaard queries
- Real-time updates binnen 1 seconde
- Frontend laadtijd < 3 seconden
- Database queries geoptimaliseerd met indexes

### 4.2 Security
- JWT token expiration
- Password hashing (bcrypt)
- Rate limiting op API endpoints
- CORS protection
- Security headers (XSS, CSRF protection)
- Input validation en sanitization
- SQL injection prevention (ORM)
- XSS protection

### 4.3 Scalability
- Database kan worden gemigreerd naar PostgreSQL
- API kan worden gehost op meerdere servers
- WebSocket connections kunnen worden geladen gebalanceerd

### 4.4 Usability
- Intuïtieve gebruikersinterface
- Responsive design voor verschillende schermformaten
- Keyboard shortcuts voor snelle navigatie
- Duidelijke error messages
- Loading states voor async operaties

### 4.5 Reliability
- Error handling en logging
- Database backups
- Transaction management
- Graceful error recovery

### 4.6 Compatibility
- Desktop: Windows, macOS, Linux
- Web: Alle moderne browsers (Chrome, Firefox, Safari, Edge)
- Printer: Windows direct print, queue voor andere platforms

---

## 5. User Stories

### 5.1 Kassa Medewerker
**Als** kassa medewerker  
**Wil ik** snel bestellingen kunnen plaatsen  
**Zodat** ik klanten efficiënt kan helpen

**Acceptance Criteria:**
- Klant kan snel worden gezocht op telefoonnummer
- Producten kunnen snel worden toegevoegd
- Bestelling wordt automatisch geprint
- Keyboard shortcuts werken

### 5.2 Admin
**Als** admin  
**Wil ik** menu items kunnen beheren  
**Zodat** ik het menu kan updaten

**Acceptance Criteria:**
- Menu items kunnen worden toegevoegd, gewijzigd, verwijderd
- Beschikbaarheid kan worden getoggled
- Prijzen kunnen worden aangepast

### 5.3 Klant
**Als** klant  
**Wil ik** online kunnen bestellen  
**Zodat** ik niet hoef te bellen

**Acceptance Criteria:**
- Menu is toegankelijk zonder login
- Bestelling kan worden geplaatst met klantgegevens
- Order status kan worden getrackt

---

## 6. API Specifications

### 6.1 Authentication Endpoints
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `POST /api/v1/auth/refresh` - Refresh token

### 6.2 Customer Endpoints
- `GET /api/v1/customers` - List customers
- `GET /api/v1/customers/{id}` - Get customer
- `POST /api/v1/customers` - Create customer
- `PUT /api/v1/customers/{id}` - Update customer
- `DELETE /api/v1/customers/{id}` - Delete customer
- `GET /api/v1/customers/search` - Search customers

### 6.3 Order Endpoints
- `GET /api/v1/orders` - List orders
- `GET /api/v1/orders/{id}` - Get order
- `POST /api/v1/orders` - Create order
- `PUT /api/v1/orders/{id}` - Update order
- `PUT /api/v1/orders/{id}/status` - Update order status
- `DELETE /api/v1/orders/{id}` - Cancel order

### 6.4 Menu Endpoints
- `GET /api/v1/menu` - Get menu (public)
- `GET /api/v1/menu/admin` - Get menu (admin)
- `GET /api/v1/menu/{id}` - Get menu item
- `POST /api/v1/menu` - Create menu item
- `PUT /api/v1/menu/{id}` - Update menu item
- `DELETE /api/v1/menu/{id}` - Delete menu item

### 6.5 Reports Endpoints
- `GET /api/v1/reports/daily` - Daily report
- `GET /api/v1/reports/monthly` - Monthly report
- `GET /api/v1/reports/z-report` - Z-report

### 6.6 WebSocket
- `WS /ws` - WebSocket connection voor real-time updates

---

## 7. Database Schema

### 7.1 Core Tables
- **customers**: Klantgegevens
- **orders**: Bestellingen
- **order_items**: Order regels
- **menu_items**: Menu producten
- **categories**: Categorieën
- **extras**: Product opties
- **couriers**: Koeriers
- **ingredients**: Ingrediënten (desktop)
- **recipes**: Recepturen (desktop)
- **inventory_transactions**: Voorraad mutaties (desktop)

### 7.2 Relationships
- Customer 1:N Orders
- Order 1:N OrderItems
- OrderItem N:1 MenuItem
- MenuItem N:1 Category
- MenuItem N:M Extras
- Order N:1 Courier (optioneel)

---

## 8. User Interface Requirements

### 8.1 Design Principles
- Modern, clean design
- Consistent kleurenschema (#e52525 rood)
- Material-UI components
- Responsive layout
- Accessible UI

### 8.2 Key Screens

#### 8.2.1 Desktop Application
- Main window met tabs
- Customer form
- Menu grid
- Order history
- Reports
- Settings

#### 8.2.2 Web Application
- Login page
- Admin dashboard
- Kassa interface
- Public menu page
- Order status page
- Customer search

### 8.3 Navigation
- Intuïtieve menu structuur
- Breadcrumbs waar nodig
- Keyboard shortcuts
- Search functionaliteit

---

## 9. Integration Requirements

### 9.1 Printer Integration
- Windows direct print support
- Print queue voor andere platforms
- ESC/POS formatting
- QR code generation

### 9.2 Email/SMS (Future)
- Framework is klaar
- SMTP configuratie nodig
- SMS service integratie (Twilio, etc.)

### 9.3 Payment Integration (Future)
- Stripe, Mollie, etc. kunnen worden toegevoegd

---

## 10. Testing Requirements

### 10.1 Unit Tests
- Business logic tests
- Service layer tests
- Repository tests
- Validation tests

### 10.2 Integration Tests
- API endpoint tests
- Database integration tests
- WebSocket tests

### 10.3 E2E Tests
- User flow tests
- Cross-browser tests

### 10.4 Test Coverage
- Minimum 70% code coverage
- Critical paths 100% coverage

---

## 11. Deployment Requirements

### 11.1 Desktop Application
- PyInstaller executable
- Windows installer (toekomstig)
- Auto-update mechanisme (toekomstig)

### 11.2 Web Application
- Backend: FastAPI met uvicorn
- Frontend: Vite build voor productie
- Database: SQLite (development), PostgreSQL (production)
- Environment variables voor configuratie

### 11.3 Infrastructure
- HTTPS in productie
- Domain configuratie
- SSL certificates
- Backup strategie

---

## 12. Documentation Requirements

### 12.1 User Documentation
- User manual
- Quick start guide
- FAQ

### 12.2 Technical Documentation
- API documentation (Swagger/ReDoc)
- Code comments
- Architecture documentation
- Deployment guide

### 12.3 Developer Documentation
- Setup instructions
- Development guidelines
- Testing guide
- Contribution guidelines

---

## 13. Future Enhancements

### 13.1 Planned Features
- Email/SMS notifications
- Payment integration
- Mobile app
- Advanced analytics
- Multi-location support
- Loyalty program
- Customer reviews

### 13.2 Technical Improvements
- Performance optimizations
- Caching layer
- CDN voor static assets
- Database sharding (bij schaal)
- Microservices architecture (bij schaal)

---

## 14. Success Metrics

### 14.1 Business Metrics
- Aantal bestellingen per dag
- Gemiddelde order waarde
- Klant retentie
- Online vs offline bestellingen ratio

### 14.2 Technical Metrics
- API response times
- Error rates
- Uptime percentage
- User satisfaction scores

---

## 15. Risk Assessment

### 15.1 Technical Risks
- Database performance bij schaal
- WebSocket connection stability
- Printer compatibility issues

### 15.2 Mitigation Strategies
- Database indexing en optimalisatie
- WebSocket reconnection logic
- Printer abstraction layer

---

## 16. Appendix

### 16.1 Glossary
- **Kassa**: Point of Sale / Cash register
- **Koerier**: Delivery driver
- **Bon**: Receipt
- **Bestelling**: Order
- **Klant**: Customer

### 16.2 References
- FastAPI documentation
- React documentation
- Material-UI documentation
- SQLAlchemy documentation

---

**Document Version History:**
- v1.0.0 - Initial PRD creation


