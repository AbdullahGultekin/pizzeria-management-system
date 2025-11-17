"""Service layer for customer business logic."""

from typing import Optional, Dict, Any, List
from repositories.customer_repository import CustomerRepository
from database import update_klant_statistieken
from logging_config import get_logger

logger = get_logger("pizzeria.services.customer")


class CustomerService:
    """Service for customer-related business operations."""
    
    def __init__(self, repository: Optional[CustomerRepository] = None):
        """
        Initialize customer service.
        
        Args:
            repository: Optional customer repository (defaults to new instance)
        """
        self.repository = repository or CustomerRepository()
    
    def find_customer(self, telefoon: str) -> Optional[Dict[str, Any]]:
        """
        Find customer by phone number.
        
        Args:
            telefoon: Phone number
            
        Returns:
            Customer data or None
        """
        return self.repository.find_by_phone(telefoon)
    
    def search_customers(self, telefoon_pattern: str) -> List[Dict[str, Any]]:
        """
        Search customers by phone pattern.
        
        Args:
            telefoon_pattern: Phone number pattern
            
        Returns:
            List of matching customers
        """
        return self.repository.find_by_phone_like(telefoon_pattern)
    
    def create_or_update_customer(
        self,
        telefoon: str,
        straat: str,
        huisnummer: str,
        plaats: str,
        naam: str
    ) -> int:
        """
        Create or update customer.
        
        Args:
            telefoon: Phone number
            straat: Street
            huisnummer: House number
            plaats: City
            naam: Name
            
        Returns:
            Customer ID
        """
        klant_id = self.repository.create_or_update(telefoon, straat, huisnummer, plaats, naam)
        logger.info(f"Customer {'updated' if klant_id else 'created'}: {telefoon}")
        return klant_id
    
    def get_customer(self, klant_id: int) -> Optional[Dict[str, Any]]:
        """
        Get customer by ID.
        
        Args:
            klant_id: Customer ID
            
        Returns:
            Customer data or None
        """
        return self.repository.get_by_id(klant_id)
    
    def update_customer_statistics(self, klant_id: int) -> None:
        """
        Update customer statistics (order count, total spent, last order).
        
        Args:
            klant_id: Customer ID
        """
        update_klant_statistieken(klant_id)
        logger.debug(f"Updated statistics for customer {klant_id}")



