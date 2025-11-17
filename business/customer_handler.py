"""Customer management business logic."""

from typing import Optional
from services.customer_service import CustomerService
from logging_config import get_logger

logger = get_logger("pizzeria.business.customer")


class CustomerHandler:
    """Handler for customer-related business operations."""
    
    def __init__(self, customer_service: Optional[CustomerService] = None):
        """
        Initialize customer handler.
        
        Args:
            customer_service: Optional customer service (defaults to new instance)
        """
        self.customer_service = customer_service or CustomerService()
    
    def auto_fill_customer_data(
        self,
        telefoon: str,
        naam_entry,
        adres_entry,
        nr_entry,
        postcode_var,
        postcodes: list
    ) -> None:
        """
        Auto-fill customer form fields based on phone number.
        
        Args:
            telefoon: Phone number to search for
            naam_entry: Name entry widget
            adres_entry: Address entry widget
            nr_entry: House number entry widget
            postcode_var: Postcode StringVar
            postcodes: List of available postcodes
        """
        if not telefoon or not telefoon.strip():
            return
        
        klant = self.customer_service.find_customer(telefoon.strip())
        
        if klant:
            naam_entry.delete(0, 'end')
            naam_entry.insert(0, klant.get('naam', '') or "")
            adres_entry.delete(0, 'end')
            adres_entry.insert(0, klant.get('straat', '') or "")
            nr_entry.delete(0, 'end')
            nr_entry.insert(0, klant.get('huisnummer', '') or "")
            
            plaats = klant.get('plaats', '') or ""
            gevonden_postcode = ""
            for p in postcodes:
                if plaats in p:
                    gevonden_postcode = p
                    break
            postcode_var.set(gevonden_postcode if gevonden_postcode else postcodes[0])
        else:
            naam_entry.delete(0, 'end')
            adres_entry.delete(0, 'end')
            nr_entry.delete(0, 'end')
            postcode_var.set(postcodes[0])
    
    def create_or_update_customer(
        self,
        telefoon: str,
        adres: str,
        nr: str,
        postcode_plaats: str,
        naam: str
    ) -> int:
        """
        Create or update customer in database.
        
        Args:
            telefoon: Phone number
            adres: Street address
            nr: House number
            postcode_plaats: Postcode and city
            naam: Customer name
            
        Returns:
            Customer ID
        """
        return self.customer_service.create_or_update_customer(
            telefoon=telefoon,
            straat=adres,
            huisnummer=nr,
            plaats=postcode_plaats,
            naam=naam
        )



