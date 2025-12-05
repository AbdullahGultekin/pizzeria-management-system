"""
Test script om de volledige order flow te testen inclusief email verzending.
Dit simuleert wat er gebeurt wanneer een klant een bestelling plaatst.
"""
import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_full_order_flow():
    """Test de volledige order flow inclusief email verzending."""
    print("=" * 70)
    print("VOLLEDIGE ORDER FLOW TEST")
    print("=" * 70)
    
    try:
        from app.core.database import SessionLocal
        from app.models.customer import Customer
        from app.models.order import Order, OrderItem
        from app.services.notification import notification_service
        from app.services.email_service import email_service
        from app.api.orders import generate_bonnummer
        
        print("\n1. INITIALISATIE:")
        print(f"   Email service enabled: {email_service.enabled}")
        if not email_service.enabled:
            print("\n   ❌ EMAIL SERVICE IS NIET GEACTIVEERD!")
            return False
        
        # Get test data
        print("\n2. TEST DATA:")
        test_email = input("   Test email adres: ").strip()
        test_phone = input("   Test telefoonnummer (optioneel, Enter voor default): ").strip() or "0486123456"
        test_naam = input("   Test naam (optioneel, Enter voor default): ").strip() or "Test Klant"
        
        if not test_email or "@" not in test_email:
            print("   ❌ Ongeldig email adres!")
            return False
        
        db = SessionLocal()
        try:
            # Step 1: Create or get customer
            print("\n3. CUSTOMER AANMAKEN/OPHALEN:")
            customer = db.query(Customer).filter(
                (Customer.email == test_email) | (Customer.telefoon == test_phone)
            ).first()
            
            if customer:
                print(f"   ✅ Bestaande customer gevonden - ID: {customer.id}")
                # Update email if different
                if customer.email != test_email:
                    print(f"   Email updaten: {customer.email} -> {test_email}")
                    customer.email = test_email
                    db.commit()
                    db.refresh(customer)
            else:
                print(f"   Nieuwe customer aanmaken...")
                customer = Customer(
                    telefoon=test_phone,
                    email=test_email,
                    naam=test_naam,
                    straat="Teststraat",
                    huisnummer="123",
                    plaats="9120 Vrasene"
                )
                db.add(customer)
                db.commit()
                db.refresh(customer)
                print(f"   ✅ Customer aangemaakt - ID: {customer.id}")
            
            print(f"   Customer details:")
            print(f"     - ID: {customer.id}")
            print(f"     - Naam: {customer.naam}")
            print(f"     - Email: {customer.email}")
            print(f"     - Telefoon: {customer.telefoon}")
            
            # Step 2: Create order (simulate order creation)
            print("\n4. ORDER AANMAKEN:")
            bonnummer = generate_bonnummer(db)
            now = datetime.now()
            datum = now.strftime("%Y-%m-%d")
            tijd = now.strftime("%H:%M:%S")
            
            order = Order(
                klant_id=customer.id,
                datum=datum,
                tijd=tijd,
                totaal=25.50,
                opmerking="Test bestelling",
                bonnummer=bonnummer,
                levertijd=None,
                status="Nieuw",
                betaalmethode="cash",
                online_bestelling=1,
                status_updated_at=now
            )
            db.add(order)
            db.flush()  # Get order ID
            
            # Add order items
            item1 = OrderItem(
                bestelling_id=order.id,
                product_naam="Test Pizza Margherita",
                aantal=2,
                prijs=12.75,
                opmerking=None,
                extras=None
            )
            db.add(item1)
            db.commit()
            db.refresh(order)
            
            print(f"   ✅ Order aangemaakt:")
            print(f"     - ID: {order.id}")
            print(f"     - Bonnummer: {order.bonnummer}")
            print(f"     - Totaal: €{order.totaal:.2f}")
            print(f"     - Datum: {order.datum} {order.tijd}")
            
            # Step 3: Prepare order data for notification
            print("\n5. ORDER DATA VOORBEREIDEN:")
            order_notification_data = {
                "id": order.id,
                "bonnummer": order.bonnummer,
                "totaal": float(order.totaal),
                "datum": order.datum,
                "tijd": order.tijd,
                "status": order.status or "Nieuw",
                "items": [
                    {
                        "product_naam": item.product_naam,
                        "aantal": item.aantal,
                        "prijs": float(item.prijs)
                    }
                    for item in order.items
                ]
            }
            
            print(f"   Order data:")
            print(f"     - Bonnummer: {order_notification_data['bonnummer']}")
            print(f"     - Totaal: €{order_notification_data['totaal']:.2f}")
            print(f"     - Items: {len(order_notification_data['items'])}")
            
            # Step 4: Send confirmation email
            print("\n6. BEVESTIGINGSMAIL VERZENDEN:")
            print(f"   Verzenden naar: {customer.email}...")
            print("   " + "-" * 60)
            
            # Refresh customer to get latest email
            db.refresh(customer)
            customer_email = customer.email
            customer_phone = customer.telefoon
            
            print(f"   Customer email: {customer_email}")
            print(f"   Email service enabled: {email_service.enabled}")
            
            success = await notification_service.send_order_confirmation(
                order_data=order_notification_data,
                customer_email=customer_email,
                customer_phone=customer_phone
            )
            
            print("   " + "-" * 60)
            
            if success:
                print(f"\n   ✅ BEVESTIGINGSMAIL VERZONDEN!")
                print(f"   Controleer de inbox van {customer_email}")
                print(f"   (Ook spam/junk folder controleren)")
                print(f"\n   Order details:")
                print(f"     - Bonnummer: {bonnummer}")
                print(f"     - Totaal: €{order.totaal:.2f}")
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


if __name__ == "__main__":
    result = asyncio.run(test_full_order_flow())
    sys.exit(0 if result else 1)


