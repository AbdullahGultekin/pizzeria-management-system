# Notification Service Setup

## Wat is geïmplementeerd

✅ **Notification Service Framework**
- Basis notification service structuur
- Order confirmation notifications
- Admin notifications
- Status update notifications
- Email formatting functies

## Huidige Status

De notification service is nu **logging-only**. Dit betekent:
- Notificaties worden gelogd in de backend logs
- Geen daadwerkelijke emails/SMS worden verstuurd (nog)
- Framework is klaar voor integratie met email/SMS services

## Volgende Stappen voor Email/SMS

### Optie 1: Email via SMTP (Aanbevolen)

1. **Installeer email library:**
   ```bash
   cd pizzeria-web/backend
   pip install aiosmtplib email-validator
   ```

2. **Update requirements.txt:**
   ```
   aiosmtplib>=2.0.0
   email-validator>=2.0.0
   ```

3. **Configureer SMTP in `.env`:**
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SMTP_FROM=noreply@pitapizzanapoli.be
   ```

4. **Implementeer email sending in `notification.py`**

### Optie 2: Email via Service (SendGrid, Mailgun, etc.)

1. **Kies een email service:**
   - SendGrid (gratis tier: 100 emails/dag)
   - Mailgun (gratis tier: 5,000 emails/maand)
   - AWS SES (zeer goedkoop)

2. **Installeer SDK:**
   ```bash
   pip install sendgrid  # of mailgun, etc.
   ```

3. **Configureer API key in `.env`**

### Optie 3: SMS via Service (Twilio, etc.)

1. **Kies een SMS service:**
   - Twilio (betaald, maar betrouwbaar)
   - MessageBird
   - AWS SNS

2. **Installeer SDK:**
   ```bash
   pip install twilio
   ```

3. **Configureer credentials in `.env`**

## Huidige Functionaliteit

### Order Confirmation
- Wordt automatisch getriggerd bij nieuwe bestelling
- Logt order details
- Klaar voor email/SMS integratie

### Status Updates
- Wordt automatisch getriggerd bij status wijziging
- Logt status change
- Klaar voor email/SMS integratie

### Admin Notifications
- Wordt automatisch getriggerd bij nieuwe bestelling
- Logt order details
- Klaar voor email/push integratie

## Testen

Check backend logs voor notifications:
```bash
tail -f /tmp/backend.log | grep -i notification
```

Je zou moeten zien:
```
INFO: Order confirmation notification for order 20240001
INFO: Admin notification for new order 20240001
INFO: Status update notification: Order 20240001 -> In behandeling
```

## Frontend Verbeteringen

✅ **Verbeterde order success message:**
- Duidelijke bonnummer weergave
- Knoppen voor status check en nieuwe bestelling
- Betere visuele feedback

## Volgende Implementatie Stappen

1. **Email integratie toevoegen** (als je dit wilt)
2. **SMS integratie toevoegen** (optioneel)
3. **Push notifications** voor admin dashboard (optioneel)
4. **Email templates** met HTML formatting (optioneel)

Wat wil je als volgende stap implementeren?


