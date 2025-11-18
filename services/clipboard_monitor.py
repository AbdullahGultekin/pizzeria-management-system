"""
Clipboard Monitor Service

Monitors clipboard for phone numbers and automatically fills them in the form.
This is a simpler and more reliable alternative to Webex API integration.
"""

import threading
import time
import re
from typing import Optional, Callable
from logging_config import get_logger

logger = get_logger("pizzeria.services.clipboard")

try:
    import win32clipboard
    import win32con
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    logger.warning("pywin32 not available, clipboard monitoring disabled")


class ClipboardMonitor:
    """
    Monitor clipboard for phone numbers and notify when detected.
    
    This service periodically checks the clipboard for phone numbers
    and calls a callback when a valid phone number is detected.
    """
    
    def __init__(self):
        """Initialize clipboard monitor."""
        self.monitoring: bool = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.poll_interval: float = 0.5  # Check every 0.5 seconds
        self.on_phone_detected: Optional[Callable[[str], None]] = None
        self.last_clipboard_content: str = ""
        self.last_phone_number: str = ""
        
    def _normalize_phone(self, text: str) -> Optional[str]:
        """
        Extract and normalize phone number from text.
        
        Args:
            text: Text to extract phone number from
            
        Returns:
            Normalized phone number or None if not found
        """
        if not text or not text.strip():
            return None
        
        # Remove common formatting
        text = text.strip()
        
        # Try to extract phone number patterns
        # Belgian phone numbers: 0X XXX XX XX or +32 X XXX XX XX
        patterns = [
            r'(\+32|0032|32)?\s?([1-9]\d{8})',  # +32 1 234 56 78 or 0123456789
            r'0([1-9]\d{8})',  # 0123456789
            r'(\d{10})',  # 10 digits
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.replace(' ', '').replace('-', '').replace('(', '').replace(')', ''))
            if match:
                phone = match.group(0)
                # Remove country code if present
                if phone.startswith('+32') or phone.startswith('0032'):
                    phone = '0' + phone[3:] if phone.startswith('+32') else '0' + phone[4:]
                elif phone.startswith('32') and len(phone) == 10:
                    phone = '0' + phone[2:]
                
                # Validate: should be 10 digits starting with 0
                if phone.startswith('0') and len(phone) == 10 and phone[1:].isdigit():
                    return phone
        
        return None
    
    def _get_clipboard_text(self) -> Optional[str]:
        """Get current clipboard text."""
        if not CLIPBOARD_AVAILABLE:
            return None
        
        try:
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
                    data = win32clipboard.GetClipboardData(win32con.CF_TEXT)
                    if isinstance(data, bytes):
                        return data.decode('utf-8', errors='ignore')
                    return str(data)
            finally:
                win32clipboard.CloseClipboard()
        except Exception as e:
            logger.debug(f"Error reading clipboard: {e}")
            return None
        
        return None
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop (runs in background thread)."""
        logger.info("Clipboard monitor started")
        
        while self.monitoring:
            try:
                clipboard_text = self._get_clipboard_text()
                
                if clipboard_text and clipboard_text != self.last_clipboard_content:
                    self.last_clipboard_content = clipboard_text
                    
                    # Try to extract phone number
                    phone_number = self._normalize_phone(clipboard_text)
                    
                    if phone_number and phone_number != self.last_phone_number:
                        self.last_phone_number = phone_number
                        logger.info(f"Phone number detected in clipboard: {phone_number}")
                        
                        # Notify callback
                        if self.on_phone_detected:
                            try:
                                self.on_phone_detected(phone_number)
                            except Exception as e:
                                logger.exception(f"Error in on_phone_detected callback: {e}")
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                logger.exception(f"Error in clipboard monitor loop: {e}")
                time.sleep(self.poll_interval)
        
        logger.info("Clipboard monitor stopped")
    
    def start_monitoring(self, on_phone_detected: Optional[Callable[[str], None]] = None) -> bool:
        """
        Start monitoring clipboard for phone numbers.
        
        Args:
            on_phone_detected: Callback function(phone_number) called when phone number detected
            
        Returns:
            True if monitoring started, False otherwise
        """
        if not CLIPBOARD_AVAILABLE:
            logger.warning("Clipboard monitoring not available (pywin32 not installed)")
            return False
        
        if self.monitoring:
            logger.warning("Clipboard monitoring already running")
            return True
        
        self.on_phone_detected = on_phone_detected
        self.monitoring = True
        self.last_clipboard_content = ""
        self.last_phone_number = ""
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="ClipboardMonitor"
        )
        self.monitor_thread.start()
        
        logger.info("Clipboard monitoring started")
        return True
    
    def stop_monitoring(self) -> None:
        """Stop monitoring clipboard."""
        if not self.monitoring:
            return
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.monitor_thread = None
        logger.info("Clipboard monitoring stopped")
    
    def is_available(self) -> bool:
        """Check if clipboard monitoring is available."""
        return CLIPBOARD_AVAILABLE

