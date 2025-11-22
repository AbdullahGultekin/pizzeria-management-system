"""
Input validation utilities for the pizzeria application.
"""
import re
from typing import Optional
from logging_config import get_logger
from exceptions import ValidationError

# Import phone validator with fallback
try:
    # Try to import phonenumbers directly
    import phonenumbers
    from phonenumbers import NumberParseException, PhoneNumberFormat
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False
    phonenumbers = None
    NumberParseException = Exception
    PhoneNumberFormat = None

# EU country codes for validation
EU_COUNTRIES = [
    'BE', 'NL', 'DE', 'FR', 'ES', 'IT', 'PT', 'AT', 'CH', 'LU',
    'DK', 'SE', 'NO', 'FI', 'PL', 'CZ', 'SK', 'HU', 'RO', 'BG',
    'GR', 'IE', 'GB', 'EE', 'LV', 'LT', 'SI', 'HR', 'CY', 'MT',
]

logger = get_logger("pizzeria.validation")


def validate_phone(phone: str) -> str:
    """
    Validate and normalize phone number for all EU countries (including landlines).
    
    Uses the phonenumbers library if available, otherwise falls back to basic validation.
    
    Args:
        phone: Phone number string
        
    Returns:
        Normalized phone number in E.164 format (e.g., +32123456789)
        
    Raises:
        ValidationError: If phone number is invalid
    """
    if not phone or not phone.strip():
        raise ValidationError("Telefoonnummer is verplicht")
    
    phone = phone.strip()
    
    # Use phonenumbers library if available
    if PHONENUMBERS_AVAILABLE:
        try:
            # Try to parse with default region (Belgium) first
            parsed_number = phonenumbers.parse(phone, 'BE')
        except NumberParseException:
            # Try parsing as international number
            try:
                parsed_number = phonenumbers.parse(phone, None)
            except NumberParseException as e:
                raise ValidationError("Ongeldig telefoonnummer formaat")
        
        # Check if number is valid
        if not phonenumbers.is_valid_number(parsed_number):
            region_code = phonenumbers.region_code_for_number(parsed_number)
            if region_code:
                raise ValidationError(f"Ongeldig telefoonnummer voor {region_code}")
            raise ValidationError("Ongeldig telefoonnummer")
        
        # Check if number is from EU country
        region_code = phonenumbers.region_code_for_number(parsed_number)
        if region_code and region_code.upper() not in EU_COUNTRIES:
            raise ValidationError(f"Alleen telefoonnummers uit EU-landen zijn toegestaan. Gevonden: {region_code}")
        
        # Normalize to E.164 format
        normalized = phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
        return normalized
    
    # Fallback to basic validation (only Belgian numbers)
    # This is used when phonenumbers library is not available
    normalized = re.sub(r'[\s\-\(\)\-\.]', '', phone)
    
    # Basic validation - Belgian phone numbers (mobiel en vast)
    # Belgische nummers: 0 gevolgd door 1-9, dan 8 meer cijfers = totaal 9 cijfers na 0
    # Voorbeeld: 037757228 (vast), 0477123456 (mobiel)
    belgian_pattern = r'^(\+32|0)[1-9]\d{8}$'
    
    if re.match(belgian_pattern, normalized):
        # Convert to E.164 format if needed
        if normalized.startswith('0'):
            normalized = '+32' + normalized[1:]
        return normalized
    
    # Also accept international format starting with +32 (already in E.164)
    if normalized.startswith('+32') and len(normalized) == 12:  # +32 + 9 digits
        return normalized
    
    # If we get here and phonenumbers is not available, show helpful error
    if not PHONENUMBERS_AVAILABLE:
        logger.warning(f"Phone validation failed for: {phone} (phonenumbers not available)")
        raise ValidationError(
            f"Ongeldig telefoonnummer formaat: '{phone}'. "
            "Installeer 'phonenumbers' voor ondersteuning van alle EU-landen: pip install phonenumbers"
        )
    
    # This should not be reached, but just in case
    raise ValidationError(f"Ongeldig telefoonnummer formaat: '{phone}'")


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
    
    Accepts any string including text like "bus 101", "123A", "12-14", etc.
    Only validates length, not format, to allow flexibility for different address formats.
    
    Args:
        number: House number string (can contain letters, numbers, spaces, hyphens, etc.)
        required: Whether house number is required
        
    Returns:
        Validated house number (trimmed)
        
    Raises:
        ValidationError: If house number is invalid (empty when required, or too long)
    """
    if not number or not number.strip():
        if required:
            raise ValidationError("Huisnummer is verplicht")
        return ""
    
    number = number.strip()
    if len(number) > 20:
        raise ValidationError("Huisnummer is te lang (maximaal 20 tekens)")
    
    # Accept any characters - house numbers can be "123", "123A", "bus 101", "12-14", etc.
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



