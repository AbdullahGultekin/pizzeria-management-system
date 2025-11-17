"""
Windows-specific printer implementation using win32print.
"""
import platform
from typing import Optional
from logging_config import get_logger
from .base import PrinterInterface, PrinterNotAvailableError

logger = get_logger("pizzeria.printers.windows")

# Conditionally import Windows-only modules
WIN32PRINT_AVAILABLE = False
if platform.system() == "Windows":
    try:
        import win32print
        WIN32PRINT_AVAILABLE = True
    except ImportError:
        logger.warning("pywin32 niet geïnstalleerd. Windows printer support niet beschikbaar.")
else:
    logger.info("win32print is alleen beschikbaar op Windows.")


class WindowsThermalPrinter(PrinterInterface):
    """Windows thermal printer implementation."""
    
    def __init__(self, printer_name: str = "EPSON TM-T20II Receipt5"):
        """
        Initialize Windows thermal printer.
        
        Args:
            printer_name: Name of the printer as it appears in Windows
        """
        if not WIN32PRINT_AVAILABLE:
            raise PrinterNotAvailableError("Windows printer support not available")
        
        self.printer_name = printer_name
        self.win32print = win32print
    
    def is_available(self) -> bool:
        """Check if printer is available."""
        if not WIN32PRINT_AVAILABLE:
            return False
        try:
            hprinter = self.win32print.OpenPrinter(self.printer_name)
            self.win32print.ClosePrinter(hprinter)
            return True
        except Exception as e:
            logger.warning(f"Printer {self.printer_name} not available: {e}")
            return False
    
    def print_receipt(self, receipt_text: str, qr_data: Optional[str] = None) -> bool:
        """
        Print receipt using Windows thermal printer.
        
        Args:
            receipt_text: Receipt text to print
            qr_data: Optional QR code data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            raise PrinterNotAvailableError(f"Printer {self.printer_name} is not available")
        
        try:
            hprinter = self.win32print.OpenPrinter(self.printer_name)
            try:
                hjob = self.win32print.StartDocPrinter(hprinter, 1, ("Bon", None, "RAW"))
                self.win32print.StartPagePrinter(hprinter)
                
                ESC = b'\x1b'
                GS = b'\x1d'
                
                # Print receipt text
                self._print_formatted_text(hprinter, receipt_text, ESC, GS)
                
                # Print QR code if provided
                if qr_data:
                    self._print_qr_code(hprinter, qr_data, ESC, GS)
                
                self.win32print.WritePrinter(hprinter, b'\n\n\n')
                self.win32print.WritePrinter(hprinter, GS + b'V' + b'\x00')
                self.win32print.EndPagePrinter(hprinter)
                self.win32print.EndDocPrinter(hprinter)
                
                logger.info(f"Receipt printed successfully to {self.printer_name}")
                return True
            finally:
                self.win32print.ClosePrinter(hprinter)
        except Exception as e:
            logger.exception(f"Error printing receipt: {e}")
            return False
    
    def _print_formatted_text(self, hprinter, text: str, ESC: bytes, GS: bytes) -> None:
        """Print formatted text with proper encoding."""
        # This is a simplified version - the full implementation from main.py
        # would be moved here
        lines = text.split('\n')
        for line in lines:
            try:
                encoded = line.encode('cp858', errors='replace')
                self.win32print.WritePrinter(hprinter, encoded)
                self.win32print.WritePrinter(hprinter, b'\n')
            except Exception as e:
                logger.warning(f"Error encoding line: {e}")
    
    def _print_qr_code(self, hprinter, qr_data: str, ESC: bytes, GS: bytes) -> None:
        """Print QR code."""
        try:
            self.win32print.WritePrinter(hprinter, b'\n')
            self.win32print.WritePrinter(hprinter, ESC + b'a' + b'\x01')
            self.win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x04\x00' + b'1A2\x00')
            self.win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x03\x00' + b'1C\x06')
            self.win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x03\x00' + b'1E0')
            qr_data_bytes = qr_data.encode('utf-8')
            qr_len = len(qr_data_bytes) + 3
            self.win32print.WritePrinter(
                hprinter, 
                GS + b'(' + b'k' + qr_len.to_bytes(2, 'little') + b'1P0' + qr_data_bytes
            )
            self.win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x03\x00' + b'1Q0')
            self.win32print.WritePrinter(hprinter, b'\n')
            self.win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')
        except Exception as e:
            logger.warning(f"Error printing QR code: {e}")


def get_printer(printer_name: Optional[str] = None) -> Optional[PrinterInterface]:
    """
    Get appropriate printer instance for current platform.
    
    Args:
        printer_name: Optional printer name (for Windows)
        
    Returns:
        Printer instance or None if no printer available
    """
    if platform.system() == "Windows" and WIN32PRINT_AVAILABLE:
        if printer_name is None:
            printer_name = "EPSON TM-T20II Receipt5"
        try:
            printer = WindowsThermalPrinter(printer_name)
            if printer.is_available():
                return printer
        except PrinterNotAvailableError:
            pass
    
    logger.warning("No printer available for current platform")
    return None



