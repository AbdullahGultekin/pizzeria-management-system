# WebSocket Real-time Updates - Setup & Test

## Wat is er geïmplementeerd

✅ **Backend WebSocket Server**
- WebSocket endpoint op `/ws`
- Connection management
- Broadcast functionaliteit voor order updates
- Admin en publieke subscriptions

✅ **Frontend WebSocket Client**
- React hook `useWebSocket` voor eenvoudig gebruik
- Automatische reconnect functionaliteit
- Message handling

✅ **Real-time Features**
- Nieuwe bestellingen verschijnen direct in admin dashboard
- Status updates zijn real-time zichtbaar
- Live indicator in UI

## Testen

### 1. Backend Starten

```bash
cd pizzeria-web/backend
source venv/bin/activate
python run.py
```

De WebSocket endpoint is beschikbaar op: `ws://localhost:8000/ws`

### 2. Frontend Starten

```bash
cd pizzeria-web/frontend
npm run dev
```

### 3. Test Scenario

1. **Open Admin Dashboard**
   - Ga naar: `http://localhost:5173/admin`
   - Log in als admin
   - Je zou een "Live" indicator moeten zien (groen chip)

2. **Plaats een Nieuwe Bestelling**
   - Open een nieuwe tab: `http://localhost:5173/menu`
   - Plaats een test bestelling
   - De bestelling zou **direct** moeten verschijnen in het admin dashboard (zonder refresh!)

3. **Update Order Status**
   - In admin dashboard, verander de status van een bestelling
   - Als de klant de status pagina heeft open staan, zou de status **real-time** moeten updaten

4. **Test Status Page**
   - Open: `http://localhost:5173/status`
   - Zoek een bestelling op via bonnummer
   - Je zou een "Live" indicator moeten zien
   - Verander de status in admin dashboard
   - De status zou real-time moeten updaten op de status pagina

## WebSocket Message Types

### Van Client naar Server:
- `{"type": "ping"}` - Keep-alive ping
- `{"type": "subscribe_admin"}` - Subscribe voor admin updates
- `{"type": "subscribe_order", "order_id": 123}` - Subscribe voor specifieke order updates

### Van Server naar Client:
- `{"type": "pong"}` - Response op ping
- `{"type": "subscribed", "role": "admin"}` - Bevestiging van subscription
- `{"type": "order_created", "data": {...}}` - Nieuwe bestelling
- `{"type": "order_updated", "data": {...}}` - Bestelling geüpdatet
- `{"type": "order_status_changed", "data": {...}}` - Status gewijzigd

## Troubleshooting

### WebSocket verbindt niet
- Check of backend draait op poort 8000
- Check browser console voor errors
- Check of CORS correct is geconfigureerd

### Updates komen niet door
- Check of WebSocket verbinding actief is (groene "Live" indicator)
- Check backend logs voor broadcast errors
- Refresh de pagina en probeer opnieuw

### Performance Issues
- WebSocket verbindingen worden automatisch opgeschoond bij disconnect
- Maximaal aantal verbindingen is niet gelimiteerd (kan in productie worden toegevoegd)

## Volgende Verbeteringen

- [ ] WebSocket authentication (JWT tokens)
- [ ] Rate limiting voor WebSocket messages
- [ ] Connection pooling voor betere performance
- [ ] Message queue voor offline clients
- [ ] Push notifications voor mobiele devices


