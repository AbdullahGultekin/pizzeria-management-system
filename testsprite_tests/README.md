# TestSprite Test Configuration

## API Configuration

Dit project gebruikt de volgende API configuratie:

- **Base URL**: `http://localhost:8000`
- **API Version Prefix**: `/api/v1`
- **Authentication**: JWT tokens via OAuth2PasswordRequestForm (form-data, niet JSON)

## Belangrijke API Endpoints

### Authentication
- **Login**: `POST /api/v1/auth/login`
  - Method: form-data (data=, niet json=)
  - Credentials: admin/admin123 of kassa/kassa123

### Customers
- **Base**: `/api/v1/customers`
- **Requires Auth**: Ja
- **Fields**: naam, telefoon, email, straat, huisnummer, postcode, gemeente

### Orders
- **Base**: `/api/v1/orders`
- **Requires Auth**: Ja
- **Create Payload**: `{items: [{menu_item_id, quantity, options}], bezorging: boolean, afhaal: boolean}`
- **Status Update**: `PUT /api/v1/orders/{id}/status` met `{status: string}`

### Menu
- **Public**: `/api/v1/menu/public` (geen auth nodig)
- **Admin**: `/api/v1/menu` (admin auth nodig)
- **Fields**: naam, beschrijving, categorie, prijs, beschikbaar

### Extras
- **Public**: `/api/v1/extras/public` (geen auth nodig)
- **Note**: Extras worden geconfigureerd in extras.json, niet via API

### Reports
- **Daily**: `/api/v1/reports/daily?report_date=YYYY-MM-DD`
- **Monthly**: `/api/v1/reports/monthly?year=YYYY&month=MM`
- **Z-Report**: `/api/v1/reports/z-report?report_date=YYYY-MM-DD`
- **Requires**: Admin role

### Printer
- **Print**: `POST /api/v1/printer/print` met `{order_id}`

### WebSocket
- **Endpoint**: `ws://localhost:8000/ws`
- **Library**: `websockets` (plural, niet `websocket`)

## Test Plan Updates

Het testplan (`testsprite_backend_test_plan.json`) bevat nu specifieke API informatie in de descriptions. TestSprite zou deze informatie moeten gebruiken bij het genereren van tests.

## API Config File

Er is een `api_config.json` bestand met volledige API configuratie die als referentie kan dienen.

## Belangrijke Notities

1. **Authentication**: Gebruik altijd form-data voor login, niet JSON
2. **API Prefix**: Alle endpoints gebruiken `/api/v1/` prefix
3. **Credentials**: admin/admin123 en kassa/kassa123
4. **Shopping Cart**: Is frontend-only, geen backend API
5. **Product Options**: Configureerd in extras.json, niet via API
6. **WebSocket**: Gebruik `websockets` library (plural)

