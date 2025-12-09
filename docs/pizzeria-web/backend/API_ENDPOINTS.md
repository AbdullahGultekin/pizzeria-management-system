# API Endpoints Documentatie

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "role": "admin"
  }
}
```

### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

---

## Customers

### List Customers
```http
GET /api/v1/customers?skip=0&limit=100&search=john
Authorization: Bearer <token>
```

### Get Customer by ID
```http
GET /api/v1/customers/{customer_id}
Authorization: Bearer <token>
```

### Create Customer
```http
POST /api/v1/customers
Authorization: Bearer <token>
Content-Type: application/json

{
  "telefoon": "+32123456789",
  "naam": "John Doe",
  "straat": "Main Street",
  "huisnummer": "123",
  "plaats": "Sint-Niklaas"
}
```

### Update Customer
```http
PUT /api/v1/customers/{customer_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "naam": "John Updated",
  "straat": "New Street"
}
```

### Get Customer by Phone
```http
GET /api/v1/customers/phone/{phone_number}
Authorization: Bearer <token>
```

---

## Orders

### List Orders
```http
GET /api/v1/orders?skip=0&limit=100&customer_id=1
Authorization: Bearer <token>
```

### Get Order by ID
```http
GET /api/v1/orders/{order_id}
Authorization: Bearer <token>
```

### Create Order
```http
POST /api/v1/orders
Authorization: Bearer <token>
Content-Type: application/json

{
  "klant_id": 1,
  "totaal": 25.50,
  "opmerking": "Extra kaas",
  "items": [
    {
      "product_naam": "Pizza Margherita",
      "aantal": 2,
      "prijs": 12.50,
      "opmerking": "Extra kaas"
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "klant_id": 1,
  "datum": "2024-01-15",
  "tijd": "14:30:00",
  "totaal": 25.50,
  "bonnummer": "20240001",
  "items": [...]
}
```

### Update Order
```http
PUT /api/v1/orders/{order_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "koerier_id": 1,
  "levertijd": "30 minuten"
}
```

### Delete Order
```http
DELETE /api/v1/orders/{order_id}
Authorization: Bearer <token>
```

---

## Menu

### Get Complete Menu
```http
GET /api/v1/menu
Authorization: Bearer <token>
```

**Response:**
```json
{
  "categories": [
    {
      "id": 1,
      "naam": "Pizza's",
      "volgorde": 0
    }
  ],
  "items": [
    {
      "id": 1,
      "naam": "Pizza Margherita",
      "categorie": "Pizza's",
      "prijs": 12.50,
      "beschikbaar": 1
    }
  ]
}
```

### Get Menu Items
```http
GET /api/v1/menu/items?categorie=Pizza's
Authorization: Bearer <token>
```

### Get Menu Item by ID
```http
GET /api/v1/menu/items/{item_id}
Authorization: Bearer <token>
```

### Get Menu Categories
```http
GET /api/v1/menu/categories
Authorization: Bearer <token>
```

### Create Menu Item (Admin Only)
```http
POST /api/v1/menu/items
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "naam": "Pizza Special",
  "categorie": "Pizza's",
  "prijs": 15.00,
  "beschrijving": "Lekkere pizza",
  "beschikbaar": 1
}
```

### Update Menu Item (Admin Only)
```http
PUT /api/v1/menu/items/{item_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "prijs": 16.00,
  "beschikbaar": 0
}
```

### Delete Menu Item (Admin Only)
```http
DELETE /api/v1/menu/items/{item_id}
Authorization: Bearer <admin_token>
```

### Create Menu Category (Admin Only)
```http
POST /api/v1/menu/categories
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "naam": "Desserts",
  "volgorde": 5
}
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource niet gevonden"
}
```

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

---

## Rate Limiting

- Most endpoints: 60 requests per minute
- Login endpoint: 5 requests per hour
- Create endpoints: 30 requests per minute

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1234567890
```


