"""
Base printer interface and abstract implementation.
"""
from abc import ABC, abstractmethod
from typing import Optional
from logging_config import get_logger

logger = get_logger("pizzeria.printers.base")


class PrinterInterface(ABC):
    """Abstract base class for printer implementations."""
    
    @abstractmethod
    def print_receipt(self, receipt_text: str, qr_data: Optional[str] = None) -> bool:
        """
        Print a receipt.
        
        Args:
            receipt_text: The receipt text to print
            qr_data: Optional QR code data to include
            
        Returns:
            True if printing succeeded, False otherwise
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the printer is available."""
        pass


class PrinterNotAvailableError(Exception):
    """Raised when printer is not available."""
    pass



