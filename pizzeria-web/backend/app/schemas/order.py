"""
Order Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class OrderItemBase(BaseModel):
    """Base order item schema."""
    product_naam: str = Field(..., max_length=200)
    product_id: Optional[int] = None  # Product ID from menu for accurate category detection
    aantal: int = Field(..., gt=0)
    prijs: float = Field(..., gt=0)
    opmerking: Optional[str] = None
    extras: Optional[dict] = None  # Extras as dict (vlees, bijgerecht, sauzen, garnering, etc.)


class OrderItemCreate(OrderItemBase):
    """Schema for creating an order item."""
    pass


class OrderItemResponse(OrderItemBase):
    """Schema for order item response."""
    id: int
    bestelling_id: int
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Base order schema."""
    klant_id: Optional[int] = None
    koerier_id: Optional[int] = None
    totaal: float = Field(..., gt=0)
    opmerking: Optional[str] = None
    levertijd: Optional[str] = None
    status: Optional[str] = "Nieuw"
    betaalmethode: Optional[str] = "cash"  # "online" or "cash"
    afstand_km: Optional[float] = None
    online_bestelling: Optional[int] = 0  # 0 = kassa, 1 = online


class OrderCreate(OrderBase):
    """Schema for creating an order."""
    items: List[OrderItemCreate] = Field(..., min_items=1)


class OrderUpdate(BaseModel):
    """Schema for updating an order."""
    koerier_id: Optional[int] = None
    opmerking: Optional[str] = None
    levertijd: Optional[str] = None
    status: Optional[str] = None
    afstand_km: Optional[float] = None


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    new_status: str
    levertijd: Optional[str] = None
    koerier_id: Optional[int] = None


class OrderResponse(OrderBase):
    """Schema for order response."""
    id: int
    datum: str
    tijd: str
    bonnummer: Optional[str] = None
    status: str = "Nieuw"
    items: List[OrderItemResponse] = []
    klant_naam: Optional[str] = None  # Customer name for display
    klant_adres: Optional[str] = None  # Customer address for display
    klant_telefoon: Optional[str] = None  # Customer phone for display
    klant_email: Optional[str] = None  # Customer email for notifications
    
    class Config:
        from_attributes = True

