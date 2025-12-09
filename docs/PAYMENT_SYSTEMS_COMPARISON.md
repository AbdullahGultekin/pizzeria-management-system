# Betaalsystemen Vergelijking - Pizzeria Management System

## Overzicht

Voor een pizzeria in België/Nederland zijn er verschillende betaalsystemen beschikbaar. Deze vergelijking focust op kosten, integratie-moeilijkheid, en geschiktheid voor online bestellingen.

---

## Top Aanbevelingen voor Pizzeria's

### 🥇 **1. Mollie** (Beste keuze voor BE/NL)
**Waarom:**
- ✅ Geen maandelijkse kosten
- ✅ Ondersteunt Bancontact (BE) en iDEAL (NL)
- ✅ Eenvoudige integratie met Python/FastAPI
- ✅ Goede documentatie
- ✅ Geschikt voor kleine tot middelgrote pizzeria's

**Kosten:**
- **Maandelijks:** €0
- **Bancontact:** €0,29 per transactie
- **iDEAL:** €0,29 per transactie
- **Creditcard:** 1,4% + €0,25 per transactie
- **PayPal:** 1,4% + €0,25 per transactie

**Integratie:**
```python
# Mollie Python SDK
pip install mollie-api-python

# Eenvoudige integratie
import mollie
mollie_client = mollie.Client()
mollie_client.set_api_key('test_...')
```

**Voordelen:**
- Geen setup kosten
- Snelle goedkeuring (meestal binnen 24 uur)
- Goede klantenservice
- Webhook support voor real-time updates

**Nadelen:**
- Iets duurder dan Pay.nl voor iDEAL
- Minder bekend internationaal dan Stripe

---

### 🥈 **2. Stripe** (Beste voor internationale groei)
**Waarom:**
- ✅ Wereldwijd bekend en betrouwbaar
- ✅ Uitstekende documentatie
- ✅ Sterke Python SDK
- ✅ Ondersteunt Apple Pay, Google Pay
- ✅ Geen maandelijkse kosten

**Kosten:**
- **Maandelijks:** €0
- **Bancontact:** €0,29 per transactie
- **iDEAL:** €0,29 per transactie
- **Creditcard EU:** 1,4% + €0,25 per transactie
- **Creditcard buiten EU:** 2,9% + €0,25 per transactie

**Integratie:**
```python
# Stripe Python SDK
pip install stripe

# Eenvoudige integratie
import stripe
stripe.api_key = "sk_test_..."
```

**Voordelen:**
- Uitstekende developer experience
- Zeer betrouwbaar (99.99% uptime)
- Goede fraud detection
- Ondersteunt subscriptions (voor abonnementen)

**Nadelen:**
- Iets duurder voor creditcards buiten EU
- Minder focus op lokale betaalmethoden dan Mollie

---

### 🥉 **3. Pay.nl** (Goedkoopste voor iDEAL)
**Waarom:**
- ✅ Laagste kosten voor iDEAL
- ✅ Geen maandelijkse kosten (basis)
- ✅ Goede ondersteuning voor Nederlandse markt

**Kosten:**
- **Maandelijks:** €0 (basis) of €19,95 (premium)
- **iDEAL:** €0,25 per transactie (basis) of €0,20 (premium)
- **Bancontact:** €0,29 per transactie
- **Creditcard:** 1,5% + €0,25 per transactie

**Integratie:**
```python
# Pay.nl API
import requests

# REST API integratie
response = requests.post(
    'https://rest-api.pay.nl/v16/Transaction/start',
    data={...}
)
```

**Voordelen:**
- Goedkoopste iDEAL optie
- Geen setup kosten
- Goede Nederlandse support

**Nadelen:**
- Minder moderne API dan Mollie/Stripe
- Minder documentatie
- Premium nodig voor beste tarieven

---

## Volledige Kostenvergelijking

### Voorbeeld: Pizzeria met 500 bestellingen/maand, gemiddeld €25 per bestelling

| Provider | Maandelijks | Transactie | Totaal/maand | Totaal/jaar |
|----------|-------------|------------|--------------|-------------|
| **Mollie** | €0 | €0,29 | €145 | €1.740 |
| **Stripe** | €0 | €0,29 | €145 | €1.740 |
| **Pay.nl (basis)** | €0 | €0,25 | €125 | €1.500 |
| **Pay.nl (premium)** | €19,95 | €0,20 | €119,95 | €1.439,40 |
| **MultiSafepay** | €45 | €0,49 | €290 | €3.480 |

**Conclusie:** Pay.nl premium is het goedkoopst voor Nederlandse pizzeria's, Mollie/Stripe zijn het beste voor Belgische of gemengde markt.

---

## Betaalmethoden Ondersteuning

### België
| Provider | Bancontact | Creditcard | PayPal | Apple Pay |
|----------|------------|------------|--------|-----------|
| Mollie | ✅ | ✅ | ✅ | ✅ |
| Stripe | ✅ | ✅ | ✅ | ✅ |
| Pay.nl | ✅ | ✅ | ❌ | ❌ |

### Nederland
| Provider | iDEAL | Creditcard | PayPal | Apple Pay |
|----------|-------|------------|--------|-----------|
| Mollie | ✅ | ✅ | ✅ | ✅ |
| Stripe | ✅ | ✅ | ✅ | ✅ |
| Pay.nl | ✅ | ✅ | ❌ | ❌ |

---

## Integratie Moeilijkheid

### Mollie ⭐⭐⭐⭐⭐ (Zeer Eenvoudig)
```python
# Installatie
pip install mollie-api-python

# Gebruik
from mollie.api.client import Client

mollie_client = Client()
mollie_client.set_api_key('test_...')

payment = mollie_client.payments.create({
    'amount': {'currency': 'EUR', 'value': '25.00'},
    'description': 'Pizza bestelling #123',
    'redirectUrl': 'https://example.com/order/123',
    'method': 'bancontact'  # of 'ideal'
})
```

**Documentatie:** Uitstekend, veel voorbeelden

### Stripe ⭐⭐⭐⭐⭐ (Zeer Eenvoudig)
```python
# Installatie
pip install stripe

# Gebruik
import stripe
stripe.api_key = "sk_test_..."

payment_intent = stripe.PaymentIntent.create(
    amount=2500,  # €25.00 in centen
    currency='eur',
    payment_method_types=['bancontact', 'ideal', 'card'],
)
```

**Documentatie:** Uitstekend, zeer uitgebreid

### Pay.nl ⭐⭐⭐ (Gemiddeld)
```python
# REST API (geen officiële SDK)
import requests
import hashlib

# Meer handmatig werk nodig
def create_payment(amount, order_id):
    # API call met handmatige signature
    ...
```

**Documentatie:** Goed, maar minder voorbeelden

---

## Aanbeveling per Scenario

### Scenario 1: Pizzeria in België
**Aanbeveling: Mollie**
- Beste ondersteuning voor Bancontact
- Geen maandelijkse kosten
- Eenvoudige integratie

### Scenario 2: Pizzeria in Nederland
**Aanbeveling: Pay.nl Premium**
- Goedkoopste iDEAL optie (€0,20 vs €0,29)
- Bespaart €60/maand bij 500 bestellingen

### Scenario 3: Pizzeria in beide landen
**Aanbeveling: Mollie of Stripe**
- Beide ondersteunen Bancontact + iDEAL
- Mollie: iets goedkoper
- Stripe: betere internationale opties

### Scenario 4: Internationale groeiplannen
**Aanbeveling: Stripe**
- Beste internationale ondersteuning
- Uitstekende developer tools
- Ondersteunt 40+ landen

---

## Implementatie Checklist

### Voor Mollie:
- [ ] Account aanmaken op mollie.com
- [ ] API key ophalen (test + live)
- [ ] Python SDK installeren: `pip install mollie-api-python`
- [ ] Payment endpoint toevoegen aan FastAPI backend
- [ ] Webhook endpoint voor betalingsupdates
- [ ] Frontend checkout integratie
- [ ] Test met test API keys
- [ ] Go-live met live API keys

### Voor Stripe:
- [ ] Account aanmaken op stripe.com
- [ ] API keys ophalen (test + live)
- [ ] Python SDK installeren: `pip install stripe`
- [ ] Payment Intent endpoint toevoegen
- [ ] Webhook endpoint voor betalingsupdates
- [ ] Stripe.js in frontend integreren
- [ ] Test met test API keys
- [ ] Go-live met live API keys

---

## Code Voorbeelden

### Mollie Integratie (FastAPI)

```python
# backend/app/api/payments.py
from fastapi import APIRouter, HTTPException
from mollie.api.client import Client
import os

router = APIRouter()
mollie_client = Client()
mollie_client.set_api_key(os.getenv('MOLLIE_API_KEY'))

@router.post("/payments/create")
async def create_payment(order_id: int, amount: float):
    """Create Mollie payment for order."""
    try:
        payment = mollie_client.payments.create({
            'amount': {
                'currency': 'EUR',
                'value': f'{amount:.2f}'
            },
            'description': f'Pizza bestelling #{order_id}',
            'redirectUrl': f'https://example.com/order/{order_id}/success',
            'webhookUrl': f'https://api.example.com/webhooks/mollie',
            'metadata': {
                'order_id': order_id
            }
        })
        return {
            'payment_id': payment.id,
            'checkout_url': payment.checkout_url
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhooks/mollie")
async def mollie_webhook(payment_id: str):
    """Handle Mollie webhook."""
    payment = mollie_client.payments.get(payment_id)
    
    if payment.is_paid():
        # Update order status
        order_id = payment.metadata['order_id']
        # Mark order as paid
        ...
    
    return {'status': 'ok'}
```

### Stripe Integratie (FastAPI)

```python
# backend/app/api/payments.py
from fastapi import APIRouter, HTTPException
import stripe
import os

router = APIRouter()
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@router.post("/payments/create")
async def create_payment(order_id: int, amount: float):
    """Create Stripe payment intent."""
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency='eur',
            payment_method_types=['bancontact', 'ideal', 'card'],
            metadata={'order_id': order_id}
        )
        return {
            'client_secret': payment_intent.client_secret,
            'payment_intent_id': payment_intent.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook."""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
        
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            order_id = payment_intent['metadata']['order_id']
            # Mark order as paid
            ...
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## Veiligheid & Compliance

### PCI DSS Compliance
- **Mollie:** ✅ Volledig PCI DSS compliant (geen kaartgegevens op je server)
- **Stripe:** ✅ Volledig PCI DSS compliant
- **Pay.nl:** ✅ PCI DSS compliant

**Belangrijk:** Met alle providers hoef je zelf geen PCI DSS certificering te hebben, omdat je geen kaartgegevens opslaat.

### GDPR Compliance
- Alle providers zijn GDPR compliant
- Geen persoonlijke data opslaan langer dan nodig
- Webhook data encryptie gebruiken

---

## Conclusie & Aanbeveling

### Voor de meeste pizzeria's: **Mollie**
- ✅ Geen maandelijkse kosten
- ✅ Ondersteunt Bancontact + iDEAL
- ✅ Eenvoudige integratie
- ✅ Goede documentatie
- ✅ Geschikt voor BE/NL markt

### Voor internationale groei: **Stripe**
- ✅ Wereldwijd bekend
- ✅ Uitstekende tools
- ✅ Ondersteunt 40+ landen

### Voor Nederlandse focus: **Pay.nl Premium**
- ✅ Goedkoopste iDEAL optie
- ✅ Goede Nederlandse support

---

## Volgende Stappen

1. **Kies een provider** op basis van je locatie en volume
2. **Maak test account** aan
3. **Implementeer integratie** in FastAPI backend
4. **Test grondig** met test API keys
5. **Go-live** met live API keys
6. **Monitor** betalingssucces rate

---

## Resources

- **Mollie:** https://www.mollie.com/nl/docs
- **Stripe:** https://stripe.com/docs
- **Pay.nl:** https://www.pay.nl/developers

---

**Laatste update:** November 2024


