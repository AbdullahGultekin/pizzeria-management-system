"""
Script om klant accounts te verwijderen of te resetten.
"""
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.models.customer import Customer

def list_customers():
    """Toon alle klanten."""
    db: Session = SessionLocal()
    try:
        customers = db.query(Customer).all()
        if not customers:
            print("Geen klanten gevonden in de database.")
            return []
        
        print("\n" + "="*80)
        print("KLANTEN IN DATABASE")
        print("="*80)
        print(f"{'ID':<5} {'E-mail':<40} {'Naam':<30} {'Telefoon':<20} {'Geverifieerd':<12}")
        print("-"*80)
        
        for customer in customers:
            verified = "✅ Ja" if customer.email_verified == 1 else "❌ Nee"
            email = customer.email or "Geen e-mail"
            naam = customer.naam or "Geen naam"
            telefoon = customer.telefoon or "Geen telefoon"
            print(f"{customer.id:<5} {email:<40} {naam:<30} {telefoon:<20} {verified:<12}")
        
        print("="*80)
        return customers
    finally:
        db.close()

def delete_customer_by_email(email: str):
    """Verwijder een klant op basis van e-mailadres."""
    db: Session = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.email == email).first()
        if not customer:
            print(f"❌ Geen klant gevonden met e-mailadres: {email}")
            return False
        
        print(f"\n⚠️  Je gaat de volgende klant verwijderen:")
        print(f"   ID: {customer.id}")
        print(f"   E-mail: {customer.email}")
        print(f"   Naam: {customer.naam}")
        print(f"   Telefoon: {customer.telefoon}")
        
        confirm = input("\nWeet je zeker dat je deze klant wilt verwijderen? (ja/nee): ").strip().lower()
        if confirm != 'ja':
            print("❌ Verwijderen geannuleerd.")
            return False
        
        db.delete(customer)
        db.commit()
        print(f"✅ Klant {email} is verwijderd.")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Fout bij verwijderen: {e}")
        return False
    finally:
        db.close()

def delete_customer_by_id(customer_id: int):
    """Verwijder een klant op basis van ID."""
    db: Session = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            print(f"❌ Geen klant gevonden met ID: {customer_id}")
            return False
        
        print(f"\n⚠️  Je gaat de volgende klant verwijderen:")
        print(f"   ID: {customer.id}")
        print(f"   E-mail: {customer.email}")
        print(f"   Naam: {customer.naam}")
        print(f"   Telefoon: {customer.telefoon}")
        
        confirm = input("\nWeet je zeker dat je deze klant wilt verwijderen? (ja/nee): ").strip().lower()
        if confirm != 'ja':
            print("❌ Verwijderen geannuleerd.")
            return False
        
        db.delete(customer)
        db.commit()
        print(f"✅ Klant ID {customer_id} is verwijderd.")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Fout bij verwijderen: {e}")
        return False
    finally:
        db.close()

def reset_verification(email: str):
    """Reset verificatie status van een klant (zodat verificatie-e-mail opnieuw kan worden verzonden)."""
    db: Session = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.email == email).first()
        if not customer:
            print(f"❌ Geen klant gevonden met e-mailadres: {email}")
            return False
        
        customer.email_verified = 0
        customer.verification_token = None
        customer.verification_token_expires = None
        db.commit()
        
        print(f"✅ Verificatie status gereset voor {email}")
        print(f"   Je kunt nu opnieuw een verificatie-e-mail aanvragen.")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Fout bij resetten: {e}")
        return False
    finally:
        db.close()

def delete_all_unverified():
    """Verwijder alle niet-geverifieerde klanten."""
    db: Session = SessionLocal()
    try:
        unverified = db.query(Customer).filter(Customer.email_verified != 1).all()
        if not unverified:
            print("Geen niet-geverifieerde klanten gevonden.")
            return
        
        print(f"\n⚠️  Je gaat {len(unverified)} niet-geverifieerde klant(en) verwijderen:")
        for customer in unverified:
            print(f"   - {customer.email} ({customer.naam})")
        
        confirm = input("\nWeet je zeker? (ja/nee): ").strip().lower()
        if confirm != 'ja':
            print("❌ Verwijderen geannuleerd.")
            return
        
        for customer in unverified:
            db.delete(customer)
        db.commit()
        
        print(f"✅ {len(unverified)} klant(en) verwijderd.")
    except Exception as e:
        db.rollback()
        print(f"❌ Fout bij verwijderen: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    
    print("\n" + "="*80)
    print("KLANT ACCOUNT BEHEER")
    print("="*80)
    print("\nKies een optie:")
    print("1. Lijst van alle klanten tonen")
    print("2. Klant verwijderen op basis van e-mailadres")
    print("3. Klant verwijderen op basis van ID")
    print("4. Verificatie status resetten (voor opnieuw verzenden e-mail)")
    print("5. Alle niet-geverifieerde klanten verwijderen")
    print("0. Afsluiten")
    
    while True:
        choice = input("\nJe keuze (0-5): ").strip()
        
        if choice == "0":
            print("Afsluiten...")
            break
        elif choice == "1":
            list_customers()
        elif choice == "2":
            email = input("E-mailadres: ").strip()
            if email:
                delete_customer_by_email(email)
        elif choice == "3":
            try:
                customer_id = int(input("Klant ID: ").strip())
                delete_customer_by_id(customer_id)
            except ValueError:
                print("❌ Ongeldig ID. Gebruik een nummer.")
        elif choice == "4":
            email = input("E-mailadres: ").strip()
            if email:
                reset_verification(email)
        elif choice == "5":
            delete_all_unverified()
        else:
            print("❌ Ongeldige keuze. Kies 0-5.")
        
        print("\n" + "-"*80)

