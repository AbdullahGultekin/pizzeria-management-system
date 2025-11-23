"""
Script om een klant account handmatig te verifiëren.
Gebruik: python verify_customer.py <email>
"""
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.models.customer import Customer

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Gebruik: python verify_customer.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    init_db()
    db: Session = SessionLocal()
    
    try:
        customer = db.query(Customer).filter(Customer.email == email).first()
        
        if not customer:
            print(f"❌ Geen klant gevonden met e-mailadres: {email}")
            sys.exit(1)
        
        if customer.email_verified == 1:
            print(f"✅ Klant {email} is al geverifieerd.")
            sys.exit(0)
        
        print(f"⚠️  Verifiëren klant:")
        print(f"   ID: {customer.id}")
        print(f"   E-mail: {customer.email}")
        print(f"   Naam: {customer.naam}")
        
        customer.email_verified = 1
        customer.verification_token = None
        customer.verification_token_expires = None
        db.commit()
        
        print(f"\n✅ Klant {email} is nu geverifieerd en kan inloggen!")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Fout: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

