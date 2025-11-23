"""
Test script voor e-mail configuratie.
Gebruik dit script om te testen of de SMTP configuratie correct werkt.
"""
import asyncio
import os
import sys
from app.services.email_service import email_service

async def test_email():
    """Test e-mail verzending."""
    print("=" * 50)
    print("E-mail Configuratie Test")
    print("=" * 50)
    
    # Check configuratie
    print("\n1. Configuratie controleren...")
    print(f"   SMTP Host: {email_service.smtp_host}")
    print(f"   SMTP Port: {email_service.smtp_port}")
    print(f"   SMTP User: {email_service.smtp_user}")
    print(f"   SMTP From: {email_service.smtp_from_email}")
    print(f"   Email Enabled: {email_service.enabled}")
    
    if not email_service.enabled:
        print("\n❌ E-mail service is NIET geconfigureerd!")
        print("\nMaak een .env bestand aan in pizzeria-web/backend/ met:")
        print("""
SMTP_HOST=smtp.one.com
SMTP_PORT=587
SMTP_USER=noreply@pitapizzanapoli.be
SMTP_PASSWORD=je-wachtwoord-hier
SMTP_FROM_EMAIL=noreply@pitapizzanapoli.be
SMTP_USE_TLS=true
        """)
        return False
    
    print("\n✅ E-mail service is geconfigureerd!")
    
    # Test e-mail verzenden
    print("\n2. Test e-mail verzenden...")
    test_email = input("   Naar welk e-mailadres wil je de test e-mail sturen? (of druk Enter om over te slaan): ").strip()
    
    if not test_email:
        print("   Test e-mail overgeslagen.")
        return True
    
    if "@" not in test_email:
        print("   ❌ Ongeldig e-mailadres!")
        return False
    
    print(f"   Verzenden naar: {test_email}...")
    
    success = await email_service.send_email(
        to_email=test_email,
        subject="Test E-mail - Pita Pizza Napoli",
        body="Dit is een test e-mail om te controleren of de SMTP configuratie correct werkt.",
        html_body="""
        <html>
        <body>
            <h2>Test E-mail - Pita Pizza Napoli</h2>
            <p>Dit is een test e-mail om te controleren of de SMTP configuratie correct werkt.</p>
            <p>Als je deze e-mail ontvangt, werkt de configuratie correct! ✅</p>
        </body>
        </html>
        """
    )
    
    if success:
        print("   ✅ Test e-mail verzonden!")
        print(f"   Controleer de inbox van {test_email}")
        return True
    else:
        print("   ❌ Fout bij verzenden van test e-mail!")
        print("   Controleer de logs voor meer details.")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_email())
    sys.exit(0 if result else 1)

