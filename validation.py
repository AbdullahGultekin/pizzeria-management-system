"""
Input validation utilities for the pizzeria application.
"""
import re
from typing import Optional
from logging_config import get_logger
from exceptions import ValidationError

logger = get_logger("pizzeria.validation")


def validate_phone(phone: str) -> str:
    """
    Validate and normalize phone number.
    
    Args:
        phone: Phone number string
        
    Returns:
        Normalized phone number
        
    Raises:
        ValidationError: If phone number is invalid
    """
    if not phone or not phone.strip():
        raise ValidationError("Telefoonnummer is verplicht")
    
    # Remove common separators
    normalized = re.sub(r'[\s\-\(\)]', '', phone.strip())
    
    # Basic validation - Belgian phone numbers
    if not re.match(r'^(\+32|0)[1-9]\d{8}$', normalized):
        raise ValidationError("Ongeldig telefoonnummer formaat")
    
    return normalized


def validate_postcode(postcode: str, allowed_postcodes: list) -> str:
    """
    Validate postcode against allowed list.
    
    Args:
        postcode: Postcode string
        allowed_postcodes: List of allowed postcodes
        
    Returns:
        Validated postcode
        
    Raises:
        ValidationError: If postcode is not in allowed list
    """
    if not postcode or not postcode.strip():
        raise ValidationError("Postcode is verplicht")
    
    postcode = postcode.strip()
    if postcode not in allowed_postcodes:
        raise ValidationError(f"Postcode {postcode} is niet in het bezorggebied")
    
    return postcode


def validate_name(name: str, required: bool = False) -> Optional[str]:
    """
    Validate customer name.
    
    Args:
        name: Name string
        required: Whether name is required
        
    Returns:
        Validated name or None
        
    Raises:
        ValidationError: If name is invalid
    """
    if not name or not name.strip():
        if required:
            raise ValidationError("Naam is verplicht")
        return None
    
    name = name.strip()
    if len(name) < 2:
        raise ValidationError("Naam moet minimaal 2 tekens lang zijn")
    
    if len(name) > 100:
        raise ValidationError("Naam is te lang (maximaal 100 tekens)")
    
    # Basic validation - allow letters, spaces, hyphens, apostrophes
    if not re.match(r'^[a-zA-Z\s\-\']+$', name):
        raise ValidationError("Naam bevat ongeldige tekens")
    
    return name


def validate_address(address: str, required: bool = True) -> str:
    """
    Validate street address.
    
    Args:
        address: Street address string
        required: Whether address is required
        
    Returns:
        Validated address
        
    Raises:
        ValidationError: If address is invalid
    """
    if not address or not address.strip():
        if required:
            raise ValidationError("Adres is verplicht")
        return ""
    
    address = address.strip()
    if len(address) < 3:
        raise ValidationError("Adres moet minimaal 3 tekens lang zijn")
    
    if len(address) > 200:
        raise ValidationError("Adres is te lang (maximaal 200 tekens)")
    
    return address


def validate_house_number(number: str, required: bool = True) -> str:
    """
    Validate house number.
    
    Args:
        number: House number string
        required: Whether house number is required
        
    Returns:
        Validated house number
        
    Raises:
        ValidationError: If house number is invalid
    """
    if not number or not number.strip():
        if required:
            raise ValidationError("Huisnummer is verplicht")
        return ""
    
    number = number.strip()
    if len(number) > 20:
        raise ValidationError("Huisnummer is te lang")
    
    return number


def validate_price(price: float, min_price: float = 0.0, max_price: float = 10000.0) -> float:
    """
    Validate price.
    
    Args:
        price: Price value
        min_price: Minimum allowed price
        max_price: Maximum allowed price
        
    Returns:
        Validated price
        
    Raises:
        ValidationError: If price is invalid
    """
    try:
        price_float = float(price)
    except (ValueError, TypeError):
        raise ValidationError("Ongeldige prijs")
    
    if price_float < min_price:
        raise ValidationError(f"Prijs moet minimaal {min_price:.2f} zijn")
    
    if price_float > max_price:
        raise ValidationError(f"Prijs mag maximaal {max_price:.2f} zijn")
    
    return round(price_float, 2)


def validate_quantity(quantity: int, min_qty: int = 1, max_qty: int = 100) -> int:
    """
    Validate quantity.
    
    Args:
        quantity: Quantity value
        min_qty: Minimum allowed quantity
        max_qty: Maximum allowed quantity
        
    Returns:
        Validated quantity
        
    Raises:
        ValidationError: If quantity is invalid
    """
    try:
        qty_int = int(quantity)
    except (ValueError, TypeError):
        raise ValidationError("Ongeldige hoeveelheid")
    
    if qty_int < min_qty:
        raise ValidationError(f"Hoeveelheid moet minimaal {min_qty} zijn")
    
    if qty_int > max_qty:
        raise ValidationError(f"Hoeveelheid mag maximaal {max_qty} zijn")
    
    return qty_int


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Remove control characters except newlines and tabs
    sanitized = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', str(value))
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return sanitized.strip()



