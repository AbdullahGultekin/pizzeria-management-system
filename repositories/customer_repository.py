"""Repository for customer data access operations."""

import re
from typing import Optional, Dict, Any, List
from database import DatabaseContext
from logging_config import get_logger

logger = get_logger("pizzeria.repositories.customer")


def normalize_customer_name(naam: str) -> str:
    """
    Normalize customer name: first letter uppercase, rest lowercase.
    
    Args:
        naam: Customer name to normalize
        
    Returns:
        Normalized name with first letter uppercase
    """
    if not naam or not naam.strip():
        return naam
    
    naam = naam.strip()
    # Capitalize first letter, lowercase the rest
    return naam[0].upper() + naam[1:].lower() if len(naam) > 1 else naam.upper()


def normalize_phone_for_search(telefoon: str) -> str:
    """
    Normalize phone number for database search.
    Handles different formats: +32123456789, 0123456789, 0032123456789
    
    Args:
        telefoon: Phone number to normalize
        
    Returns:
        Normalized phone number (E.164 format: +32123456789)
    """
    if not telefoon:
        return telefoon
    
    telefoon = telefoon.strip()
    
    # Remove all spaces, dashes, parentheses, dots
    cleaned = re.sub(r'[\s\-\(\)\-\.]', '', telefoon)
    
    # Convert to E.164 format
    if cleaned.startswith('+32'):
        return cleaned
    elif cleaned.startswith('0032'):
        return '+32' + cleaned[4:]
    elif cleaned.startswith('32') and len(cleaned) == 11:
        return '+' + cleaned
    elif cleaned.startswith('0') and len(cleaned) == 10:
        return '+32' + cleaned[1:]
    
    # Return as-is if already in E.164 or unknown format
    return cleaned


class CustomerRepository:
    """Repository for customer-related database operations."""
    
    @staticmethod
    def find_by_phone(telefoon: str) -> Optional[Dict[str, Any]]:
        """
        Find customer by phone number.
        Tries multiple formats to handle different phone number formats in database.
        
        Args:
            telefoon: Phone number to search for
            
        Returns:
            Customer data as dict or None if not found
        """
        if not telefoon:
            return None
        
        normalized = normalize_phone_for_search(telefoon)
        
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            
            # Try exact match first (normalized format)
            cursor.execute(
                "SELECT * FROM klanten WHERE telefoon = ?",
                (normalized,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            
            # Try alternative formats if normalized doesn't match
            # Convert +32 to 0 format
            if normalized.startswith('+32'):
                alt_format = '0' + normalized[3:]
                cursor.execute(
                    "SELECT * FROM klanten WHERE telefoon = ?",
                    (alt_format,)
                )
                row = cursor.fetchone()
                if row:
                    return dict(row)
            
            # Try 0032 format
            if normalized.startswith('+32'):
                alt_format = '0032' + normalized[3:]
                cursor.execute(
                    "SELECT * FROM klanten WHERE telefoon = ?",
                    (alt_format,)
                )
                row = cursor.fetchone()
                if row:
                    return dict(row)
            
            return None
    
    @staticmethod
    def find_by_phone_like(telefoon_pattern: str) -> List[Dict[str, Any]]:
        """
        Find customers by phone number pattern.
        
        Args:
            telefoon_pattern: Phone number pattern (e.g., "%123%")
            
        Returns:
            List of customer data dictionaries
        """
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, telefoon, naam, straat, huisnummer FROM klanten WHERE telefoon LIKE ?",
                (telefoon_pattern,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def create_or_update(telefoon: str, straat: str, huisnummer: str, plaats: str, naam: str) -> int:
        """
        Create or update customer.
        Normalizes phone number to E.164 format for consistent storage.
        
        Args:
            telefoon: Phone number (unique identifier)
            straat: Street name
            huisnummer: House number
            plaats: City/town
            naam: Customer name
            
        Returns:
            Customer ID
        """
        # Normalize customer name: first letter uppercase, rest lowercase
        normalized_naam = normalize_customer_name(naam)
        
        # Normalize phone number to E.164 format for consistent storage
        normalized_telefoon = normalize_phone_for_search(telefoon)
        
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            # Check if customer exists (try multiple formats)
            existing = None
            existing_id = None
            
            # Try normalized format first
            cursor.execute("SELECT id FROM klanten WHERE telefoon = ?", (normalized_telefoon,))
            row = cursor.fetchone()
            if row:
                existing = row
                existing_id = row['id']
            else:
                # Try alternative formats
                if normalized_telefoon.startswith('+32'):
                    alt_format = '0' + normalized_telefoon[3:]
                    cursor.execute("SELECT id FROM klanten WHERE telefoon = ?", (alt_format,))
                    row = cursor.fetchone()
                    if row:
                        existing = row
                        existing_id = row['id']
                        # Update to normalized format
                        cursor.execute("UPDATE klanten SET telefoon = ? WHERE id = ?", (normalized_telefoon, existing_id))
            
            if existing:
                # Update existing customer - always update address when provided
                # This ensures that if a customer with the same phone number provides
                # a different address, it will be updated
                # Extract postcode from plaats if it contains postcode (format: "9120 Beveren")
                postcode = ""
                gemeente = plaats
                if plaats and " " in plaats:
                    parts = plaats.split(" ", 1)
                    if parts[0].isdigit() and len(parts[0]) == 4:
                        postcode = parts[0]
                        gemeente = parts[1] if len(parts) > 1 else ""
                
                # Check if updated_at column exists
                cursor.execute("PRAGMA table_info(klanten)")
                columns = [row[1] for row in cursor.fetchall()]
                has_updated_at = 'updated_at' in columns
                has_postcode = 'postcode' in columns
                
                if has_updated_at and has_postcode:
                    cursor.execute(
                        "UPDATE klanten SET straat = ?, huisnummer = ?, plaats = ?, postcode = ?, naam = ?, telefoon = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (straat, huisnummer, gemeente, postcode, normalized_naam, normalized_telefoon, existing_id)
                    )
                elif has_updated_at:
                    cursor.execute(
                        "UPDATE klanten SET straat = ?, huisnummer = ?, plaats = ?, naam = ?, telefoon = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (straat, huisnummer, plaats, normalized_naam, normalized_telefoon, existing_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE klanten SET straat = ?, huisnummer = ?, plaats = ?, naam = ?, telefoon = ? WHERE id = ?",
                        (straat, huisnummer, plaats, normalized_naam, normalized_telefoon, existing_id)
                    )
                
                rows_affected = cursor.rowcount
                if rows_affected > 0:
                    logger.info(f"Klant geüpdatet: telefoon={normalized_telefoon}, straat={straat}, huisnummer={huisnummer}, plaats={plaats}")
                else:
                    logger.warning(f"UPDATE klant had geen effect: telefoon={normalized_telefoon}")
                return existing_id
            else:
                # Create new customer with normalized phone number
                # Extract postcode from plaats if it contains postcode
                postcode = ""
                gemeente = plaats
                if plaats and " " in plaats:
                    parts = plaats.split(" ", 1)
                    if parts[0].isdigit() and len(parts[0]) == 4:
                        postcode = parts[0]
                        gemeente = parts[1] if len(parts) > 1 else ""
                
                # Check if new columns exist
                cursor.execute("PRAGMA table_info(klanten)")
                columns = [row[1] for row in cursor.fetchall()]
                has_postcode = 'postcode' in columns
                has_created_at = 'created_at' in columns
                
                if has_postcode and has_created_at:
                    cursor.execute(
                        "INSERT INTO klanten (telefoon, straat, huisnummer, plaats, postcode, naam, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                        (normalized_telefoon, straat, huisnummer, gemeente, postcode, normalized_naam)
                    )
                elif has_created_at:
                    cursor.execute(
                        "INSERT INTO klanten (telefoon, straat, huisnummer, plaats, naam, created_at, updated_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                        (normalized_telefoon, straat, huisnummer, plaats, normalized_naam)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO klanten (telefoon, straat, huisnummer, plaats, naam) VALUES (?, ?, ?, ?, ?)",
                        (normalized_telefoon, straat, huisnummer, plaats, normalized_naam)
                    )
                logger.info(f"Nieuwe klant aangemaakt: telefoon={normalized_telefoon}, straat={straat}, huisnummer={huisnummer}, plaats={plaats}")
                return cursor.lastrowid
    
    @staticmethod
    def get_by_id(klant_id: int) -> Optional[Dict[str, Any]]:
        """
        Get customer by ID.
        
        Args:
            klant_id: Customer ID
            
        Returns:
            Customer data as dict or None if not found
        """
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM klanten WHERE id = ?", (klant_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """
        Get all customers.
        
        Returns:
            List of all customer data dictionaries
        """
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM klanten ORDER BY naam")
            return [dict(row) for row in cursor.fetchall()]



