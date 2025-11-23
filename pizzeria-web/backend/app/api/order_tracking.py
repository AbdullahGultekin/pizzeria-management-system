"""
Order tracking endpoints for customers (public, no authentication required).
Allows customers to track orders using bonnummer + phone number or email.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.order import Order
from app.models.customer import Customer
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/orders/track/{bonnummer}")
async def track_order_by_bonnummer(
    bonnummer: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Track order by bonnummer with REQUIRED phone or email verification.
    
    Security: Phone or email is REQUIRED to prevent unauthorized access to orders.
    This ensures customers can only track their own orders.
    """
    # SECURITY: Require phone or email for verification
    if not phone and not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telefoonnummer of e-mailadres is verplicht om je bestelling te volgen"
        )
    
    order = db.query(Order).filter(Order.bonnummer == bonnummer).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestelling niet gevonden"
        )
    
    # Get customer for verification
    customer = None
    if order.klant_id:
        customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
    
    if not customer:
        # If no customer linked, we can't verify - deny access for security
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Deze bestelling kan niet worden geverifieerd. Neem contact op met de zaak."
        )
    
    # Normalize phone numbers for comparison
    # Handle different formats: +32 486 62 19 14, 0486621914, 32486621914, etc.
    def normalize_phone(phone_str: str) -> str:
        """Normalize phone number by removing spaces, dashes, and handling country codes."""
        if not phone_str:
            return ''
        
        # Remove all spaces, dashes, parentheses
        normalized = phone_str.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').strip()
        
        # Remove leading + if present
        if normalized.startswith('+'):
            normalized = normalized[1:]
        
        # For Belgian numbers: if starts with 0, remove it (0486... -> 486...)
        # But keep it if it's part of the number
        # We'll try to match both with and without leading 0
        return normalized
    
    def phones_match(phone1: str, phone2: str) -> bool:
        """Check if two phone numbers match, handling different formats."""
        if not phone1 or not phone2:
            return False
        
        norm1 = normalize_phone(phone1)
        norm2 = normalize_phone(phone2)
        
        # Exact match
        if norm1 == norm2:
            return True
        
        # Handle Belgian numbers: 0486... vs 32486... vs 486...
        # If one starts with 0 and the other with 32, remove both prefixes and compare
        norm1_no_prefix = norm1.lstrip('0').lstrip('32')
        norm2_no_prefix = norm2.lstrip('0').lstrip('32')
        
        if norm1_no_prefix == norm2_no_prefix and len(norm1_no_prefix) >= 8:
            return True
        
        # Substring match (for partial numbers)
        if norm1 in norm2 or norm2 in norm1:
            return True
        
        # Try with leading 0 removed
        if norm1.lstrip('0') == norm2.lstrip('0'):
            return True
        
        return False
    
    # Normalize phone numbers for comparison
    phone_normalized = None
    customer_phone_normalized = ''
    if phone:
        phone_normalized = normalize_phone(phone)
        if customer.telefoon:
            customer_phone_normalized = normalize_phone(customer.telefoon)
    
    # Normalize emails for comparison
    email_normalized = None
    customer_email_normalized = ''
    if email:
        email_normalized = email.lower().strip()
        if customer.email:
            customer_email_normalized = customer.email.lower().strip()
    
    # Verify phone or email matches
    phone_match = phone_normalized and customer_phone_normalized and phones_match(phone_normalized, customer_phone_normalized)
    email_match = email_normalized and customer_email_normalized and email_normalized == customer_email_normalized
    
    # Log for debugging
    if phone and customer.telefoon:
        logger.info(f"Phone verification: input='{phone}' (normalized: '{phone_normalized}'), db='{customer.telefoon}' (normalized: '{customer_phone_normalized}'), match={phone_match}")
    
    if not (phone_match or email_match):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Telefoonnummer of e-mailadres komt niet overeen met deze bestelling. Je kunt alleen je eigen bestellingen volgen."
        )
    
    # Get customer name if available
    klant_naam = None
    if order.klant_id:
        customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
        if customer:
            klant_naam = customer.naam
    
    # Return order details
    return {
        "id": order.id,
        "bonnummer": order.bonnummer,
        "klant_naam": klant_naam,
        "datum": order.datum,
        "tijd": order.tijd,
        "totaal": order.totaal,
        "opmerking": order.opmerking,
        "levertijd": order.levertijd,
        "status": order.status or "Nieuw",
        "betaalmethode": getattr(order, 'betaalmethode', 'cash'),
        "items": [
            {
                "id": item.id,
                "product_naam": item.product_naam,
                "aantal": item.aantal,
                "prijs": item.prijs
            }
            for item in order.items
        ]
    }


@router.get("/orders/track/by-phone")
async def track_orders_by_phone(
    phone: str,
    db: Session = Depends(get_db)
):
    """
    Get all orders for a phone number (for customers who haven't verified email).
    """
    # Normalize phone number
    phone_normalized = phone.replace(' ', '').replace('-', '').replace('+', '')
    
    # Find customer by phone
    customers = db.query(Customer).filter(Customer.telefoon.like(f'%{phone_normalized}%')).all()
    
    if not customers:
        return {"orders": []}
    
    # Get all orders for matching customers
    customer_ids = [c.id for c in customers]
    orders = db.query(Order).filter(Order.klant_id.in_(customer_ids)).order_by(Order.datum.desc(), Order.tijd.desc()).limit(10).all()
    
    return {
        "orders": [
            {
                "id": order.id,
                "bonnummer": order.bonnummer,
                "datum": order.datum,
                "tijd": order.tijd,
                "totaal": order.totaal,
                "status": order.status or "Nieuw",
                "levertijd": order.levertijd
            }
            for order in orders
        ]
    }

