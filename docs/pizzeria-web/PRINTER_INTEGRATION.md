# Printer Integration Service

## ✅ Wat is geïmplementeerd

### 1. **Printer Service (Backend)**
- `app/services/printer.py`: Core printer service
  - Direct printing support (Windows only, via win32print)
  - Print job queue voor desktop client
  - Receipt formatting functie
  - QR code support
  - Printer discovery (lijst beschikbare printers)

### 2. **Printer API Endpoints**
- `GET /api/v1/printer/info`: Printer informatie en status
- `POST /api/v1/printer/print`: Print receipt voor een order
- `GET /api/v1/printer/jobs/pending`: Lijst van pending print jobs (admin)
- `POST /api/v1/printer/jobs/{job_id}/complete`: Markeer job als voltooid (admin)
- `POST /api/v1/printer/configure`: Configureer printer naam (admin)

### 3. **Frontend API Client**
- `printerAPI` toegevoegd aan `services/api.ts`
- Alle printer endpoints beschikbaar voor frontend

## Hoe het werkt

### Direct Printing (Windows)
Als de backend op Windows draait en `win32print` beschikbaar is:
1. Backend probeert direct te printen naar geconfigureerde printer
2. Als succesvol: job wordt gemarkeerd als "printed"
3. Als mislukt: job blijft in queue voor desktop client

### Print Job Queue
Voor cross-platform support of als direct printing niet werkt:
1. Print jobs worden in een queue gezet
2. Desktop client kan jobs ophalen via API
3. Desktop client print lokaal
4. Desktop client markeert job als voltooid

## Gebruik

### Backend (Python)
```python
from app.services.printer import printer_service

# Configureer printer
printer_service.set_printer_name("EPSON TM-T20II Receipt5")

# Print een order
job_id = printer_service.queue_print_job(
    order_data,
    receipt_text,
    qr_data="https://pitapizzanapoli.be/status?bonnummer=20240001"
)
```

### Frontend (React)
```typescript
import { printerAPI } from '../services/api'

// Print een order
await printerAPI.printOrder(orderId, "Custom footer text")

// Haal printer info op
const info = await printerAPI.getInfo()
console.log(info.available_printers)
```

## Printer Configuratie

### Via API (Admin only)
```typescript
// Configureer printer
await printerAPI.configure("EPSON TM-T20II Receipt5")
```

### Beschikbare Printers Ophalen
```typescript
const info = await printerAPI.getInfo()
console.log(info.available_printers) // Lijst van beschikbare printers
```

## Receipt Formatting

De `format_receipt` functie maakt een gestructureerde bon met:
- Header (bedrijfsnaam, adres, contact)
- Order informatie (bonnummer, datum, tijd)
- Klant informatie (als beschikbaar)
- Order items met prijzen
- Totaal
- Footer (openingsuren, custom footer)
- QR code (optioneel)

## Volgende Stappen

### Optioneel: Desktop Client
Een desktop client kan worden gemaakt die:
1. Periodiek pending jobs ophaalt
2. Lokaal print (gebruik bestaande print_utils.py)
3. Jobs markeert als voltooid

### Optioneel: Frontend UI
- Print knop in OrdersOverview component
- Printer configuratie pagina in Admin dashboard
- Print job status weergave

## Testen

1. **Test printer info:**
   ```bash
   curl http://localhost:8000/api/v1/printer/info \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **Test print order:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/printer/print \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"order_id": 1}'
   ```

3. **Test pending jobs:**
   ```bash
   curl http://localhost:8000/api/v1/printer/jobs/pending \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## Notities

- **Windows Only**: Direct printing werkt alleen op Windows met `win32print`
- **Cross-Platform**: Print job queue werkt op alle platformen
- **Security**: Alle printer endpoints vereisen authenticatie
- **Admin Only**: Configuratie en job management vereisen admin rol

De printer service is klaar voor gebruik! 🖨️


