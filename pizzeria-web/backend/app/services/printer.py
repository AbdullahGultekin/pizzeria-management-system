"""
Printer service for handling receipt printing.
Supports both direct printing (Windows) and print job queue for desktop client.
"""
import logging
import platform
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Windows print support
WIN32PRINT_AVAILABLE = False
if platform.system() == "Windows":
    try:
        import win32print
        WIN32PRINT_AVAILABLE = True
    except ImportError:
        pass


class PrinterService:
    """Service for handling receipt printing."""
    
    def __init__(self):
        self.print_queue: List[Dict[str, Any]] = []
        self.printer_name: Optional[str] = None
        self.direct_print_enabled = WIN32PRINT_AVAILABLE
    
    def set_printer_name(self, printer_name: str) -> None:
        """Set the printer name for direct printing."""
        self.printer_name = printer_name
        logger.info(f"Printer name set to: {printer_name}")
    
    def get_available_printers(self) -> List[str]:
        """Get list of available printers."""
        if not WIN32PRINT_AVAILABLE:
            return []
        
        try:
            printers = []
            printer_info = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
            for printer in printer_info:
                printers.append(printer[2])  # printer[2] is the printer name
            return printers
        except Exception as e:
            logger.error(f"Error getting available printers: {e}")
            return []
    
    def queue_print_job(
        self,
        order_data: Dict[str, Any],
        receipt_text: str,
        qr_data: Optional[str] = None
    ) -> str:
        """
        Queue a print job for desktop client.
        
        Args:
            order_data: Order information
            receipt_text: Formatted receipt text
            qr_data: Optional QR code data
            
        Returns:
            Job ID
        """
        job_id = f"print_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{order_data.get('id', 'unknown')}"
        
        job = {
            "id": job_id,
            "order_id": order_data.get("id"),
            "bonnummer": order_data.get("bonnummer"),
            "receipt_text": receipt_text,
            "qr_data": qr_data,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        self.print_queue.append(job)
        logger.info(f"Print job queued: {job_id} for order {order_data.get('bonnummer')}")
        
        # Try direct print if enabled
        if self.direct_print_enabled and self.printer_name:
            try:
                success = self._print_direct(receipt_text, qr_data)
                if success:
                    job["status"] = "printed"
                    logger.info(f"Print job {job_id} printed directly")
            except Exception as e:
                logger.warning(f"Direct print failed, job remains in queue: {e}")
        
        return job_id
    
    def get_pending_jobs(self) -> List[Dict[str, Any]]:
        """Get all pending print jobs."""
        return [job for job in self.print_queue if job["status"] == "pending"]
    
    def mark_job_printed(self, job_id: str) -> bool:
        """Mark a print job as printed."""
        for job in self.print_queue:
            if job["id"] == job_id:
                job["status"] = "printed"
                logger.info(f"Print job {job_id} marked as printed")
                return True
        return False
    
    def _print_direct(self, receipt_text: str, qr_data: Optional[str] = None) -> bool:
        """
        Print directly to Windows printer.
        
        Args:
            receipt_text: Receipt text to print
            qr_data: Optional QR code data
            
        Returns:
            True if successful, False otherwise
        """
        if not WIN32PRINT_AVAILABLE or not self.printer_name:
            return False
        
        try:
            hprinter = win32print.OpenPrinter(self.printer_name)
            try:
                hjob = win32print.StartDocPrinter(hprinter, 1, ("Bon", None, "RAW"))
                win32print.StartPagePrinter(hprinter)
                
                ESC = b'\x1b'
                GS = b'\x1d'
                
                # Print receipt text
                self._print_formatted_text(hprinter, receipt_text, ESC, GS)
                
                # Print QR code if provided
                if qr_data:
                    self._print_qr_code(hprinter, qr_data, ESC, GS)
                
                win32print.WritePrinter(hprinter, b'\n\n\n')
                win32print.WritePrinter(hprinter, GS + b'V' + b'\x00')  # Cut paper
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
                
                logger.info(f"Receipt printed successfully to {self.printer_name}")
                return True
            finally:
                win32print.ClosePrinter(hprinter)
        except Exception as e:
            logger.error(f"Error printing receipt: {e}")
            return False
    
    def _print_formatted_text(self, hprinter, text: str, ESC: bytes, GS: bytes) -> None:
        """Print formatted text to printer."""
        lines = text.split('\n')
        for line in lines:
            try:
                # Try cp858 encoding (common for thermal printers)
                encoded = line.encode('cp858', errors='replace')
                win32print.WritePrinter(hprinter, encoded)
                win32print.WritePrinter(hprinter, b'\n')
            except Exception as e:
                logger.warning(f"Error encoding line: {e}")
                # Fallback to utf-8
                try:
                    encoded = line.encode('utf-8', errors='replace')
                    win32print.WritePrinter(hprinter, encoded)
                    win32print.WritePrinter(hprinter, b'\n')
                except Exception as e2:
                    logger.error(f"Error encoding line with utf-8: {e2}")
    
    def _print_qr_code(self, hprinter, qr_data: str, ESC: bytes, GS: bytes) -> None:
        """Print QR code using ESC/POS commands."""
        try:
            win32print.WritePrinter(hprinter, b'\n')
            win32print.WritePrinter(hprinter, ESC + b'a' + b'\x01')  # Center align
            win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x04\x00' + b'1A2\x00')
            win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x03\x00' + b'1C\x06')
            win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x03\x00' + b'1E0')
            qr_data_bytes = qr_data.encode('utf-8')
            qr_len = len(qr_data_bytes) + 3
            win32print.WritePrinter(
                hprinter,
                GS + b'(' + b'k' + qr_len.to_bytes(2, 'little') + b'1P0' + qr_data_bytes
            )
            win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x03\x00' + b'1Q0')
            win32print.WritePrinter(hprinter, b'\n')
            win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')  # Left align
        except Exception as e:
            logger.warning(f"Error printing QR code: {e}")
    
    def format_receipt(
        self,
        order_data: Dict[str, Any],
        customer_data: Optional[Dict[str, Any]] = None,
        custom_footer: Optional[str] = None
    ) -> str:
        """
        Format receipt text from order data.
        
        Args:
            order_data: Order information
            customer_data: Customer information
            custom_footer: Custom footer text
            
        Returns:
            Formatted receipt text
        """
        lines = []
        
        # Header
        lines.append("=" * 42)
        lines.append("PITA PIZZA NAPOLI")
        lines.append("Brugstraat 12, 9120 Vrasene")
        lines.append("Tel: 03 775 72 28")
        lines.append("=" * 42)
        lines.append("")
        
        # Order info
        lines.append(f"Bonnummer: {order_data.get('bonnummer', 'N/A')}")
        lines.append(f"Datum: {order_data.get('datum', '')} {order_data.get('tijd', '')}")
        lines.append("")
        
        # Customer info
        if customer_data:
            lines.append("Klant:")
            if customer_data.get('naam'):
                lines.append(f"  {customer_data.get('naam')}")
            if customer_data.get('straat') and customer_data.get('huisnummer'):
                lines.append(f"  {customer_data.get('straat')} {customer_data.get('huisnummer')}")
            if customer_data.get('postcode') and customer_data.get('plaats'):
                lines.append(f"  {customer_data.get('postcode')} {customer_data.get('plaats')}")
            if customer_data.get('telefoon'):
                lines.append(f"  Tel: {customer_data.get('telefoon')}")
            lines.append("")
        
        # Order items
        lines.append("Bestelling:")
        lines.append("-" * 42)
        items = order_data.get('items', [])
        for item in items:
            lines.append(f"{item.get('aantal', 1)}x {item.get('product_naam', 'N/A')}")
            
            # Display extras (vlees, bijgerecht, sauzen, garnering, etc.)
            extras = item.get('extras') or {}
            if isinstance(extras, str):
                import json
                try:
                    extras = json.loads(extras)
                except:
                    extras = {}
            
            if extras:
                # Vlees
                if extras.get('vlees'):
                    lines.append(f"  Vlees: {extras['vlees']}")
                
                # Bijgerecht
                bijgerecht = extras.get('bijgerecht')
                if bijgerecht:
                    if isinstance(bijgerecht, list):
                        lines.append(f"  Bijgerecht: {', '.join(bijgerecht)}")
                    else:
                        lines.append(f"  Bijgerecht: {bijgerecht}")
                
                # Sauzen
                sauzen = extras.get('sauzen')
                if sauzen:
                    if isinstance(sauzen, list):
                        lines.append(f"  Sauzen: {', '.join(sauzen)}")
                    else:
                        lines.append(f"  Sauzen: {sauzen}")
                
                # Sauzen toeslag
                if extras.get('sauzen_toeslag'):
                    lines.append(f"  Sauzen extra: €{extras['sauzen_toeslag']:.2f}")
                
                # Garnering
                garnering = extras.get('garnering')
                if garnering:
                    if isinstance(garnering, list):
                        lines.append(f"  Garnering: {', '.join(garnering)}")
                    else:
                        lines.append(f"  Garnering: {garnering}")
                
                # Half-half
                if extras.get('half_half'):
                    half_half = extras['half_half']
                    if isinstance(half_half, list) and len(half_half) == 2:
                        lines.append(f"  Half-half: {half_half[0]} / {half_half[1]}")
            
            # Opmerking
            if item.get('opmerking'):
                lines.append(f"  Opmerking: {item.get('opmerking')}")
            
            lines.append(f"  €{item.get('prijs', 0) * item.get('aantal', 1):.2f}")
        lines.append("-" * 42)
        
        # Total
        total = order_data.get('totaal', 0)
        lines.append(f"TOTAAL: €{total:.2f}")
        lines.append("")
        
        # Footer
        if custom_footer:
            lines.append(custom_footer)
            lines.append("")
        lines.append("Open: Dinsdag t/m Zondag")
        lines.append("Van 17:00 tot 20:30")
        lines.append("")
        lines.append("Eet smakelijk!")
        lines.append("")
        lines.append("=" * 42)
        
        return "\n".join(lines)


# Global printer service instance
printer_service = PrinterService()


