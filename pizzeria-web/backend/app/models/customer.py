"""
Customer database model.
"""
from sqlalchemy import Column, Integer, String, Float, Text
from app.core.database import Base


class Customer(Base):
    """Customer model."""
    __tablename__ = "klanten"
    
    id = Column(Integer, primary_key=True, index=True)
    telefoon = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True, index=True)  # Email for login
    password_hash = Column(String, nullable=True)  # Hashed password
    email_verified = Column(Integer, default=0, nullable=False)  # 0 = not verified, 1 = verified
    verification_token = Column(String, nullable=True)  # Token for email verification
    verification_token_expires = Column(String, nullable=True)  # Expiration time for token
    naam = Column(String)
    straat = Column(String)
    huisnummer = Column(String)
    plaats = Column(String)
    notities = Column(Text)
    voorkeur_levering = Column(String)
    laatste_bestelling = Column(String)
    totaal_bestellingen = Column(Integer, default=0)
    totaal_besteed = Column(Float, default=0.0)
    volle_kaart = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Customer(id={self.id}, naam={self.naam}, telefoon={self.telefoon}, email={self.email})>"


