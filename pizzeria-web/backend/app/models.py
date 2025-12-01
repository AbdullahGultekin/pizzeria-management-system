"""
Complete database models file for server deployment.
This file contains ALL database tables as SQLAlchemy models.

This is the complete schema definition required for server deployment.
"""
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


# ============================================================================
# CUSTOMER MODELS
# ============================================================================

class Customer(Base):
    """Customer model - klanten table."""
    __tablename__ = "klanten"
    
    id = Column(Integer, primary_key=True, index=True)
    telefoon = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    password_hash = Column(String, nullable=True)
    email_verified = Column(Integer, default=0, nullable=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires = Column(String, nullable=True)
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
        return f"<Customer(id={self.id}, naam={self.naam}, telefoon={self.telefoon})>"


# ============================================================================
# ORDER MODELS
# ============================================================================

class Order(Base):
    """Order model - bestellingen table."""
    __tablename__ = "bestellingen"
    
    id = Column(Integer, primary_key=True, index=True)
    klant_id = Column(Integer, ForeignKey("klanten.id"), nullable=True)
    koerier_id = Column(Integer, nullable=True)
    datum = Column(String, nullable=False)
    tijd = Column(String, nullable=False)
    totaal = Column(Float, nullable=False)
    opmerking = Column(Text)
    bonnummer = Column(String)
    levertijd = Column(String)
    status = Column(String, default="Nieuw", nullable=False)
    betaalmethode = Column(String, default="cash")
    afstand_km = Column(Float, nullable=True)
    online_bestelling = Column(Integer, default=0)
    afhaal = Column(Integer, default=0)
    status_updated_at = Column(DateTime, nullable=True)
    
    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.id}, bonnummer={self.bonnummer}, totaal={self.totaal})>"


class OrderItem(Base):
    """Order item model - bestelregels table."""
    __tablename__ = "bestelregels"
    
    id = Column(Integer, primary_key=True, index=True)
    bestelling_id = Column(Integer, ForeignKey("bestellingen.id"), nullable=False)
    categorie = Column(String)
    product = Column(String)
    product_naam = Column(String, nullable=False)
    aantal = Column(Integer, nullable=False, default=1)
    prijs = Column(Float, nullable=False)
    opmerking = Column(Text)
    extras = Column(Text)  # JSON string for extras
    
    # Relationships
    order = relationship("Order", back_populates="items")
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, product={self.product_naam}, aantal={self.aantal})>"


# ============================================================================
# COURIER MODEL
# ============================================================================

class Courier(Base):
    """Courier model - koeriers table."""
    __tablename__ = "koeriers"
    
    id = Column(Integer, primary_key=True, index=True)
    naam = Column(String, unique=True, nullable=False)
    
    def __repr__(self):
        return f"<Courier(id={self.id}, naam={self.naam})>"


# ============================================================================
# MENU MODELS
# ============================================================================

class MenuCategory(Base):
    """Menu category model - menu_categories table."""
    __tablename__ = "menu_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    naam = Column(String, unique=True, nullable=False)
    volgorde = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<MenuCategory(id={self.id}, naam={self.naam})>"


class MenuItem(Base):
    """Menu item model - menu_items table."""
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    naam = Column(String, nullable=False)
    categorie = Column(String, nullable=False)
    prijs = Column(Float, nullable=False)
    beschrijving = Column(Text)
    beschikbaar = Column(Integer, default=1)
    volgorde = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<MenuItem(id={self.id}, naam={self.naam}, prijs={self.prijs})>"


# ============================================================================
# RECEIPT NUMBER MODEL
# ============================================================================

class BonTeller(Base):
    """Receipt number counter model - bon_teller table."""
    __tablename__ = "bon_teller"
    
    jaar = Column(Integer, primary_key=True, nullable=False)
    dag = Column(Integer, primary_key=True, nullable=False)
    laatste_nummer = Column(Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f"<BonTeller(jaar={self.jaar}, dag={self.dag}, nummer={self.laatste_nummer})>"


# ============================================================================
# FAVORITE ORDERS MODEL
# ============================================================================

class FavoriteOrder(Base):
    """Favorite order model - favoriete_bestellingen table."""
    __tablename__ = "favoriete_bestellingen"
    
    id = Column(Integer, primary_key=True, index=True)
    klant_id = Column(Integer, ForeignKey("klanten.id"), nullable=False)
    naam = Column(String, nullable=False)
    bestelregels_json = Column(Text, nullable=False)
    totaal_prijs = Column(Float)
    aangemaakt_op = Column(String, nullable=False)
    laatst_gebruikt = Column(String)
    gebruik_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<FavoriteOrder(id={self.id}, naam={self.naam}, klant_id={self.klant_id})>"


# ============================================================================
# CUSTOMER NOTES MODEL
# ============================================================================

class CustomerNote(Base):
    """Customer note model - klant_notities table."""
    __tablename__ = "klant_notities"
    
    id = Column(Integer, primary_key=True, index=True)
    klant_id = Column(Integer, ForeignKey("klanten.id"), nullable=False)
    notitie = Column(Text, nullable=False)
    aangemaakt_op = Column(String, nullable=False)
    medewerker = Column(String)
    
    def __repr__(self):
        return f"<CustomerNote(id={self.id}, klant_id={self.klant_id})>"


# ============================================================================
# INVENTORY MODELS
# ============================================================================

class Ingredient(Base):
    """Ingredient model - ingredienten table."""
    __tablename__ = "ingredienten"
    
    id = Column(Integer, primary_key=True, index=True)
    naam = Column(String, unique=True, nullable=False)
    eenheid = Column(String, nullable=False)
    minimum = Column(Float, default=0)
    huidige_voorraad = Column(Float, default=0)
    
    def __repr__(self):
        return f"<Ingredient(id={self.id}, naam={self.naam})>"


class Recipe(Base):
    """Recipe model - recepturen table."""
    __tablename__ = "recepturen"
    
    id = Column(Integer, primary_key=True, index=True)
    categorie = Column(String, nullable=False)
    product = Column(String, nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredienten.id"), nullable=False)
    hoeveelheid_per_stuk = Column(Float, nullable=False)
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
    
    def __repr__(self):
        return f"<Recipe(id={self.id}, categorie={self.categorie}, product={self.product})>"


class InventoryTransaction(Base):
    """Inventory transaction model - voorraad_mutaties table."""
    __tablename__ = "voorraad_mutaties"
    
    id = Column(Integer, primary_key=True, index=True)
    ingredient_id = Column(Integer, ForeignKey("ingredienten.id"), nullable=False)
    mutatie = Column(Float, nullable=False)
    reden = Column(Text)
    datumtijd = Column(String, nullable=False)
    
    def __repr__(self):
        return f"<InventoryTransaction(id={self.id}, ingredient_id={self.ingredient_id})>"


# ============================================================================
# EXPORT ALL MODELS
# ============================================================================

__all__ = [
    # Customer
    "Customer",
    
    # Orders
    "Order",
    "OrderItem",
    
    # Courier
    "Courier",
    
    # Menu
    "MenuItem",
    "MenuCategory",
    
    # Receipt
    "BonTeller",
    
    # Favorites
    "FavoriteOrder",
    
    # Notes
    "CustomerNote",
    
    # Inventory
    "Ingredient",
    "Recipe",
    "InventoryTransaction",
]
