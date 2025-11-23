# E-mail Configuratie voor One.com

## SMTP Instellingen

**BELANGRIJK:** De SMTP hostnaam voor one.com is meestal **`mail.one.com`** of **`smtp01.one.com`**, NIET `smtp.one.com`!

Maak een `.env` bestand aan in de `pizzeria-web/backend/` directory met de volgende instellingen:

```bash
# One.com SMTP Configuratie
# Probeer eerst mail.one.com, als dat niet werkt probeer smtp01.one.com
SMTP_HOST=mail.one.com
SMTP_PORT=587
SMTP_USER=noreply@pitapizzanapoli.be
SMTP_PASSWORD=JE_WACHTWOORD_HIER
SMTP_FROM_EMAIL=noreply@pitapizzanapoli.be
SMTP_USE_TLS=true
```

**Alternatieve hostnamen om te proberen:**
- `mail.one.com` (meest gebruikelijk)
- `smtp01.one.com`
- `smtp.one.com` (werkt meestal niet)

## Stappen

1. Maak een `.env` bestand aan in `pizzeria-web/backend/`
2. Kopieer de bovenstaande configuratie
3. Vervang `JE_WACHTWOORD_HIER` met het wachtwoord van het `noreply@pitapizzanapoli.be` e-mailadres
4. Start de backend opnieuw

## Testen

Na het configureren, test de e-mailverificatie door:
1. Een nieuwe gebruiker te registreren
2. De verificatielink in de inbox te controleren (of in de backend logs als e-mail niet werkt)

## Troubleshooting

Als e-mails niet worden verstuurd:

### Poorten geblokkeerd (timeout errors)
Als je een "timeout" of "connection refused" fout krijgt:
1. **Firewall check**: Controleer of je firewall poorten 587, 465 of 25 blokkeert
2. **ISP blokkering**: Sommige ISP's blokkeren SMTP poorten. Probeer:
   - Een andere netwerkverbinding (bijv. mobiele hotspot)
   - VPN gebruiken
3. **One.com specifieke instellingen**: 
   - Log in op je one.com dashboard
   - Ga naar E-mail instellingen
   - Controleer de exacte SMTP server naam en poort
   - Sommige providers gebruiken een andere hostnaam zoals `smtp.yourdomain.com`

### Alternatieve oplossingen

**Optie 1: Gebruik een externe e-mailservice**
Voor betrouwbare e-mailverzending kun je een service gebruiken zoals:
- **SendGrid** (gratis tier: 100 e-mails/dag)
- **Mailgun** (gratis tier: 5,000 e-mails/maand)
- **AWS SES** (zeer goedkoop)
- **Gmail SMTP** (als je een Gmail account hebt)

**Optie 2: E-mailverificatie uitschakelen (alleen voor ontwikkeling)**
Voor lokale ontwikkeling kun je tijdelijk e-mailverificatie uitschakelen.

**Optie 3: Handmatige verificatie**
Je kunt klanten handmatig verifiëren via de admin interface.

### Test je SMTP verbinding
Gebruik het test script:
```bash
python test_smtp_connection.py
```

Dit test verschillende SMTP configuraties en toont welke werken.

