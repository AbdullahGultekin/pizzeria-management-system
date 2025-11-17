"""
Application state management to replace global variables.
"""
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from tkinter import StringVar, Entry

from logging_config import get_logger

logger = get_logger("pizzeria.state")


@dataclass
class MenuState:
    """State for menu navigation."""
    categorie: Optional[str] = None
    producten: List[Dict[str, Any]] = field(default_factory=list)
    page: int = 0
    page_size: int = 10
    gekozen_product: Optional[Dict[str, Any]] = None


@dataclass
class OrderItem:
    """Represents a single order item."""
    categorie: str
    product: str
    aantal: int
    prijs: float
    base_price: float
    extras: Dict[str, Any] = field(default_factory=dict)
    opmerking: str = ""


@dataclass
class CustomerData:
    """Customer information for current order."""
    telefoon: str = ""
    naam: str = ""
    adres: str = ""
    nr: str = ""
    postcode_gemeente: str = ""
    opmerking: str = ""
    
    def is_valid(self) -> bool:
        """Check if customer data is valid for order."""
        return bool(self.telefoon.strip())


@dataclass
class ApplicationState:
    """Main application state container."""
    # Menu data
    menu_data: Dict[str, Any] = field(default_factory=dict)
    extras_data: Dict[str, Any] = field(default_factory=dict)
    
    # Menu navigation state
    menu_state: MenuState = field(default_factory=MenuState)
    
    # Current order
    order_items: List[Dict[str, Any]] = field(default_factory=list)  # Using dict for compatibility
    
    # Current customer data
    customer_data: CustomerData = field(default_factory=CustomerData)
    
    # Control state (for UI state management)
    ctrl: Dict[str, Any] = field(default_factory=dict)
    
    # Settings
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # Postcodes (delivery areas)
    postcodes: List[str] = field(default_factory=lambda: [
        "2070 Zwijndrecht", "4568 Nieuw-Namen", "9100 Nieuwkerken-Waas",
        "9100 Sint-Niklaas", "9120 Beveren", "9120 Vrasene", "9120 Haasdonk",
        "9120 Kallo", "9120 Melsele", "9130 Verrebroek", "9130 Kieldrecht",
        "9130 Doel", "9170 Klein meerdonk", "9170 Meerdonk",
        "9170 Sint-Gillis-Waas", "9170 De Klinge"
    ])
    
    # UI references (optional, for dependency injection)
    telefoon_entry: Optional['Entry'] = None
    naam_entry: Optional['Entry'] = None
    adres_entry: Optional['Entry'] = None
    nr_entry: Optional['Entry'] = None
    postcode_var: Optional['StringVar'] = None
    opmerkingen_entry: Optional['Entry'] = None
    
    def clear_order(self) -> None:
        """Clear the current order."""
        self.order_items.clear()
        logger.debug("Order cleared")
    
    def add_order_item(self, item: Dict[str, Any]) -> None:
        """Add an item to the current order."""
        self.order_items.append(item)
        logger.debug(f"Added order item: {item.get('product', 'unknown')} x{item.get('aantal', 0)}")
    
    def remove_order_item(self, index: int) -> None:
        """Remove an order item by index."""
        if 0 <= index < len(self.order_items):
            removed = self.order_items.pop(index)
            logger.debug(f"Removed order item: {removed.get('product', 'unknown')}")
    
    def get_order_total(self) -> float:
        """Calculate total price of current order."""
        return sum(item.get('prijs', 0) * item.get('aantal', 0) for item in self.order_items)
    
    def clear_customer_data(self) -> None:
        """Clear customer data."""
        self.customer_data = CustomerData()
        logger.debug("Customer data cleared")
    
    def update_customer_data(self, **kwargs) -> None:
        """Update customer data fields."""
        for key, value in kwargs.items():
            if hasattr(self.customer_data, key):
                setattr(self.customer_data, key, value)
        logger.debug(f"Customer data updated: {list(kwargs.keys())}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            "menu_data": self.menu_data,
            "extras_data": self.extras_data,
            "settings": self.settings,
            "order_count": len(self.order_items),
            "order_total": self.get_order_total(),
            "customer_phone": self.customer_data.telefoon
        }

