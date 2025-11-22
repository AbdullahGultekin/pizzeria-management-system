"""
Order database models.
"""
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Order(Base):
    """Order model."""
    __tablename__ = "bestellingen"
    
    id = Column(Integer, primary_key=True, index=True)
    klant_id = Column(Integer, ForeignKey("klanten.id"), nullable=True)
    koerier_id = Column(Integer, nullable=True)  # Removed foreign key constraint - koeriers table may not exist
    datum = Column(String, nullable=False)
    tijd = Column(String, nullable=False)
    totaal = Column(Float, nullable=False)
    opmerking = Column(Text)
    bonnummer = Column(String)
    levertijd = Column(String)
    status = Column(String, default="Nieuw", nullable=False)  # Nieuw, In de keuken, Onderweg, Afgeleverd, Geannuleerd
    betaalmethode = Column(String, default="cash")  # "online" or "cash"
    afstand_km = Column(Float, nullable=True)  # Distance in kilometers
    online_bestelling = Column(Integer, default=0)  # 0 = kassa, 1 = online
    status_updated_at = Column(DateTime, nullable=True)  # Timestamp when status was last updated
    
    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.id}, bonnummer={self.bonnummer}, totaal={self.totaal})>"


class OrderItem(Base):
    """Order item model."""
    __tablename__ = "bestelregels"
    
    id = Column(Integer, primary_key=True, index=True)
    bestelling_id = Column(Integer, ForeignKey("bestellingen.id"), nullable=False)
    product_naam = Column(String, nullable=False)
    aantal = Column(Integer, nullable=False, default=1)
    prijs = Column(Float, nullable=False)
    opmerking = Column(Text)
    extras = Column(Text)  # JSON string for extras (vlees, bijgerecht, sauzen, garnering, etc.)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, product={self.product_naam}, aantal={self.aantal})>"

