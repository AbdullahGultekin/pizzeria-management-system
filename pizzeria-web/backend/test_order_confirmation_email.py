"""
Test script om te controleren of order confirmation emails worden verzonden.
"""
import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_order_confirmation_email():
    """Test order confirmation email sending."""
    print("=" * 70)
    print("ORDER CONFIRMATION EMAIL TEST")
    print("=" * 70)
    
    try:
        from app.core.database import SessionLocal
        from app.models.customer import Customer
        from app.models.order import Order, OrderItem
        from app.services.notification import notification_service
        from app.services.email_service import email_service
        
        print("\n1. EMAIL SERVICE STATUS:")
        print(f"   Enabled: {email_service.enabled}")
        if not email_service.enabled:
            print("\n   ❌ EMAIL SERVICE IS NIET GEACTIVEERD!")
            print("   Controleer SMTP configuratie in .env")
            return False
        
        print(f"   SMTP Host: {email_service.smtp_host}")
        print(f"   SMTP Port: {email_service.smtp_port}")
        print(f"   SMTP User: {email_service.smtp_user}")
        print(f"   SMTP From: {email_service.smtp_from_email}")
        
        # Get test email
        print("\n2. TEST SETUP:")
        test_email = input("   Naar welk email adres wil je de test bevestigingsmail sturen? ").strip()
        
        if not test_email or "@" not in test_email:
            print("   ❌ Ongeldig email adres!")
            return False
        
        # Get or create test customer
        print("\n3. CUSTOMER SETUP:")
        db = SessionLocal()
        try:
            # Check if customer exists
            customer = db.query(Customer).filter(Customer.email == test_email).first()
            
            if not customer:
                # Create test customer
                print(f"   Test customer aanmaken met email: {test_email}")
                customer = Customer(
                    telefoon="0486123456",
                    email=test_email,
                    naam="Test Klant",
                    straat="Teststraat",
                    huisnummer="123",
                    plaats="9120 Vrasene"
                )
                db.add(customer)
                db.commit()
                db.refresh(customer)
                print(f"   ✅ Test customer aangemaakt - ID: {customer.id}")
            else:
                print(f"   ✅ Bestaande customer gevonden - ID: {customer.id}")
                print(f"   Naam: {customer.naam}")
                print(f"   Email: {customer.email}")
                print(f"   Telefoon: {customer.telefoon}")
            
            # Create test order data
            print("\n4. TEST ORDER DATA:")
            test_bonnummer = f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}"
            order_data = {
                "id": 999999,
                "bonnummer": test_bonnummer,
                "totaal": 25.50,
                "datum": datetime.now().strftime("%Y-%m-%d"),
                "tijd": datetime.now().strftime("%H:%M:%S"),
                "status": "Nieuw",
                "items": [
                    {
                        "product_naam": "Test Pizza Margherita",
                        "aantal": 2,
                        "prijs": 12.75
                    }
                ]
            }
            
            print(f"   Bonnummer: {test_bonnummer}")
            print(f"   Totaal: €{order_data['totaal']:.2f}")
            print(f"   Items: {len(order_data['items'])}")
            
            # Test notification service
            print("\n5. EMAIL VERZENDEN:")
            print(f"   Verzenden naar: {test_email}...")
            print("   " + "-" * 60)
            
            success = await notification_service.send_order_confirmation(
                order_data=order_data,
                customer_email=customer.email,
                customer_phone=customer.telefoon
            )
            
            print("   " + "-" * 60)
            
            if success:
                print(f"\n   ✅ BEVESTIGINGSMAIL VERZONDEN!")
                print(f"   Controleer de inbox van {test_email}")
                print(f"   (Ook spam/junk folder controleren)")
                return True
            else:
                print(f"\n   ❌ BEVESTIGINGSMAIL NIET VERZONDEN!")
                print(f"   Controleer de logs hierboven voor details")
                return False
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_direct_email_sending():
    """Test direct email sending without notification service."""
    print("\n" + "=" * 70)
    print("DIRECT EMAIL SENDING TEST (zonder notification service)")
    print("=" * 70)
    
    try:
        from app.services.email_service import email_service
        
        if not email_service.enabled:
            print("\n❌ Email service niet enabled")
            return False
        
        test_email = input("\nNaar welk email adres wil je een directe test email sturen? ").strip()
        
        if not test_email or "@" not in test_email:
            print("❌ Ongeldig email adres!")
            return False
        
        print(f"\nVerzenden naar: {test_email}...")
        
        success = await email_service.send_email(
            to_email=test_email,
            subject="Directe Test Email - Pita Pizza Napoli",
            body="Dit is een directe test email om te controleren of SMTP werkt.",
            html_body="""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #ad2929;">Directe Test Email</h2>
                <p>Dit is een directe test email om te controleren of SMTP werkt.</p>
                <p>Als je deze email ontvangt, werkt SMTP correct! ✅</p>
            </body>
            </html>
            """
        )
        
        if success:
            print("✅ Directe test email verzonden!")
            return True
        else:
            print("❌ Directe test email niet verzonden!")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\nKies een test:")
    print("1. Test order confirmation email (via notification service)")
    print("2. Test directe email sending (zonder notification service)")
    print("3. Beide tests uitvoeren")
    
    choice = input("\nKeuze (1/2/3): ").strip()
    
    if choice == "1":
        result = asyncio.run(test_order_confirmation_email())
    elif choice == "2":
        result = asyncio.run(test_direct_email_sending())
    elif choice == "3":
        result1 = asyncio.run(test_order_confirmation_email())
        result2 = asyncio.run(test_direct_email_sending())
        result = result1 and result2
    else:
        print("❌ Ongeldige keuze")
        sys.exit(1)
    
    sys.exit(0 if result else 1)


