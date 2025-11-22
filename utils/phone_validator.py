"""
Phone number validation utility for European countries.
Used by the Kassa system for validating customer phone numbers.
"""
try:
    import phonenumbers
    from phonenumbers import NumberParseException, PhoneNumberFormat
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False
    phonenumbers = None
    NumberParseException = Exception
    PhoneNumberFormat = None

from typing import Optional, Tuple
from logging_config import get_logger

logger = get_logger("pizzeria.validation.phone")

# EU country codes
EU_COUNTRIES = [
    'BE',  # Belgium
    'NL',  # Netherlands
    'DE',  # Germany
    'FR',  # France
    'ES',  # Spain
    'IT',  # Italy
    'PT',  # Portugal
    'AT',  # Austria
    'CH',  # Switzerland
    'LU',  # Luxembourg
    'DK',  # Denmark
    'SE',  # Sweden
    'NO',  # Norway
    'FI',  # Finland
    'PL',  # Poland
    'CZ',  # Czech Republic
    'SK',  # Slovakia
    'HU',  # Hungary
    'RO',  # Romania
    'BG',  # Bulgaria
    'GR',  # Greece
    'IE',  # Ireland
    'GB',  # United Kingdom
    'EE',  # Estonia
    'LV',  # Latvia
    'LT',  # Lithuania
    'SI',  # Slovenia
    'HR',  # Croatia
    'CY',  # Cyprus
    'MT',  # Malta
]


def validate_phone_number(phone: str, default_region: str = 'BE') -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate phone number for European countries.
    
    Args:
        phone: Phone number to validate
        default_region: Default country code (default: BE for Belgium)
        
    Returns:
        Tuple of (is_valid, normalized_number, error_message)
        - is_valid: True if phone number is valid
        - normalized_number: E.164 formatted number (e.g., +32123456789) or None
        - error_message: Error message if invalid, None if valid
    """
    if not PHONENUMBERS_AVAILABLE:
        # Fallback to basic validation if phonenumbers is not available
        logger.warning("phonenumbers library not available, using basic validation")
        return _basic_validate_phone(phone)
    
    if not phone or not phone.strip():
        return False, None, "Telefoonnummer is verplicht"
    
    # Try to parse with default region first
    try:
        parsed_number = phonenumbers.parse(phone, default_region)
    except NumberParseException as e:
        # Try parsing as international number
        try:
            parsed_number = phonenumbers.parse(phone, None)
        except NumberParseException:
            return False, None, f"Ongeldig telefoonnummer formaat"
    
    # Check if number is valid
    if not phonenumbers.is_valid_number(parsed_number):
        # Try to get a more specific error
        region_code = phonenumbers.region_code_for_number(parsed_number)
        if region_code:
            return False, None, f"Ongeldig telefoonnummer voor {region_code}"
        return False, None, "Ongeldig telefoonnummer"
    
    # Check if number is from EU country
    region_code = phonenumbers.region_code_for_number(parsed_number)
    if region_code and region_code.upper() not in EU_COUNTRIES:
        return False, None, f"Alleen telefoonnummers uit EU-landen zijn toegestaan. Gevonden: {region_code}"
    
    # Normalize to E.164 format
    normalized = phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
    
    return True, normalized, None


def _basic_validate_phone(phone: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Basic phone validation fallback when phonenumbers library is not available.
    Only validates Belgian numbers.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (is_valid, normalized_number, error_message)
    """
    import re
    
    if not phone or not phone.strip():
        return False, None, "Telefoonnummer is verplicht"
    
    # Remove common separators
    normalized = re.sub(r'[\s\-\(\)]', '', phone.strip())
    
    # Basic validation - Belgian phone numbers
    if re.match(r'^(\+32|0)[1-9]\d{8}$', normalized):
        # Convert to E.164 format if needed
        if normalized.startswith('0'):
            normalized = '+32' + normalized[1:]
        return True, normalized, None
    
    return False, None, "Ongeldig telefoonnummer formaat (alleen Belgische nummers zonder phonenumbers library)"


def format_phone_number(phone: str, region: str = 'BE') -> Optional[str]:
    """
    Format phone number to E.164 format.
    
    Args:
        phone: Phone number to format
        region: Country code
        
    Returns:
        Formatted phone number in E.164 format or None if invalid
    """
    is_valid, normalized, _ = validate_phone_number(phone, region)
    return normalized if is_valid else None


def format_phone_for_display(phone: str, region: str = 'BE') -> Optional[str]:
    """
    Format phone number for display (national format).
    
    Args:
        phone: Phone number in E.164 format
        region: Country code for formatting
        
    Returns:
        Formatted phone number for display or None if invalid
    """
    if not PHONENUMBERS_AVAILABLE:
        return phone
    
    try:
        parsed_number = phonenumbers.parse(phone, region)
        if phonenumbers.is_valid_number(parsed_number):
            return phonenumbers.format_number(parsed_number, PhoneNumberFormat.NATIONAL)
    except NumberParseException:
        pass
    return phone  # Return original if cannot format

