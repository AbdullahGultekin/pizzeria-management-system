# Alternatieve E-mail Oplossingen

Als one.com SMTP niet werkt vanwege geblokkeerde poorten, zijn hier alternatieven:

## Optie 1: SendGrid (Aanbevolen - Gratis Tier)

SendGrid biedt 100 gratis e-mails per dag.

### Stappen:
1. Maak account aan op https://sendgrid.com
2. Verifieer je e-mail
3. Maak een API key aan
4. Update `.env`:

```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM_EMAIL=noreply@pitapizzanapoli.be
SMTP_USE_TLS=true
```

## Optie 2: Mailgun (Gratis Tier: 5,000 e-mails/maand)

### Stappen:
1. Maak account aan op https://www.mailgun.com
2. Verifieer je domein
3. Update `.env`:

```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
SMTP_FROM_EMAIL=noreply@pitapizzanapoli.be
SMTP_USE_TLS=true
```

## Optie 3: Gmail SMTP (Als je Gmail hebt)

### Stappen:
1. Schakel "Minder veilige app-toegang" in (of gebruik App Password)
2. Maak een App Password aan in je Google Account
3. Update `.env`:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@pitapizzanapoli.be
SMTP_USE_TLS=true
```

## Optie 4: E-mailverificatie tijdelijk uitschakelen (Alleen ontwikkeling)

Voor lokale ontwikkeling kun je e-mailverificatie tijdelijk uitschakelen door in de database `email_verified=1` te zetten voor test accounts.

## Welke optie kiezen?

- **Voor productie**: SendGrid of Mailgun (betrouwbaar, gratis tier)
- **Voor ontwikkeling**: Gmail SMTP of verificatie uitschakelen
- **Als one.com werkt**: Blijf bij one.com maar los het firewall probleem op

