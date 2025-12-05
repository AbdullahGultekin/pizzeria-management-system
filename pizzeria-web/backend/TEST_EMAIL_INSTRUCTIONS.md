# Test Instructies voor Bevestigingsmails

## Probleem
Bevestigingsmails worden niet verzonden naar klanten na het plaatsen van een bestelling.

## Test Scripts

Er zijn 3 test scripts beschikbaar om te controleren waar het probleem zit:

### 1. Email Configuratie Test
Test of SMTP correct is geconfigureerd.

```bash
cd pizzeria-web/backend
python3 check_email_config.py
```

**Wat het doet:**
- Controleert SMTP configuratie
- Test of een directe email kan worden verzonden

**Verwacht resultaat:**
- ✅ "Test email verzonden!" = SMTP werkt
- ❌ "Email service not enabled" = SMTP configuratie probleem

---

### 2. Order Confirmation Email Test
Test of de notification service emails kan verzenden.

```bash
cd pizzeria-web/backend
python3 test_order_confirmation_email.py
```

**Kies optie 1** voor order confirmation test.

**Wat het doet:**
- Maakt een test customer aan (of gebruikt bestaande)
- Simuleert order data
- Test of notification service de email verzendt

**Verwacht resultaat:**
- ✅ "BEVESTIGINGSMAIL VERZONDEN!" = Notification service werkt
- ❌ "BEVESTIGINGSMAIL NIET VERZONDEN!" = Probleem in notification service

---

### 3. Volledige Order Flow Test
Test de volledige flow zoals bij een echte bestelling.

```bash
cd pizzeria-web/backend
python3 test_order_flow.py
```

**Wat het doet:**
- Maakt een customer aan/update
- Maakt een echte order aan in de database
- Verstuurt bevestigingsmail via notification service
- Simuleert exact wat er gebeurt bij een echte bestelling

**Verwacht resultaat:**
- ✅ "BEVESTIGINGSMAIL VERZONDEN!" = Volledige flow werkt
- ❌ "BEVESTIGINGSMAIL NIET VERZONDEN!" = Probleem in de flow

---

## Stap-voor-stap Diagnose

### Stap 1: Test SMTP Configuratie
```bash
python3 check_email_config.py
```

**Als dit faalt:**
- Controleer `.env` bestand
- Zorg dat alle SMTP variabelen zijn ingesteld:
  - `SMTP_HOST=send.one.com`
  - `SMTP_PORT=465`
  - `SMTP_USER=noreply@pitapizzanapoli.be`
  - `SMTP_PASSWORD=...`
  - `SMTP_FROM_EMAIL=noreply@pitapizzanapoli.be`
  - `SMTP_USE_TLS=false`

### Stap 2: Test Notification Service
```bash
python3 test_order_confirmation_email.py
# Kies optie 1
```

**Als dit faalt:**
- Controleer backend logs voor errors
- Controleer of `email_service.enabled = True`
- Controleer of customer email wordt doorgegeven

### Stap 3: Test Volledige Flow
```bash
python3 test_order_flow.py
```

**Als dit faalt:**
- Controleer of customer email wordt opgeslagen in database
- Controleer backend logs tijdens echte bestelling
- Zoek naar:
  - "Order confirmation notification for order..."
  - "Customer email: ..."
  - "Email service enabled: ..."
  - "Order confirmation email sent to..." of error messages

---

## Debugging Tips

### 1. Controleer Backend Logs
Tijdens het plaatsen van een bestelling, kijk naar de logs voor:

```
INFO: Order {bonnummer}: Customer found - ID: X, Email: ..., Phone: ...
INFO: Order confirmation notification for order {bonnummer}
INFO: Customer email: ...
INFO: Email service enabled: True/False
INFO: Order confirmation email sent to ... 
```

**Als je ziet:**
- "No customer email provided" → Email wordt niet opgeslagen bij customer aanmaken
- "Email service not enabled" → SMTP configuratie probleem
- "Failed to send order confirmation email" → SMTP verzending probleem

### 2. Controleer Database
```bash
# In Python shell of SQLite browser
SELECT id, naam, email, telefoon FROM klanten WHERE email IS NOT NULL;
```

Controleer of customers daadwerkelijk een email hebben.

### 3. Test Direct Email
```bash
python3 test_order_confirmation_email.py
# Kies optie 2
```

Dit test directe email verzending zonder notification service.

---

## Veelvoorkomende Problemen

### Probleem 1: Email wordt niet opgeslagen
**Symptoom:** "No customer email provided" in logs

**Oplossing:**
- Controleer of frontend email meestuurt bij customer create/update
- Controleer `CheckoutPage.tsx` - email moet worden meegestuurd

### Probleem 2: Email service niet enabled
**Symptoom:** "Email service not enabled" in logs

**Oplossing:**
- Controleer `.env` bestand
- Zorg dat alle SMTP variabelen zijn ingesteld
- Herstart backend server na `.env` wijzigingen

### Probleem 3: Async task wordt niet uitgevoerd
**Symptoom:** Geen logs over email verzending

**Oplossing:**
- Controleer of `asyncio.create_task()` wordt aangeroepen
- Controleer of er errors zijn in de async task
- Kijk naar volledige error traceback in logs

### Probleem 4: SMTP Authentication Error
**Symptoom:** "SMTP error" in logs

**Oplossing:**
- Controleer SMTP credentials
- Test met `check_email_config.py`
- Controleer one.com SMTP instellingen

---

## Test Resultaten Interpreteren

### ✅ Alles werkt
```
✅ Test email verzonden!
✅ BEVESTIGINGSMAIL VERZONDEN!
```
→ Emails worden verzonden, controleer spam folder als je ze niet ziet

### ❌ SMTP probleem
```
❌ Email service not enabled
❌ SMTP error sending email
```
→ Controleer SMTP configuratie in `.env`

### ❌ Notification service probleem
```
❌ BEVESTIGINGSMAIL NIET VERZONDEN!
❌ No customer email provided
```
→ Controleer of customer email wordt opgeslagen en doorgegeven

---

## Volgende Stappen

1. **Run alle tests** en noteer welke falen
2. **Controleer logs** tijdens echte bestelling
3. **Deel test resultaten** zodat we het probleem kunnen identificeren
4. **Fix het probleem** op basis van de test resultaten


