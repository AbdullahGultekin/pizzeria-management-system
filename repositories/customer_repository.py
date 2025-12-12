"""Repository for customer data access operations."""

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


class CustomerRepository:
    """Repository for customer-related database operations."""
    
    @staticmethod
    def find_by_phone(telefoon: str) -> Optional[Dict[str, Any]]:
        """
        Find customer by phone number.
        
        Args:
            telefoon: Phone number to search for
            
        Returns:
            Customer data as dict or None if not found
        """
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM klanten WHERE telefoon = ?",
                (telefoon,)
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
        
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            # Check if customer exists
            cursor.execute("SELECT id FROM klanten WHERE telefoon = ?", (telefoon,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing customer
                cursor.execute(
                    "UPDATE klanten SET straat = ?, huisnummer = ?, plaats = ?, naam = ? WHERE telefoon = ?",
                    (straat, huisnummer, plaats, normalized_naam, telefoon)
                )
                return existing['id']
            else:
                # Create new customer
                cursor.execute(
                    "INSERT INTO klanten (telefoon, straat, huisnummer, plaats, naam) VALUES (?, ?, ?, ?, ?)",
                    (telefoon, straat, huisnummer, plaats, normalized_naam)
                )
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



