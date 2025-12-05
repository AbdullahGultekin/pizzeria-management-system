"""
Script om email configuratie te controleren en test email te versturen.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def check_email_config():
    """Check email configuration and send test email."""
    print("=" * 60)
    print("EMAIL CONFIGURATIE CHECK")
    print("=" * 60)
    
    try:
        from app.core.config import settings
        from app.services.email_service import email_service
        
        print("\n1. CONFIGURATIE:")
        print(f"   SMTP_HOST: {settings.SMTP_HOST}")
        print(f"   SMTP_PORT: {settings.SMTP_PORT}")
        print(f"   SMTP_USER: {settings.SMTP_USER}")
        print(f"   SMTP_FROM_EMAIL: {settings.SMTP_FROM_EMAIL}")
        print(f"   SMTP_USE_TLS: {settings.SMTP_USE_TLS}")
        print(f"   EMAIL_VERIFICATION_REQUIRED: {settings.EMAIL_VERIFICATION_REQUIRED}")
        
        print("\n2. EMAIL SERVICE STATUS:")
        print(f"   Enabled: {email_service.enabled}")
        if not email_service.enabled:
            print("\n   ❌ EMAIL SERVICE IS NIET GEACTIVEERD!")
            print("\n   Controleer of alle SMTP variabelen zijn ingesteld in .env:")
            print("   - SMTP_HOST")
            print("   - SMTP_PORT")
            print("   - SMTP_USER")
            print("   - SMTP_PASSWORD")
            print("   - SMTP_FROM_EMAIL")
            return False
        
        print("\n3. TEST EMAIL VERSTUREN:")
        test_email = input("   Naar welk email adres wil je een test email sturen? (Enter om over te slaan): ").strip()
        
        if not test_email:
            print("   Test email overgeslagen.")
            return True
        
        if "@" not in test_email:
            print("   ❌ Ongeldig email adres!")
            return False
        
        print(f"\n   Verzenden naar: {test_email}...")
        
        success = await email_service.send_email(
            to_email=test_email,
            subject="Test Email - Pita Pizza Napoli",
            body="Dit is een test email om te controleren of de SMTP configuratie correct werkt.",
            html_body="""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #ad2929;">Test Email - Pita Pizza Napoli</h2>
                <p>Dit is een test email om te controleren of de SMTP configuratie correct werkt.</p>
                <p>Als je deze email ontvangt, werkt de configuratie correct! ✅</p>
            </body>
            </html>
            """
        )
        
        if success:
            print("   ✅ Test email verzonden!")
            print(f"   Controleer de inbox van {test_email}")
            return True
        else:
            print("   ❌ Fout bij verzenden van test email!")
            print("   Controleer de logs voor meer details.")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(check_email_config())
    sys.exit(0 if result else 1)


