"""
Menu database models.
"""
from sqlalchemy import Column, Integer, String, Float, Text
from app.core.database import Base


class MenuCategory(Base):
    """Menu category model."""
    __tablename__ = "menu_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    naam = Column(String, unique=True, nullable=False)
    volgorde = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<MenuCategory(id={self.id}, naam={self.naam})>"


class MenuItem(Base):
    """Menu item model."""
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    naam = Column(String, nullable=False)
    categorie = Column(String, nullable=False)
    prijs = Column(Float, nullable=False)
    beschrijving = Column(Text)
    beschikbaar = Column(Integer, default=1)  # 1 = available, 0 = not available
    volgorde = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<MenuItem(id={self.id}, naam={self.naam}, prijs={self.prijs})>"


