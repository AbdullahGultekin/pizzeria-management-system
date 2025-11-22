"""Service layer for order business logic."""

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from repositories.order_repository import OrderRepository
from repositories.customer_repository import CustomerRepository
from database import get_next_bonnummer, update_klant_statistieken, boek_voorraad_verbruik
from exceptions import ValidationError, DatabaseError
from logging_config import get_logger

logger = get_logger("pizzeria.services.order")


class OrderService:
    """Service for order-related business operations."""
    
    def __init__(
        self,
        order_repository: Optional[OrderRepository] = None,
        customer_repository: Optional[CustomerRepository] = None
    ):
        """
        Initialize order service.
        
        Args:
            order_repository: Optional order repository (defaults to new instance)
            customer_repository: Optional customer repository (defaults to new instance)
        """
        self.order_repository = order_repository or OrderRepository()
        self.customer_repository = customer_repository or CustomerRepository()
    
    def create_order(
        self,
        klant_telefoon: str,
        order_items: List[Dict[str, Any]],
        opmerking: Optional[str] = None,
        koerier_id: Optional[int] = None,
        levertijd: Optional[str] = None,
        korting_percentage: float = 0.0,
        afhaal: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Create a new order.
        
        Args:
            klant_telefoon: Customer phone number
            order_items: List of order items
            opmerking: Optional order notes
            koerier_id: Optional courier ID
            levertijd: Optional delivery time (e.g., "19:30")
            korting_percentage: Optional discount percentage (default: 0.0)
            
        Returns:
            Tuple of (success, bonnummer)
            
        Raises:
            ValidationError: If order data is invalid
            DatabaseError: If database operation fails
        """
        if not klant_telefoon or not klant_telefoon.strip():
            raise ValidationError("Telefoonnummer is verplicht")
        
        if not order_items:
            raise ValidationError("Bestelling moet minimaal één item bevatten")
        
        # Calculate subtotal
        subtotaal = sum(item.get('prijs', 0) * item.get('aantal', 0) for item in order_items)
        
        if subtotaal <= 0:
            raise ValidationError("Totaalprijs moet groter zijn dan 0")
        
        # Apply discount if applicable
        korting_bedrag = 0.0
        totaal = subtotaal
        
        if korting_percentage > 0 and subtotaal > 0:
            korting_bedrag = round(subtotaal * (korting_percentage / 100), 2)
            totaal = subtotaal - korting_bedrag
        
        # Get or create customer
        klant = self.customer_repository.find_by_phone(klant_telefoon)
        if not klant:
            raise ValidationError(f"Klant met telefoonnummer {klant_telefoon} niet gevonden")
        
        klant_id = klant['id']
        
        # Get receipt number
        bonnummer = get_next_bonnummer()
        
        # Create order
        nu = datetime.now()
        bestelling_id = self.order_repository.create(
            klant_id=klant_id,
            datum=nu.strftime('%Y-%m-%d'),
            tijd=nu.strftime('%H:%M'),
            totaal=totaal,
            opmerking=opmerking,
            bonnummer=bonnummer,
            koerier_id=koerier_id,
            levertijd=levertijd,
            afhaal=afhaal
        )
        
        # Add order items
        for item in order_items:
            self.order_repository.add_order_item(
                bestelling_id=bestelling_id,
                categorie=item.get('categorie', ''),
                product=item.get('product', ''),
                aantal=item.get('aantal', 1),
                prijs=item.get('prijs', 0),
                extras=item.get('extras')
            )
        
        # Update customer statistics
        update_klant_statistieken(klant_id)
        
        # Book inventory usage
        boek_voorraad_verbruik(bestelling_id)
        
        logger.info(f"Order created: {bestelling_id}, bonnummer: {bonnummer}")
        return True, bonnummer
    
    def get_order(self, bestelling_id: int) -> Optional[Dict[str, Any]]:
        """
        Get order by ID with all details.
        
        Args:
            bestelling_id: Order ID
            
        Returns:
            Order data with items or None
        """
        order = self.order_repository.get_by_id(bestelling_id)
        if order:
            order['items'] = self.order_repository.get_order_items(bestelling_id)
        return order
    
    def get_orders_by_date(self, datum: str) -> List[Dict[str, Any]]:
        """
        Get all orders for a specific date.
        
        Args:
            datum: Date in YYYY-MM-DD format
            
        Returns:
            List of orders
        """
        return self.order_repository.get_by_date(datum)
    
    def get_customer_orders(self, klant_id: int) -> List[Dict[str, Any]]:
        """
        Get all orders for a customer.
        
        Args:
            klant_id: Customer ID
            
        Returns:
            List of orders
        """
        return self.order_repository.get_by_customer(klant_id)
    
    def assign_courier(self, bestelling_id: int, koerier_id: Optional[int]) -> None:
        """
        Assign or remove courier from order.
        
        Args:
            bestelling_id: Order ID
            koerier_id: Courier ID or None to remove
        """
        self.order_repository.update_courier(bestelling_id, koerier_id)
        logger.info(f"Courier {'assigned' if koerier_id else 'removed'} to order {bestelling_id}")
    
    def delete_order(self, bestelling_id: int) -> None:
        """
        Delete an order.
        
        Args:
            bestelling_id: Order ID to delete
        """
        # Get order to find customer for statistics update
        order = self.order_repository.get_by_id(bestelling_id)
        if order:
            klant_id = order.get('klant_id')
            self.order_repository.delete(bestelling_id)
            if klant_id:
                update_klant_statistieken(klant_id)
            logger.info(f"Order deleted: {bestelling_id}")
        else:
            raise ValidationError(f"Order {bestelling_id} niet gevonden")

