# E-mail Verificatie Problemen Oplossen

## Problemen Gevonden en Opgelost

### 1. Email Service Retourneerde True Zelfs Als Email Niet Was Verzonden
**Probleem**: Als SMTP niet was geconfigureerd, retourneerde de email service `True` terwijl er geen email werd verstuurd. Dit gaf een vals gevoel van succes.

**Oplossing**: De email service retourneert nu `False` wanneer SMTP niet is geconfigureerd, met duidelijke error logging.

### 2. Base URL Probleem
**Probleem**: De verificatie link gebruikte `localhost:3000` als fallback, wat niet werkt in productie.

**Oplossing**: 
- Toegevoegd `FRONTEND_URL` configuratie optie
- Verbeterde logica om base URL te bepalen:
  1. Eerst proberen `Origin` header
  2. Dan `Referer` header (zonder pad)
  3. Als laatste `FRONTEND_URL` uit configuratie

### 3. Gebrek aan Duidelijke Error Messages
**Probleem**: Gebruikers kregen geen duidelijke feedback wanneer email verzending mislukte.

**Oplossing**: 
- Betere error messages in API responses
- Duidelijke logging voor debugging
- HTTP 500 error bij resend als email niet kan worden verzonden

## Configuratie Vereisten

### SMTP Instellingen
Voor e-mail verificatie om te werken, moet je de volgende environment variabelen instellen:

```bash
# SMTP Server Instellingen
SMTP_HOST=smtp.one.com                    # of je SMTP server
SMTP_PORT=587                             # Meestal 587 (TLS) of 465 (SSL)
SMTP_USER=noreply@pitapizzanapoli.be     # Je SMTP gebruikersnaam
SMTP_PASSWORD=je_wachtwoord_hier         # Je SMTP wachtwoord
SMTP_FROM_EMAIL=noreply@pitapizzanapoli.be
SMTP_USE_TLS=true                         # true voor port 587, false voor port 465

# Frontend URL (voor verificatie links)
FRONTEND_URL=https://jouw-domein.be       # Je productie frontend URL

# Email Verificatie (optioneel, standaard true)
EMAIL_VERIFICATION_REQUIRED=true
```

### Waar Instellen?
Maak een `.env` bestand in de `pizzeria-web/backend/` directory met bovenstaande instellingen.

## Testen

### 1. Test SMTP Connectie
```bash
cd pizzeria-web/backend
python test_smtp_connection.py
```

### 2. Test Email Verzending
```bash
cd pizzeria-web/backend
python test_email.py
```

### 3. Check Logs
Controleer de backend logs voor:
- `"Email service not configured"` - SMTP niet ingesteld
- `"SMTP error"` - SMTP connectie probleem
- `"Verification email sent"` - Succesvol verzonden
- `"Verification email FAILED to send"` - Verzending mislukt

## Veelvoorkomende Problemen

### Probleem: "Email service not configured"
**Oplossing**: Zorg dat alle SMTP environment variabelen zijn ingesteld in `.env` bestand.

### Probleem: "SMTP error" of "Network/DNS error"
**Oplossing**: 
- Controleer of `SMTP_HOST` correct is
- Controleer of je internetverbinding werkt
- Controleer firewall instellingen
- Voor one.com: gebruik `smtp.one.com` of `mail.one.com`

### Probleem: Verificatie link werkt niet
**Oplossing**: 
- Zorg dat `FRONTEND_URL` correct is ingesteld (zonder trailing slash)
- Controleer of de frontend op die URL draait
- Check of CORS correct is geconfigureerd

### Probleem: Email komt aan maar link werkt niet
**Oplossing**: 
- Controleer of de token niet is verlopen (24 uur geldig)
- Check of de database correct is geconfigureerd
- Controleer backend logs voor token verificatie errors

## Debugging

### Enable Debug Logging
In `pizzeria-web/backend/app/core/config.py`:
```python
DEBUG: bool = True  # Zet op True voor debug logging
```

### Check Email Service Status
De email service logt automatisch of het is geconfigureerd bij startup:
- `"Email service is not configured"` - Niet ingesteld
- Geen warning = Correct geconfigureerd

### Check Verification Token
```bash
cd pizzeria-web/backend
python verify_customer.py <email>
```

Dit toont de verificatie status van een klant.

## Productie Checklist

- [ ] SMTP credentials zijn ingesteld in `.env`
- [ ] `FRONTEND_URL` is ingesteld naar productie URL
- [ ] SMTP connectie is getest
- [ ] Email verzending is getest
- [ ] Verificatie link werkt in productie
- [ ] Error logging is geconfigureerd
- [ ] CORS is correct geconfigureerd voor productie domein



