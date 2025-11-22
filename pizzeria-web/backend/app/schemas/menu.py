"""
Menu Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class MenuItemBase(BaseModel):
    """Base menu item schema."""
    naam: str = Field(..., max_length=200)
    categorie: str = Field(..., max_length=100)
    prijs: float = Field(..., gt=0)
    beschrijving: Optional[str] = None
    beschikbaar: int = Field(default=1, ge=0, le=1)
    volgorde: int = Field(default=0)


class MenuItemCreate(MenuItemBase):
    """Schema for creating a menu item."""
    pass


class MenuItemUpdate(BaseModel):
    """Schema for updating a menu item."""
    naam: Optional[str] = Field(None, max_length=200)
    categorie: Optional[str] = Field(None, max_length=100)
    prijs: Optional[float] = Field(None, gt=0)
    beschrijving: Optional[str] = None
    beschikbaar: Optional[int] = Field(None, ge=0, le=1)
    volgorde: Optional[int] = None


class MenuItemResponse(MenuItemBase):
    """Schema for menu item response."""
    id: int
    
    class Config:
        from_attributes = True


class MenuCategoryBase(BaseModel):
    """Base menu category schema."""
    naam: str = Field(..., max_length=100)
    volgorde: int = Field(default=0)


class MenuCategoryCreate(MenuCategoryBase):
    """Schema for creating a menu category."""
    pass


class MenuCategoryResponse(MenuCategoryBase):
    """Schema for menu category response."""
    id: int
    
    class Config:
        from_attributes = True


class MenuResponse(BaseModel):
    """Complete menu response with categories and items."""
    categories: List[MenuCategoryResponse]
    items: List[MenuItemResponse]


