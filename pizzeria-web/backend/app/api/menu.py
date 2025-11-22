"""
Menu API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.menu import MenuItem, MenuCategory
from app.schemas.menu import (
    MenuItemCreate, MenuItemUpdate, MenuItemResponse,
    MenuCategoryCreate, MenuCategoryResponse, MenuResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


# Public menu endpoint (no authentication required)
@router.get("/menu/public", response_model=MenuResponse)
async def get_public_menu(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get complete menu with categories and items (public endpoint, no authentication required).
    Only returns available items.
    """
    try:
        categories = db.query(MenuCategory).order_by(MenuCategory.volgorde, MenuCategory.naam).all()
        items = db.query(MenuItem).filter(MenuItem.beschikbaar == 1).order_by(MenuItem.volgorde, MenuItem.naam).all()
        
        logger.info(f"Found {len(categories)} categories and {len(items)} items")
        
        # Convert to response format
        categories_data = [
            MenuCategoryResponse(
                id=cat.id,
                naam=cat.naam,
                volgorde=cat.volgorde
            )
            for cat in categories
        ]
        
        items_data = [
            MenuItemResponse(
                id=item.id,
                naam=item.naam,
                categorie=item.categorie,
                prijs=float(item.prijs) if item.prijs is not None else 0.0,
                beschrijving=item.beschrijving or "",
                beschikbaar=1 if item.beschikbaar else 0,
                volgorde=item.volgorde
            )
            for item in items
        ]
        
        return MenuResponse(
            categories=categories_data,
            items=items_data
        )
    except Exception as e:
        logger.error(f"Error in get_public_menu: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fout bij laden menu: {str(e)}"
        )


# Menu endpoints (read-only for kassa, full CRUD for admin)
@router.get("/menu", response_model=MenuResponse)
async def get_menu(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    include_unavailable: bool = False
):
    """
    Get complete menu with categories and items.
    For admin users, can include unavailable items.
    """
    categories = db.query(MenuCategory).order_by(MenuCategory.volgorde, MenuCategory.naam).all()
    query = db.query(MenuItem)
    
    # Only filter by beschikbaar if not admin or not including unavailable
    if not include_unavailable and current_user.get("role") != "admin":
        query = query.filter(MenuItem.beschikbaar == 1)
    
    items = query.order_by(MenuItem.volgorde, MenuItem.naam).all()
    
    return {
        "categories": [
            {
                "id": cat.id,
                "naam": cat.naam,
                "volgorde": cat.volgorde
            }
            for cat in categories
        ],
        "items": [
            {
                "id": item.id,
                "naam": item.naam,
                "categorie": item.categorie,
                "prijs": item.prijs,
                "beschrijving": item.beschrijving,
                "beschikbaar": item.beschikbaar,
                "volgorde": item.volgorde
            }
            for item in items
        ]
    }


@router.get("/menu/items", response_model=List[MenuItemResponse])
async def get_menu_items(
    request: Request,
    categorie: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get menu items, optionally filtered by category.
    """
    query = db.query(MenuItem)
    
    if categorie:
        query = query.filter(MenuItem.categorie == categorie)
    
    items = query.order_by(MenuItem.volgorde, MenuItem.naam).all()
    return items


@router.get("/menu/items/{item_id}", response_model=MenuItemResponse)
async def get_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific menu item.
    """
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item niet gevonden"
        )
    return item


@router.get("/menu/categories", response_model=List[MenuCategoryResponse])
async def get_menu_categories(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all menu categories.
    """
    categories = db.query(MenuCategory).order_by(MenuCategory.volgorde, MenuCategory.naam).all()
    return categories


# Admin-only endpoints
@router.post("/menu/items", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    request: Request,
    item: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    """
    Create a new menu item (admin only).
    """
    db_item = MenuItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    logger.info(f"Menu item created: {db_item.id} - {db_item.naam}")
    return db_item


@router.put("/menu/items/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(
    item_id: int,
    item_update: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    """
    Update a menu item (admin only).
    """
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item niet gevonden"
        )
    
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    logger.info(f"Menu item updated: {item_id}")
    return item


@router.delete("/menu/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    """
    Delete a menu item (admin only).
    """
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item niet gevonden"
        )
    
    db.delete(item)
    db.commit()
    
    logger.info(f"Menu item deleted: {item_id}")
    return None


@router.post("/menu/categories", response_model=MenuCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_category(
    request: Request,
    category: MenuCategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    """
    Create a new menu category (admin only).
    """
    # Check if category already exists
    existing = db.query(MenuCategory).filter(MenuCategory.naam == category.naam).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Categorie met deze naam bestaat al"
        )
    
    db_category = MenuCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    logger.info(f"Menu category created: {db_category.id} - {db_category.naam}")
    return db_category

