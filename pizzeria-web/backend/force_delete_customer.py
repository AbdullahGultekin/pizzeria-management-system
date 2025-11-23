"""
Force delete customer - verwijdert direct zonder bevestiging.
Gebruik: python force_delete_customer.py <email>
"""
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.models.customer import Customer

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Gebruik: python force_delete_customer.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    init_db()
    db: Session = SessionLocal()
    
    try:
        # Verwijder alle accounts met dit e-mailadres
        customers = db.query(Customer).filter(Customer.email == email).all()
        
        if not customers:
            print(f"❌ Geen klant gevonden met e-mailadres: {email}")
            sys.exit(1)
        
        print(f"⚠️  Verwijderen {len(customers)} klant(en) met e-mail: {email}")
        
        for customer in customers:
            print(f"   - ID: {customer.id}, Naam: {customer.naam}, Telefoon: {customer.telefoon}")
            db.delete(customer)
        
        db.commit()
        print(f"\n✅ {len(customers)} klant(en) verwijderd!")
        
        # Verifieer
        remaining = db.query(Customer).filter(Customer.email == email).count()
        if remaining == 0:
            print("✅ Verificatie: Geen accounts meer gevonden met dit e-mailadres.")
        else:
            print(f"⚠️  Waarschuwing: {remaining} account(s) nog steeds in database!")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Fout: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

