"""
Password validation utilities.
"""
import re
from typing import Tuple


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Wachtwoord moet minimaal 8 tekens lang zijn"
    
    if not re.search(r'[A-Z]', password):
        return False, "Wachtwoord moet minimaal één hoofdletter bevatten"
    
    if not re.search(r'[a-z]', password):
        return False, "Wachtwoord moet minimaal één kleine letter bevatten"
    
    if not re.search(r'\d', password):
        return False, "Wachtwoord moet minimaal één cijfer bevatten"
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        return False, "Wachtwoord moet minimaal één speciaal teken bevatten (!@#$%^&*()_+-=[]{}|;:,.<>?)"
    
    return True, ""


def is_password_strong_enough(password: str) -> bool:
    """
    Check if password meets strength requirements.
    
    Args:
        password: Password to check
        
    Returns:
        True if password is strong enough, False otherwise
    """
    is_valid, _ = validate_password_strength(password)
    return is_valid


