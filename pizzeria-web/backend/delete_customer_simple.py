"""
Eenvoudig script om klant accounts te verwijderen.
Gebruik: python delete_customer_simple.py [email]
Of zonder argumenten om alle niet-geverifieerde accounts te zien.
"""
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.models.customer import Customer

def main():
    init_db()
    db: Session = SessionLocal()
    
    try:
        # Als e-mailadres is opgegeven als argument
        if len(sys.argv) > 1:
            email = sys.argv[1]
            customer = db.query(Customer).filter(Customer.email == email).first()
            if not customer:
                print(f"❌ Geen klant gevonden met e-mailadres: {email}")
                return
            
            print(f"\n⚠️  Verwijderen klant:")
            print(f"   ID: {customer.id}")
            print(f"   E-mail: {customer.email}")
            print(f"   Naam: {customer.naam}")
            print(f"   Telefoon: {customer.telefoon}")
            print(f"   Geverifieerd: {'Ja' if customer.email_verified == 1 else 'Nee'}")
            
            db.delete(customer)
            db.commit()
            print(f"\n✅ Klant {email} is verwijderd.")
            return
        
        # Toon alle klanten
        customers = db.query(Customer).all()
        if not customers:
            print("Geen klanten gevonden in de database.")
            return
        
        print("\n" + "="*80)
        print("ALLE KLANTEN IN DATABASE")
        print("="*80)
        print(f"{'ID':<5} {'E-mail':<40} {'Naam':<30} {'Telefoon':<20} {'Geverifieerd':<12}")
        print("-"*80)
        
        unverified = []
        for customer in customers:
            verified = "✅ Ja" if customer.email_verified == 1 else "❌ Nee"
            email = customer.email or "Geen e-mail"
            naam = customer.naam or "Geen naam"
            telefoon = customer.telefoon or "Geen telefoon"
            print(f"{customer.id:<5} {email:<40} {naam:<30} {telefoon:<20} {verified:<12}")
            
            if customer.email_verified != 1:
                unverified.append(customer)
        
        print("="*80)
        
        if unverified:
            print(f"\n📋 {len(unverified)} niet-geverifieerde klant(en) gevonden:")
            for customer in unverified:
                print(f"   - {customer.email} (ID: {customer.id})")
            print(f"\n💡 Om een klant te verwijderen, gebruik:")
            print(f"   python delete_customer_simple.py <email-adres>")
            print(f"\n💡 Om alle niet-geverifieerde klanten te verwijderen:")
            print(f"   python delete_customer_simple.py --delete-unverified")
        else:
            print("\n✅ Alle klanten zijn geverifieerd.")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Fout: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def delete_all_unverified():
    """Verwijder alle niet-geverifieerde klanten."""
    init_db()
    db: Session = SessionLocal()
    
    try:
        unverified = db.query(Customer).filter(Customer.email_verified != 1).all()
        if not unverified:
            print("Geen niet-geverifieerde klanten gevonden.")
            return
        
        print(f"\n⚠️  Verwijderen {len(unverified)} niet-geverifieerde klant(en):")
        for customer in unverified:
            print(f"   - {customer.email} ({customer.naam})")
        
        for customer in unverified:
            db.delete(customer)
        db.commit()
        
        print(f"\n✅ {len(unverified)} klant(en) verwijderd.")
    except Exception as e:
        db.rollback()
        print(f"❌ Fout bij verwijderen: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--delete-unverified":
        delete_all_unverified()
    else:
        main()

