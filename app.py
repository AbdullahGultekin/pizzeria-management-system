"""
Pizzeria Management System - Main Application Class

This module contains the PizzeriaApp class which encapsulates all application logic,
state, and UI components.
"""

import tkinter as tk
from tkinter import messagebox, Toplevel, scrolledtext, ttk, simpledialog
from typing import Dict, List, Optional, Any, Tuple
import json
import datetime
import platform

# Optional QR code support
try:
    import qrcode
    from PIL import Image
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    qrcode = None
    Image = None

# Core imports
from bon_generator import generate_bon_text
from modules.koeriers import open_koeriers
from modules.afhaal import open_afhaal
from modules.geschiedenis import open_geschiedenis
from modules.klanten import open_klanten_zoeken
from modules.menu_management import open_menu_management
from modules.extras_management import open_extras_management
from modules.klant_management import open_klant_management
from modules.rapportage import open_rapportage
from modules.backup import open_backup_tool
from modules.voorraad import open_voorraad
from modules.bon_viewer import open_bon_viewer
from modules.online_bestellingen import open_online_bestellingen
from database import DatabaseContext, initialize_database
from logging_config import setup_logging, get_logger
from config import load_settings, save_settings, load_json_file, save_json_file
from exceptions import ValidationError, OrderError, DatabaseError
from validation import (
    validate_phone, validate_name, validate_address, validate_house_number,
    validate_postcode, sanitize_string
)

# Import refactored modules
from utils.menu_utils import get_pizza_num, load_menu_categories
from utils.print_utils import open_printer_settings, open_footer_settings, show_print_preview as utils_show_print_preview
from utils.address_utils import suggest_straat, on_adres_entry, selectie_suggestie, update_straatnamen_json
from ui.customer_form_enhanced import EnhancedCustomerForm
from ui.tab_manager import TabManager
from ui.menu_grids import ModernMenuGrids
from ui.category_order_dialog import CategoryOrderDialog
from ui.product_order_dialog import ProductOrderDialog
from ui.product_options_dialog import ProductOptionsDialog
from ui.mode_selector import ModeSelector
from business.customer_handler import CustomerHandler
from business.order_processor import OrderProcessor

# Setup logging
setup_logging()
logger = get_logger()


class PizzeriaApp:
    """
    Main application class for Pizzeria Management System.
    
    This class encapsulates all application state, UI components, and business logic.
    """
    
    # Application version
    VERSION = "1.0.0"
    
    # Constants
    SETTINGS_FILE = "settings.json"
    POSTCODES = [
        "2070 Zwijndrecht", "4568 Nieuw-Namen", "9100 Nieuwkerken-Waas",
        "9100 Sint-Niklaas", "9120 Beveren", "9120 Vrasene", "9120 Haasdonk",
        "9120 Kallo", "9120 Melsele", "9130 Verrebroek", "9130 Kieldrecht",
        "9130 Doel", "9170 Klein meerdonk", "9170 Meerdonk",
        "9170 Sint-Gillis-Waas", "9170 De Klinge"
    ]
    
    def __init__(self, mode: str = "front"):
        """
        Initialize the application.
        
        Args:
            mode: Application mode - "front" (kassa) or "back" (admin)
        """
        # Application mode
        self.mode = mode.lower()
        if self.mode not in ("front", "back"):
            self.mode = "front"
            logger.warning(f"Invalid mode '{mode}', defaulting to 'front'")
        
        logger.info(f"Application started in {self.mode.upper()} mode")
        
        # Platform-specific support
        self.qrcode_available = QRCODE_AVAILABLE
        self.win32print_available = False
        if platform.system() == "Windows":
            try:
                import win32print
                self.win32print_available = True
                logger.info("Windows printer support enabled")
            except ImportError:
                logger.warning("pywin32 niet geïnstalleerd. Windows printer support niet beschikbaar.")
        
        # Warn if optional dependencies are missing
        if not self.qrcode_available:
            logger.warning("qrcode module not installed. QR code generation will not be available.")
        
        # Application data
        self.EXTRAS: Dict[str, Any] = {}
        self.menu_data: Dict[str, Any] = {}
        self.app_settings: Dict[str, Any] = {}
        
        # Business logic handlers
        self.customer_handler = CustomerHandler()
        self.order_processor = OrderProcessor()
        
        # Clipboard monitor (primary method for phone number input)
        self.clipboard_monitor: Optional[Any] = None
        if self.mode == "front":
            try:
                from services.clipboard_monitor import ClipboardMonitor
                self.clipboard_monitor = ClipboardMonitor()
                logger.info("Clipboard monitor initialized")
            except Exception as e:
                logger.warning(f"Could not initialize clipboard monitor: {e}")
                self.clipboard_monitor = None
        
        # Order state
        self.bestelregels: List[Dict[str, Any]] = []
        
        # Menu navigation state
        self.state = {
            "categorie": None,
            "producten": [],
            "page": 0,
            "page_size": 10,
            "gekozen_product": None
        }
        
        # UI control variables (will be initialized in setup_ui)
        self.ctrl: Dict[str, Any] = {}
        self.half1_var: Optional[tk.StringVar] = None
        self.half2_var: Optional[tk.StringVar] = None
        
        # UI references (will be set during GUI setup)
        self.root: Optional[tk.Tk] = None
        self.menubar: Optional[tk.Menu] = None
        self.app_tabs: Optional[ttk.Notebook] = None
        self.bestellen_tab: Optional[tk.Frame] = None
        self.main_frame: Optional[tk.Frame] = None
        self.klant_frame: Optional[tk.LabelFrame] = None
        
        # Customer form widgets
        self.telefoon_entry: Optional[tk.Entry] = None
        self.naam_entry: Optional[tk.Entry] = None
        self.adres_entry: Optional[tk.Entry] = None
        self.nr_entry: Optional[tk.Entry] = None
        self.postcode_var: Optional[tk.StringVar] = None
        self.opmerkingen_entry: Optional[tk.Entry] = None
        self.levertijd_entry: Optional[tk.Entry] = None
        self.lb_suggesties: Optional[tk.Listbox] = None
        
        # Menu interface widgets
        self.product_grid_holder: Optional[tk.Frame] = None
        self.producten_titel: Optional[tk.Label] = None
        self.opties_frame: Optional[tk.Frame] = None
        self.opt_title: Optional[tk.Label] = None
        self.right_overview: Optional[tk.Text] = None
        self.menu_main_panel: Optional[tk.PanedWindow] = None
        self.bestel_frame: Optional[tk.LabelFrame] = None
        self.dynamic_product_options_frame: Optional[tk.Frame] = None
        self.current_options_popup_window: Optional[tk.Toplevel] = None
        self.overzicht: Optional[tk.Text] = None
        
        # Tab management
        self.tabs_map: Dict[str, Dict[str, Any]] = {}
        self.tab_manager: Optional[TabManager] = None
        
        # Load application data
        self.load_data()
        
        # Initialize database
        initialize_database()
    
    def load_data(self) -> None:
        """Load application data (menu, extras, settings)."""
        extras_fallback = {}
        self.EXTRAS = load_json_file("extras.json", fallback_data=extras_fallback)
        try:
            with open("menu.json", "r", encoding="utf-8") as f:
                self.menu_data = json.load(f)
        except FileNotFoundError:
            logger.error("menu.json niet gevonden!")
            self.menu_data = {}
        except json.JSONDecodeError as e:
            logger.error(f"menu.json is geen geldige JSON: {e}")
            self.menu_data = {}
        self.app_settings = load_settings()
    
    def _initialize_app_variables(self) -> None:
        """Initialize Tkinter control variables."""
        if not self.root:
            raise RuntimeError("Root window must be created before initializing variables")
        
        self.ctrl["aantal"] = tk.IntVar(master=self.root, value=1)
        self.ctrl["vlees"] = tk.StringVar(master=self.root)
        self.ctrl["bijgerecht_combos"] = []
        self.ctrl["saus_combos"] = []
        self.ctrl["garnering"] = []
        self.ctrl["opmerking"] = tk.StringVar(master=self.root)
        
        self.half1_var = tk.StringVar(master=self.root, value="1")
        self.half2_var = tk.StringVar(master=self.root, value="2")
    
    def _get_current_order_data(self) -> Tuple[Optional[Dict[str, Any]], Optional[List[Dict[str, Any]]], Optional[str]]:
        """
        Collect current order data with validation.
        
        Returns:
            Tuple of (klant_data, order_items, temp_bonnummer) or (None, None, None) if invalid
        """
        # Get afhaal status first to pass to order processor
        is_afhaal = False
        if hasattr(self, 'enhanced_customer_form') and self.enhanced_customer_form:
            enhanced_data = self.enhanced_customer_form.get_customer_data()
            is_afhaal = enhanced_data.get('afhaal', False)
        
        klant_data, order_items, temp_bonnummer = self.order_processor.get_current_order_data(
            self.telefoon_entry,
            self.naam_entry,
            self.adres_entry,
            self.nr_entry,
            self.postcode_var,
            self.opmerkingen_entry,
            self.bestelregels,
            self.POSTCODES,
            is_afhaal=is_afhaal
        )
        
        # Add levertijd and afhaal/korting info to klant_data if available
        if klant_data:
            if hasattr(self, 'enhanced_customer_form'):
                # Use enhanced form's get_customer_data which handles levertijd and afhaal
                enhanced_data = self.enhanced_customer_form.get_customer_data()
                klant_data['levertijd'] = enhanced_data.get('levertijd')
                klant_data['afhaal'] = enhanced_data.get('afhaal', False)
                klant_data['korting_percentage'] = enhanced_data.get('korting_percentage', 0.0)
            elif self.levertijd_entry:
                levertijd = self.levertijd_entry.get().strip()
                if levertijd and levertijd != "bijv. 19:30":
                    klant_data['levertijd'] = levertijd
                else:
                    klant_data['levertijd'] = None
                klant_data['afhaal'] = False
                klant_data['korting_percentage'] = 0.0
        
        return klant_data, order_items, temp_bonnummer
    
    def bestelling_opslaan(self, show_confirmation: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Save order to database.
        
        Args:
            show_confirmation: Whether to show confirmation message
            
        Returns:
            Tuple of (success, bonnummer)
        """
        klant_data, order_items, _ = self._get_current_order_data()
        if klant_data is None:
            return False, None
        
        success, bonnummer = self.order_processor.save_order(klant_data, order_items, show_confirmation)
        
        if success:
            # Clear UI after successful save
            self.clear_order_form()
            self.update_overzicht()
            # Update statistics dashboard
            if hasattr(self, 'stats_dashboard') and self.stats_dashboard:
                self._update_statistics()
        
        return success, bonnummer
    
    def clear_order_form(self) -> None:
        """Clear the order form fields."""
        if hasattr(self, 'enhanced_customer_form'):
            self.enhanced_customer_form.clear_form()
        else:
            if self.telefoon_entry:
                self.telefoon_entry.delete(0, tk.END)
            if self.naam_entry:
                self.naam_entry.delete(0, tk.END)
            if self.adres_entry:
                self.adres_entry.delete(0, tk.END)
            if self.nr_entry:
                self.nr_entry.delete(0, tk.END)
            if self.postcode_var:
                self.postcode_var.set(self.POSTCODES[0])
            if self.opmerkingen_entry:
                self.opmerkingen_entry.delete(0, tk.END)
            if self.levertijd_entry:
                self.levertijd_entry.delete(0, tk.END)
                self.levertijd_entry.insert(0, "bijv. 19:30")
                self.levertijd_entry.config(fg="gray")
        if self.ctrl.get("opmerking"):
            self.ctrl["opmerking"].set("")
        self.bestelregels.clear()
    
    def laad_bestelling_voor_aanpassing(
        self,
        klant_data: Dict[str, Any],
        bestelregels_data: List[Dict[str, Any]],
        oude_bestelling_id: Optional[int]
    ) -> None:
        """
        Load order for editing or reopening.
        
        Args:
            klant_data: Customer data
            bestelregels_data: Order items (empty list for reopen)
            oude_bestelling_id: Order ID to delete (None for reopen - keeps original order)
        """
        if oude_bestelling_id is not None:
            # Edit mode: delete old order and load items
            self.order_processor.load_order_for_editing(
                klant_data,
                bestelregels_data,
                oude_bestelling_id,
                self.telefoon_entry,
                self.naam_entry,
                self.adres_entry,
                self.nr_entry,
                self.opmerkingen_entry,
                self.bestelregels,
                self.POSTCODES,
                self.postcode_var,
                self.levertijd_entry
            )
        else:
            # Reopen mode: just load customer data, keep original order
            # Clear current order if exists
            if self.bestelregels and not messagebox.askyesno(
                "Bevestigen",
                "De huidige (onopgeslagen) bestelling wordt gewist. Weet u zeker dat u wilt doorgaan?"
            ):
                return
            
            # Clear UI
            self.clear_order_form()
            
            # Load customer data only
            if hasattr(self, 'enhanced_customer_form'):
                self.enhanced_customer_form.set_customer_data(klant_data)
            else:
                if klant_data.get('telefoon'):
                    self.telefoon_entry.insert(0, klant_data.get('telefoon', ''))
                if klant_data.get('naam'):
                    self.naam_entry.insert(0, klant_data.get('naam', ''))
                if klant_data.get('adres'):
                    self.adres_entry.insert(0, klant_data.get('adres', ''))
                if klant_data.get('nr'):
                    self.nr_entry.insert(0, klant_data.get('nr', ''))
                if klant_data.get('opmerking'):
                    self.opmerkingen_entry.insert(0, klant_data.get('opmerking', ''))
                if klant_data.get('levertijd') and self.levertijd_entry:
                    self.levertijd_entry.delete(0, tk.END)
                    self.levertijd_entry.insert(0, klant_data.get('levertijd', ''))
                    self.levertijd_entry.config(fg="black")
                
                # Set postcode
                gevonden_postcode = ""
                for p in self.POSTCODES:
                    if klant_data.get('postcode_gemeente', '') in p:
                        gevonden_postcode = p
                        break
                self.postcode_var.set(gevonden_postcode if gevonden_postcode else self.POSTCODES[0])
            
            # Load order items if provided (for reopen, usually empty)
            if bestelregels_data:
                self.bestelregels.extend(bestelregels_data)
        
        self.update_overzicht()
    
    def show_keyboard_shortcuts(self, event: Optional[tk.Event] = None) -> None:
        """Display keyboard shortcuts help dialog."""
        shortcuts_win = tk.Toplevel(self.root)
        shortcuts_win.title("Sneltoetsen")
        shortcuts_win.geometry("400x300")
        shortcuts_win.transient(self.root)
        shortcuts_win.grab_set()
        
        text_widget = scrolledtext.ScrolledText(shortcuts_win, wrap=tk.WORD, padx=10, pady=10, font=("Arial", 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        shortcuts_text = """Sneltoetsen:

Print & Bestelling:
Ctrl+P / Cmd+P    - Print preview
Ctrl+S / Cmd+S    - Snel printen (zonder preview)
Ctrl+N / Cmd+N    - Nieuwe bestelling (wissen)
Delete / Backspace - Verwijder geselecteerde regel
Escape             - Sluit dialogs

Help:
F1 / Ctrl+H       - Toon deze help
Ctrl+H / Cmd+H    - Toon deze help

Navigatie:
- Gebruik de muis om door menu's te navigeren
- Tab toets om tussen velden te bewegen
- Enter om formulieren in te dienen
"""
        
        text_widget.insert(tk.END, shortcuts_text)
        text_widget.config(state=tk.DISABLED)
        
        tk.Button(shortcuts_win, text="Sluiten", command=shortcuts_win.destroy, bg="#D1FFD1").pack(pady=10)
    
    def _handle_escape(self, event: Optional[tk.Event] = None) -> Optional[str]:
        """Handle Escape key - close topmost dialog."""
        # Find and close topmost Toplevel window
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel) and widget.winfo_viewable():
                widget.destroy()
                return "break"
        return None
    
    def _handle_delete(self, event: Optional[tk.Event] = None) -> Optional[str]:
        """Handle Delete/Backspace key - remove selected order item."""
        if not hasattr(self, 'overzicht') or not self.overzicht:
            return None
        
        try:
            # Get cursor position
            index = self.overzicht.index("insert")
            line_no = int(index.split('.')[0]) - 2  # Subtract 2 for header lines
            
            if line_no >= 0 and line_no < len(self.bestelregels):
                # Remove the item
                self.bestelregels.pop(line_no)
                self.update_overzicht()
                return "break"
        except Exception:
            pass
        
        return None
    
    def _handle_paste_phone(self, event: Optional[tk.Event] = None) -> Optional[str]:
        """Handle Ctrl+Shift+V - paste and normalize phone number from clipboard."""
        try:
            # Get clipboard content
            clipboard_text = self.root.clipboard_get()
            
            if clipboard_text:
                # Normalize phone number
                phone_number = self._normalize_phone_from_text(clipboard_text)
                
                if phone_number and hasattr(self, 'enhanced_customer_form') and self.enhanced_customer_form:
                    if self.enhanced_customer_form.telefoon_entry:
                        # Clear and set phone number
                        self.enhanced_customer_form.telefoon_entry.delete(0, tk.END)
                        self.enhanced_customer_form.telefoon_entry.insert(0, phone_number)
                        # Auto-fill customer data
                        self.enhanced_customer_form._auto_fill_customer()
                        logger.info(f"Phone number pasted from clipboard: {phone_number}")
                        return "break"
        except tk.TclError:
            # Clipboard might be empty or not text
            pass
        except Exception as e:
            logger.exception(f"Error handling paste phone: {e}")
        
        return None
    
    def _normalize_phone_from_text(self, text: str) -> Optional[str]:
        """
        Extract and normalize phone number from text.
        
        Args:
            text: Text to extract phone number from
            
        Returns:
            Normalized phone number or None if not found
        """
        if not text or not text.strip():
            return None
        
        import re
        
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
    
    def _quick_new_order(self, event: Optional[tk.Event] = None) -> Optional[str]:
        """Quick new order - clear all items."""
        if self.bestelregels:
            if messagebox.askyesno("Bevestigen", "Alle items uit de bestelling verwijderen?"):
                self.bestelregels.clear()
                self.update_overzicht()
                return "break"
        return None
    
    def _quick_print(self, event: Optional[tk.Event] = None) -> Optional[str]:
        """Quick print without preview."""
        klant_data, order_items, temp_bonnummer = self._get_current_order_data()
        if klant_data is None:
            messagebox.showwarning("Geen bestelling", "Er is geen bestelling om te printen.")
            return None
        
        if not order_items:
            messagebox.showwarning("Lege bestelling", "De bestelling is leeg.")
            return None
        
        # Save and print directly
        success, bonnummer = self.bestelling_opslaan(show_confirmation=False)
        if success:
            logger.info(f"Quick print: Order {bonnummer} printed successfully")
        else:
            messagebox.showerror("Fout", "Kon bestelling niet printen.")
        
        return "break"
    
    def show_print_preview(self, event: Optional[tk.Event] = None) -> None:
        """Show print preview dialog."""
        klant_data, order_items, temp_bonnummer = self._get_current_order_data()
        if klant_data is None:
            return
        
        open_bon_viewer(
            self.root,
            klant_data,
            order_items,
            temp_bonnummer,
            self.menu_data,
            self.EXTRAS,
            self.app_settings,
            self._save_and_print_from_preview
        )
    
    def _save_and_print_from_preview(
        self,
        full_bon_text_for_print: str,
        address_for_qr: Optional[str] = None,
        klant_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Save order and print from preview."""
        if not self.win32print_available:
            messagebox.showerror("Platform Error", "Windows printer support niet beschikbaar.")
            return
        
        success, bonnummer = self.bestelling_opslaan(show_confirmation=False)
        if not success:
            messagebox.showerror("Fout", "Bestelling kon niet worden opgeslagen.")
            return
        
        import win32print
        from utils.print_utils import get_available_printers
        
        printer_name = self.app_settings.get("thermal_printer_name", "Default")
        
        # Check if printer name is valid
        if not printer_name or printer_name == "Default":
            messagebox.showwarning(
                "Printer niet geconfigureerd",
                "Er is geen printer geconfigureerd.\n\n"
                "Ga naar Instellingen > Printer Instellingen om een printer te selecteren."
            )
            return
        
        # Try to get available printers to suggest alternatives
        available_printers = get_available_printers()
        
        try:
            hprinter = win32print.OpenPrinter(printer_name)
            try:
                hjob = win32print.StartDocPrinter(hprinter, 1, ("Bon", None, "RAW"))
                win32print.StartPagePrinter(hprinter)
                
                ESC = b'\x1b'
                GS = b'\x1d'
                
                # ============ 1. HEADER ============
                win32print.WritePrinter(hprinter, ESC + b'a' + b'\x01')  # Centreren
                win32print.WritePrinter(hprinter, GS + b'!' + b'\x11')  # Groot (dubbele hoogte + breedte)
                win32print.WritePrinter(hprinter, b'PITA PIZZA NAPOLI\n')
                win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')  # Normale grootte
                win32print.WritePrinter(hprinter, b'\n')
                
                header_info = """Brugstraat 12 - 9120 Vrasene
TEL: 03 / 775 72 28
FAX: 03 / 755 52 22
BTW: BE 0479.048.950
Bestel online
www.pitapizzanapoli.be
info@pitapizzanapoli.be

"""
                win32print.WritePrinter(hprinter, header_info.encode('cp437', errors='replace'))
                
                # ============ 2. PARSE BON LINES ============
                bon_lines = full_bon_text_for_print.split('\n')
                bonnummer_idx = bezorgtijd_idx = address_idx = dhr_mvr_idx = details_idx = 0
                
                for i, line in enumerate(bon_lines):
                    if 'Bonnummer' in line: bonnummer_idx = i
                    if 'Bezorgtijd' in line: bezorgtijd_idx = i
                    if 'Leveringsadres:' in line: address_idx = i
                    if ('Dhr.' in line or 'Mvr.' in line): dhr_mvr_idx = i
                    if 'Details bestelling' in line: details_idx = i; break
                
                # ============ 3. BESTELINFO (tot bezorgtijd) ============
                win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')  # Links uitlijnen
                win32print.WritePrinter(hprinter, '\n'.join(bon_lines[bonnummer_idx:bezorgtijd_idx]).encode('cp437', errors='replace'))
                
                # ============ 4. BEZORGTIJD (vet) ============
                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x01')  # Bold aan
                win32print.WritePrinter(hprinter, bon_lines[bezorgtijd_idx].encode('cp437', errors='replace'))
                win32print.WritePrinter(hprinter, b'\n')
                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                win32print.WritePrinter(hprinter, b'\n')
                
                # ============ 5. KLANTNAAM OPHALEN ============
                klantnaam = ""
                if klant_data:
                    klantnaam = klant_data.get("naam", "").strip()
                
                if not klantnaam:
                    # Val terug op bontekst: zoek regel na "Dhr. / Mvr."
                    if dhr_mvr_idx and dhr_mvr_idx + 1 < len(bon_lines):
                        possible_name = bon_lines[dhr_mvr_idx + 1].strip()
                        if possible_name and ("Details bestelling" not in possible_name):
                            klantnaam = possible_name
                
                # ============ 6. LEVERINGSADRES (groot en vet) ============
                win32print.WritePrinter(hprinter, 'Leveringsadres:\n'.encode('cp858'))
                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x01')  # Bold aan
                win32print.WritePrinter(hprinter, GS + b'!' + b'\x01')  # Dubbele hoogte + breedte
                
                # Klantnaam printen
                if klantnaam:
                    win32print.WritePrinter(hprinter, (klantnaam + '\n').encode('cp858', errors='replace'))
                
                # Adres printen
                adres_end = dhr_mvr_idx if (dhr_mvr_idx > 0 and dhr_mvr_idx > address_idx) else details_idx
                address_content = bon_lines[address_idx + 1:adres_end] if address_idx > 0 and adres_end > 0 else []
                for addr_line in address_content:
                    win32print.WritePrinter(hprinter, addr_line.encode('cp858', errors='replace'))
                    win32print.WritePrinter(hprinter, b'\n')
                
                # Reset stijl
                win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')  # Normale grootte
                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                
                # ============ 7. BESTEL-DETAILS ============
                win32print.WritePrinter(hprinter, b'\x1B\x74\x13')  # CP858 encoding voor euroteken
                
                if details_idx > 0:
                    # Bereken einde van details sectie
                    details_end_idx = len(bon_lines)
                    for i in range(details_idx, len(bon_lines)):
                        if 'Tarief' in bon_lines[i] or ('Totaal' in bon_lines[i] and i > details_idx + 2):
                            details_end_idx = i
                            break
                    
                    # "Details bestelling" vet maar normale grootte
                    win32print.WritePrinter(hprinter, ESC + b'E' + b'\x01')  # Bold aan
                    win32print.WritePrinter(hprinter, 'Details bestelling\n'.encode('cp858'))
                    win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                    win32print.WritePrinter(hprinter, b'\n')
                    
                    # Items GROTER maken - dubbele hoogte + breedte
                    win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')  # Links uitlijnen
                    win32print.WritePrinter(hprinter, GS + b'!' + b'\x01')  # Dubbele hoogte
                    win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                    
                    current_item_lines = []
                    first_item = True
                    
                    for line in bon_lines[details_idx + 1:details_end_idx]:
                        stripped_line = line.strip()
                        if stripped_line and (stripped_line[0].isdigit() and 'x' in line[:5]):
                            if current_item_lines:
                                # Print vorige item
                                win32print.WritePrinter(hprinter, '\n'.join(current_item_lines).encode('cp858'))
                                win32print.WritePrinter(hprinter, b'\n')
                                # Reset tijdelijk voor scheidingslijn
                                win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')  # Normale grootte
                                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                                win32print.WritePrinter(hprinter, ('-' * 42 + '\n').encode('cp858'))
                                # Weer groot maken voor volgende item
                                win32print.WritePrinter(hprinter, GS + b'!' + b'\x01')  # Groot
                                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                                current_item_lines = []
                            elif first_item:
                                first_item = False
                            current_item_lines.append(line.replace('?', '€'))
                        else:
                            if "TE BETALEN" in line:
                                continue
                            if stripped_line:
                                current_item_lines.append(f"> {stripped_line}")
                    
                    if current_item_lines:
                        win32print.WritePrinter(hprinter, '\n'.join(current_item_lines).encode('cp858'))
                        win32print.WritePrinter(hprinter, b'\n')
                    
                    # Reset stijl na details
                    win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')  # Normale grootte
                    win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                    win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')  # Links
                    
                    # ============ 8. TARIEF-SECTIE ============
                    tarief_start = -1
                    for i in range(details_end_idx, len(bon_lines)):
                        line = bon_lines[i]
                        if ("Tarief" in line and "Basis" in line and "BTW" in line and "Totaal" in line):
                            tarief_start = i
                            break
                    
                    if tarief_start >= 0:
                        tarief_end = len(bon_lines)
                        for j in range(tarief_start + 1, len(bon_lines)):
                            if bon_lines[j].strip() == "" or bon_lines[j].startswith("Totaal"):
                                tarief_end = j
                                break
                        tarief_block = "\n".join(bon_lines[tarief_start:tarief_end]).encode('cp858', errors='replace')
                        win32print.WritePrinter(hprinter, tarief_block)
                        win32print.WritePrinter(hprinter, b'\n')
                
                # ============ 9. TOTAAL (groot, vet, gecentreerd) ============
                totaal_line = ""
                for i in range(len(bon_lines) - 1, -1, -1):
                    if 'Totaal' in bon_lines[i] and ('€' in bon_lines[i] or '?' in bon_lines[i]):
                        totaal_line = bon_lines[i]
                        break
                
                if totaal_line:
                    totaal_line = totaal_line.replace('\u20ac', '€').replace('\xe2\x82\xac', '€').replace('?', '€')
                    win32print.WritePrinter(hprinter, b'\n')
                    win32print.WritePrinter(hprinter, ESC + b'a' + b'\x01')  # Centreren
                    win32print.WritePrinter(hprinter, ESC + b'E' + b'\x01')  # Bold aan
                    win32print.WritePrinter(hprinter, GS + b'!' + b'\x11')  # Groot (dubbele hoogte + breedte)
                    win32print.WritePrinter(hprinter, totaal_line.encode('cp858', errors='replace'))
                    win32print.WritePrinter(hprinter, b'\n')
                    win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')  # Normale grootte
                    win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                    win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')  # Links uitlijnen
                
                # ============ 10. OPMERKING (indien aanwezig) ============
                if klant_data:
                    klant_opm = (klant_data.get("opmerking") or "").strip()
                    if klant_opm:
                        win32print.WritePrinter(hprinter, b'\n')
                        win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')  # Links
                        win32print.WritePrinter(hprinter, ESC + b'E' + b'\x01')  # Vet aan
                        win32print.WritePrinter(hprinter, GS + b'!' + b'\x01')  # Dubbele hoogte aan
                        opmerking_text = f"Opmerking:\n{klant_opm}"
                        win32print.WritePrinter(hprinter, opmerking_text.encode('cp858', errors='replace'))
                        win32print.WritePrinter(hprinter, b'\n')
                        win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')  # Reset grootte
                        win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Vet uit
                        win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')  # Links uitlijnen
                
                # ============ 11. FOOTER ============
                footer = """

"""
                win32print.WritePrinter(hprinter, ESC + b'a' + b'\x01')  # Centreren
                win32print.WritePrinter(hprinter, footer.encode('cp437', errors='replace'))
                
                # TE BETALEN! (groot/vet) + exact 1 lege lijn erna
                win32print.WritePrinter(hprinter, ESC + b'a' + b'\x01')  # Centreren
                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x01')  # Bold aan
                win32print.WritePrinter(hprinter, GS + b'!' + b'\x01')  # Dubbele hoogte
                win32print.WritePrinter(hprinter, b'TE BETALEN!\n')
                # Reset grootte/vet, blijven gecentreerd
                win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')  # Normale grootte
                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                # Precies één lege lijn na "TE BETALEN!"
                win32print.WritePrinter(hprinter, b'\n')
                # Centraal "Eet smakelijk"
                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x01')  # Bold aan
                win32print.WritePrinter(hprinter, b'Eet smakelijk\n')
                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                # Openingsuren
                win32print.WritePrinter(hprinter, b'Van Dins- tot Zon\n vanaf 17 u Tot 20u30\n')
                
                # Custom footer tekst (indien ingesteld)
                custom_footer_text = self.app_settings.get("bon_footer_custom_text", "").strip()
                if custom_footer_text:
                    # Split in regels en print elke regel
                    for line in custom_footer_text.split('\n'):
                        if line.strip():  # Alleen niet-lege regels printen
                            win32print.WritePrinter(hprinter, line.strip().encode('cp858', errors='replace'))
                            win32print.WritePrinter(hprinter, b'\n')
                
                # Reset uitlijning
                win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')  # Links uitlijnen
                
                # ============ 12. QR CODE (indien aanwezig) ============
                if address_for_qr:
                    win32print.WritePrinter(hprinter, b'\n')
                    win32print.WritePrinter(hprinter, ESC + b'a' + b'\x01')  # Centreren
                    win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x04\x00' + b'1A2\x00')
                    win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x03\x00' + b'1C\x06')
                    win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x03\x00' + b'1E0')
                    qr_data = address_for_qr.encode('utf-8')
                    qr_len = len(qr_data) + 3
                    win32print.WritePrinter(hprinter, GS + b'(' + b'k' + qr_len.to_bytes(2, 'little') + b'1P0' + qr_data)
                    win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x03\x00' + b'1Q0')
                    win32print.WritePrinter(hprinter, b'\n')
                    win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')  # Links uitlijnen
                
                # ============ 13. AFSNIJDEN ============
                win32print.WritePrinter(hprinter, b'\n\n\n')
                win32print.WritePrinter(hprinter, GS + b'V' + b'\x00')  # Snij papier
                
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
                
                messagebox.showinfo("Voltooid", f"Bon {bonnummer} opgeslagen en naar printer gestuurd!")
            finally:
                win32print.ClosePrinter(hprinter)
        except Exception as e:
            error_msg = str(e)
            if "Ongeldige printernaam" in error_msg or "Invalid printer name" in error_msg or "1801" in error_msg:
                # Build error message with available printers
                error_text = (
                    f"De printer '{printer_name}' kon niet worden gevonden.\n\n"
                    f"Controleer:\n"
                    f"1. Of de printer is aangesloten en ingeschakeld\n"
                    f"2. Of de printer naam exact overeenkomt met Windows\n"
                    f"3. Open Instellingen > Printer Instellingen om de juiste naam te selecteren\n\n"
                )
                
                if available_printers:
                    error_text += f"Beschikbare printers ({len(available_printers)}):\n"
                    for i, printer in enumerate(available_printers[:5], 1):  # Show first 5
                        error_text += f"  {i}. {printer}\n"
                    if len(available_printers) > 5:
                        error_text += f"  ... en {len(available_printers) - 5} meer\n"
                    error_text += "\n"
                
                error_text += f"Foutdetails: {error_msg}"
                
                messagebox.showerror("Fout bij afdrukken", error_text)
            else:
                messagebox.showerror("Fout bij afdrukken", f"Kon de bon niet afdrukken.\n\nFoutdetails: {error_msg}")
    
    def update_overzicht(self) -> None:
        """Update order overview display with enhanced formatting."""
        if not self.overzicht:
            return
        
        self.overzicht.delete(1.0, tk.END)
        
        # Header with better styling
        self.overzicht.insert(tk.END, "📋 Bestellingsoverzicht\n", "header")
        self.overzicht.insert(tk.END, "─" * 45 + "\n", "separator")
        self.overzicht.insert(tk.END, "\n")
        
        # Show levertijd if set
        if self.levertijd_entry:
            levertijd = self.levertijd_entry.get().strip()
            if levertijd and levertijd != "bijv. 19:30":
                self.overzicht.insert(tk.END, "⏰ Levertijd: ", "delivery_time")
                self.overzicht.insert(tk.END, f"{levertijd}\n\n", "section")
        
        # Group identical items
        grouped = {}
        order_keys = []
        for item in self.bestelregels:
            extras_key = json.dumps(item.get('extras', {}), sort_keys=True, ensure_ascii=False)
            key = (item.get('categorie'), item.get('product'), extras_key, item.get('opmerking', ''))
            if key not in grouped:
                grouped[key] = {
                    'categorie': item.get('categorie'),
                    'product': item.get('product'),
                    'aantal': 0,
                    'prijs': float(item.get('prijs', 0.0)),
                    'extras': item.get('extras', {}),
                    'opmerking': item.get('opmerking', '')
                }
                order_keys.append(key)
            grouped[key]['aantal'] += int(item.get('aantal', 0))
        
        # Sort order_keys by category to group items together
        order_keys.sort(key=lambda k: (grouped[k].get('categorie', ''), k[1]))
        
        # Display grouped items with category subtotals
        totaal = 0.0
        line_no = 1
        name_col_width = 38
        
        # Track subtotals per category
        category_totals = {}
        current_category = None
        
        for key in order_keys:
            item = grouped[key]
            aantal = item['aantal']
            totaal_regel = item['prijs'] * aantal
            totaal += totaal_regel
            
            # Track category for subtotals
            item_category = item.get('categorie', '')
            if item_category not in category_totals:
                category_totals[item_category] = 0.0
            category_totals[item_category] += totaal_regel
            
            # Show category header if category changed
            if current_category != item_category:
                if current_category is not None and line_no > 1:
                    # Show subtotal for previous category
                    cat_subtotal = category_totals.get(current_category, 0.0)
                    if cat_subtotal > 0:
                        self.overzicht.insert(tk.END, "\n  ", "extra")
                        self.overzicht.insert(tk.END, f"Subtotaal {current_category}: ", "item_header")
                        self.overzicht.insert(tk.END, f"€{cat_subtotal:.2f}\n", "price")
                        self.overzicht.insert(tk.END, "─" * 35 + "\n", "separator")
                
                # New category header
                if item_category:
                    self.overzicht.insert(tk.END, "\n" if line_no > 1 else "", "extra")
                    self.overzicht.insert(tk.END, f"📦 {item_category}\n", "section")
                    self.overzicht.insert(tk.END, "\n", "extra")
                current_category = item_category
            
            # Determine display name
            product_naam = item['product']
            cat = (item['categorie'] or '').lower()
            prefix = ""
            display_name = ""
            
            # Determine prefix based on category
            if "small" in cat:
                prefix = "Small"
            elif "medium" in cat:
                prefix = "Medium"
            elif "large" in cat:
                prefix = "Large"
            elif "grote-broodjes" in cat:
                prefix = "Groot"
            elif "klein-broodjes" in cat:
                prefix = "Klein"
            elif "turks-brood" in cat:
                prefix = "Turks"
            elif "durum" in cat:
                prefix = "Durum"
            elif "pasta" in cat:
                prefix = "Pasta"
            elif "schotel" in cat and "mix" not in cat:
                prefix = "Schotel"
            elif "vegetarisch broodjes" in cat:
                prefix = "Broodje"
            
            extras = item.get('extras', {})
            half_half = extras.get('half_half')
            is_mixschotel = "mix schotel" in cat
            is_gratis = extras.get('volle_kaart', False)
            
            # Logic for pizzas
            if any(x in cat for x in ("pizza's", "pizza")):
                formaat = prefix if prefix else "Pizza"
                if half_half and isinstance(half_half, list) and len(half_half) == 2:
                    display_name = f"{formaat} {half_half[0]}/{half_half[1]}"
                else:
                    nummer = get_pizza_num(product_naam)
                    display_name = f"{formaat} {nummer}"
            else:
                if is_mixschotel:
                    display_name = product_naam.strip()
                elif prefix:
                    display_name = f"{prefix} {product_naam}".strip()
                else:
                    display_name = product_naam.strip()
            
            # Add spacing between items for better readability
            if line_no > 1:
                self.overzicht.insert(tk.END, "\n")
            
            # Item header with number
            self.overzicht.insert(tk.END, f"[{line_no}] ", "item_number")
            self.overzicht.insert(tk.END, f"{display_name}", "item_header")
            
            if is_gratis:
                self.overzicht.insert(tk.END, " [GRATIS]", "free")
            
            self.overzicht.insert(tk.END, f" ×{aantal}\n", "item_number")
            
            # Price with better formatting
            if is_gratis:
                self.overzicht.insert(tk.END, "  ", "extra")
                self.overzicht.insert(tk.END, "€0.00", "free")
                self.overzicht.insert(tk.END, " [GRATIS]\n", "free")
            else:
                self.overzicht.insert(tk.END, "  ", "extra")
                self.overzicht.insert(tk.END, f"€{totaal_regel:.2f}\n", "price")
            
            # Display extras with better formatting
            extras = item.get('extras', {}) or {}
            if extras:
                for k in ['vlees', 'bijgerecht', 'saus', 'sauzen', 'garnering']:
                    if k in extras and extras[k]:
                        val = extras[k]
                        if isinstance(val, list):
                            for v in val:
                                if v:
                                    self.overzicht.insert(tk.END, "  └─ ", "extra")
                                    self.overzicht.insert(tk.END, f"{v}\n", "extra")
                        else:
                            self.overzicht.insert(tk.END, "  └─ ", "extra")
                            self.overzicht.insert(tk.END, f"{val}\n", "extra")
                if 'sauzen_toeslag' in extras and extras['sauzen_toeslag']:
                    try:
                        toeslag = float(extras['sauzen_toeslag'])
                        if toeslag > 0:
                            self.overzicht.insert(tk.END, "  └─ ", "extra")
                            self.overzicht.insert(tk.END, f"Sauzen extra: ", "extra")
                            self.overzicht.insert(tk.END, f"€{toeslag:.2f}\n", "price")
                    except Exception:
                        pass
            
            # Display note with better formatting
            if item.get('opmerking'):
                self.overzicht.insert(tk.END, "  └─ ", "note")
                self.overzicht.insert(tk.END, f"Opmerking: {item['opmerking']}\n", "note")
            
            line_no += 1
        
        # Show subtotal for last category
        if current_category and category_totals.get(current_category, 0.0) > 0:
            cat_subtotal = category_totals.get(current_category, 0.0)
            self.overzicht.insert(tk.END, "\n  ", "extra")
            self.overzicht.insert(tk.END, f"Subtotaal {current_category}: ", "item_header")
            self.overzicht.insert(tk.END, f"€{cat_subtotal:.2f}\n", "price")
        
        # Total section with better formatting
        if order_keys:
            self.overzicht.insert(tk.END, "\n" + "═" * 45 + "\n", "separator")
            self.overzicht.insert(tk.END, "\n")
        
        # Show category breakdown if multiple categories
        if len(category_totals) > 1:
            self.overzicht.insert(tk.END, "📊 Overzicht per categorie:\n", "section")
            for cat_name, cat_total in sorted(category_totals.items()):
                if cat_total > 0:
                    self.overzicht.insert(tk.END, f"  • {cat_name}: ", "extra")
                    self.overzicht.insert(tk.END, f"€{cat_total:.2f}\n", "price")
            self.overzicht.insert(tk.END, "\n", "extra")
        
        # Check for afhaal korting
        korting_percentage = 0.0
        korting_bedrag = 0.0
        is_afhaal = False
        
        if hasattr(self, 'enhanced_customer_form') and self.enhanced_customer_form:
            customer_data = self.enhanced_customer_form.get_customer_data()
            is_afhaal = customer_data.get('afhaal', False)
            korting_percentage = customer_data.get('korting_percentage', 0.0)
        
        # Calculate discount
        if korting_percentage > 0 and totaal > 0:
            korting_bedrag = round(totaal * (korting_percentage / 100), 2)
            subtotaal = totaal
            totaal_na_korting = subtotaal - korting_bedrag
            
            self.overzicht.insert(tk.END, "💰 Subtotaal: ", "item_header")
            self.overzicht.insert(tk.END, f"€{subtotaal:.2f}\n", "price")
            
            self.overzicht.insert(tk.END, "🎁 Korting (", "extra")
            self.overzicht.insert(tk.END, f"{korting_percentage:.0f}%", "free")
            self.overzicht.insert(tk.END, "): ", "extra")
            self.overzicht.insert(tk.END, f"-€{korting_bedrag:.2f}\n", "free")
            
            self.overzicht.insert(tk.END, "💰 Totaal: ", "item_header")
            self.overzicht.insert(tk.END, f"€{totaal_na_korting:.2f}\n", "total")
        else:
            self.overzicht.insert(tk.END, "💰 Totaal: ", "item_header")
            self.overzicht.insert(tk.END, f"€{totaal:.2f}\n", "total")
        
        # Scroll to top
        self.overzicht.see(1.0)
    
    def _get_today_statistics(self) -> Dict[str, Any]:
        """
        Get today's order statistics.
        
        Returns:
            Dictionary with count, total, and average
        """
        try:
            from datetime import date
            today = date.today().strftime('%Y-%m-%d')
            
            with DatabaseContext() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as count, COALESCE(SUM(totaal), 0) as total
                    FROM bestellingen
                    WHERE datum = ?
                """, (today,))
                row = cursor.fetchone()
                
                if row:
                    count = row['count'] or 0
                    total = float(row['total'] or 0.0)
                    average = round(total / count, 2) if count > 0 else 0.0
                    return {
                        'count': count,
                        'total': round(total, 2),
                        'average': average
                    }
        except Exception as e:
            logger.exception(f"Error fetching today's statistics: {e}")
        
        return {'count': 0, 'total': 0.0, 'average': 0.0}
    
    def _setup_statistics_dashboard(self, parent: tk.Frame) -> None:
        """Setup statistics dashboard showing today's sales."""
        self.stats_dashboard = tk.LabelFrame(
            parent,
            text="📊 Vandaag",
            font=("Arial", 8, "bold"),
            padx=6,
            pady=4,
            bg="#F8F9FA",
            relief=tk.RAISED,
            bd=1
        )
        self.stats_dashboard.pack(fill=tk.X, pady=(0, 6))
        
        # Stats container - compact horizontal layout
        stats_container = tk.Frame(self.stats_dashboard, bg="#F8F9FA")
        stats_container.pack(fill=tk.X)
        
        # Create stat cards - compact
        self.stats_labels = {}
        
        # Aantal bestellingen - compact
        count_frame = tk.Frame(stats_container, bg="#E3F2FD", relief=tk.RAISED, bd=1, padx=4, pady=3)
        count_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 2))
        
        tk.Label(
            count_frame,
            text="Bestellingen",
            font=("Arial", 7),
            bg="#E3F2FD",
            fg="#6C757D"
        ).pack()
        
        self.stats_labels['count'] = tk.Label(
            count_frame,
            text="0",
            font=("Arial", 12, "bold"),
            bg="#E3F2FD",
            fg="#1976D2"
        )
        self.stats_labels['count'].pack()
        
        # Totaal omzet - compact
        total_frame = tk.Frame(stats_container, bg="#E8F5E9", relief=tk.RAISED, bd=1, padx=4, pady=3)
        total_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1)
        
        tk.Label(
            total_frame,
            text="Omzet",
            font=("Arial", 7),
            bg="#E8F5E9",
            fg="#6C757D"
        ).pack()
        
        self.stats_labels['total'] = tk.Label(
            total_frame,
            text="€0.00",
            font=("Arial", 12, "bold"),
            bg="#E8F5E9",
            fg="#2E7D32"
        )
        self.stats_labels['total'].pack()
        
        # Gemiddelde - compact
        avg_frame = tk.Frame(stats_container, bg="#FFF3E0", relief=tk.RAISED, bd=1, padx=4, pady=3)
        avg_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 0))
        
        tk.Label(
            avg_frame,
            text="Gemiddelde",
            font=("Arial", 7),
            bg="#FFF3E0",
            fg="#6C757D"
        ).pack()
        
        self.stats_labels['average'] = tk.Label(
            avg_frame,
            text="€0.00",
            font=("Arial", 12, "bold"),
            bg="#FFF3E0",
            fg="#F57C00"
        )
        self.stats_labels['average'].pack()
        
        # Initial update
        self._update_statistics()
    
    def _update_statistics(self) -> None:
        """Update statistics dashboard with latest data."""
        if not hasattr(self, 'stats_labels') or not self.stats_labels:
            return
        
        stats = self._get_today_statistics()
        
        # Update labels
        if 'count' in self.stats_labels:
            self.stats_labels['count'].config(text=str(stats['count']))
        if 'total' in self.stats_labels:
            self.stats_labels['total'].config(text=f"€{stats['total']:.2f}")
        if 'average' in self.stats_labels:
            self.stats_labels['average'].config(text=f"€{stats['average']:.2f}")
    
    def update_right_overview(self, extra_keuze: Dict[str, Any], product: Dict[str, Any]) -> None:
        """Update right overview panel with product and extras."""
        if self.right_overview is None:
            return
        try:
            self.right_overview.delete(1.0, tk.END)
        except Exception:
            return
        
        base_line = f"{product['naam']} x{self.ctrl['aantal'].get()} — €{product['prijs']:.2f}"
        lines = [base_line]
        
        for k, v in extra_keuze.items():
            if k == 'half_half' and isinstance(v, list) and len(v) == 2:
                lines.append(f"  Half-Half: Pizza {v[0]} & {v[1]}")
            elif k == 'sauzen_toeslag':
                lines.append(f"  Sauzen extra: €{float(v):.2f}")
            elif isinstance(v, list) and v:
                lines.append(f"  {k}: {', '.join(map(str, v))}")
            elif v and k not in ('sauzen_toeslag',):
                lines.append(f"  {k}: {v}")
        
        self.right_overview.insert(tk.END, "\n".join(lines))
    
    def clear_opties(self) -> None:
        """Clear all option controls."""
        self.ctrl["aantal"].set(1)
        self.ctrl["vlees"].set("")
        for var in self.ctrl["bijgerecht_combos"]:
            if var:
                var.set("")
        self.ctrl["bijgerecht_combos"].clear()
        
        for var in self.ctrl["saus_combos"]:
            if var:
                var.set("")
        self.ctrl["saus_combos"].clear()
        
        for naam, var in self.ctrl["garnering"]:
            if var:
                var.set(False)
        self.ctrl["garnering"].clear()
        
        self.ctrl["opmerking"].set("")
        if self.half1_var:
            self.half1_var.set("1")
        if self.half2_var:
            self.half2_var.set("2")
    
    def render_opties(self, product: Dict[str, Any]) -> None:
        """Render product options dialog using enhanced dialog."""
        if self.current_options_popup_window and self.current_options_popup_window.winfo_exists():
            self.current_options_popup_window.destroy()
            self.current_options_popup_window = None
        
        self.state["gekozen_product"] = product
        if not product:
            if self.opt_title:
                self.opt_title.config(text="Opties Product")
            if self.right_overview:
                self.right_overview.delete(1.0, tk.END)
            return
        
        self.clear_opties()
        
        # Get category and extras config
        cat_key = (self.state["categorie"] or "").lower()
        extras_cat = self.EXTRAS.get(cat_key, {}) if isinstance(self.EXTRAS, dict) else {}
        
        # Prepare initial values
        initial_values = {
            'aantal': self.ctrl["aantal"].get(),
            'vlees': self.ctrl["vlees"].get(),
            'opmerking': self.ctrl["opmerking"].get(),
            'half1': self.half1_var.get(),
            'half2': self.half2_var.get(),
            'volle_kaart': False,
        }
        
        # Callback for when product is added
        def on_add(result: Dict[str, Any]) -> None:
            self.bestelregels.append(result)
            self.update_overzicht()
        
        # Callback for when dialog closes
        def on_close() -> None:
            self.state["gekozen_product"] = None
            self.current_options_popup_window = None
            if self.opt_title:
                self.opt_title.config(text="Opties Product")
        
        # Create and show dialog
        dialog = ProductOptionsDialog(
            parent=self.root,
            product=product,
            category=self.state["categorie"] or "",
            extras_config=extras_cat,
            initial_values=initial_values,
            on_add=on_add,
            on_close=on_close
        )
        
        self.current_options_popup_window = dialog.window
    
    def _quick_add_product(self, product: Dict[str, Any], category: str) -> None:
        """
        Quickly add a product to order with default options (no dialog).
        
        Args:
            product: Product dictionary
            category: Category name
        """
        # Create order item with default values
        order_item = {
            'categorie': category,
            'product': product.get('naam', ''),
            'aantal': 1,
            'prijs': float(product.get('prijs', 0.0)),
            'extras': {},
            'opmerking': ''
        }
        
        # Add to order
        self.bestelregels.append(order_item)
        self.update_overzicht()
        
        logger.info(f"Quick add: {product.get('naam', '')} from {category}")
    
    def render_producten(self) -> None:
        """Render product grid for current category - original version."""
        if not self.product_grid_holder:
            return
        
        cat = self.state["categorie"] or "-"
        items = self.state["producten"]
        # Use more columns for pizza categories to fit all products
        is_pizza_category = "pizza's" in (cat or "").lower()
        columns = 5 if is_pizza_category else 5  # 7 columns for pizzas, 5 for others
        
        kleuren_lijst = [
            "#FFDD44",  # Geel
            "#6BE3C1",  # Mint
            "#FF9A8B",  # Oranje/Rood
            "#84B6F4",  # Blauw
            "#FFD6E5",  # Pastel roze
        ]
        
        for w in self.product_grid_holder.winfo_children():
            w.destroy()
        
        for i, product in enumerate(items):
            bg_color = kleuren_lijst[i % len(kleuren_lijst)]
            
            card_frame = tk.Frame(self.product_grid_holder, bd=1, relief=tk.RAISED, padx=1, pady=1, bg=bg_color)
            card_frame.grid(row=i // columns, column=i % columns, padx=1, pady=1, sticky="nsew")
            card_frame.grid_propagate(False)
            
            if is_pizza_category:
                pizza_number = product['naam'].split('.')[0].strip()
                btn = tk.Button(
                    card_frame,
                    text=pizza_number,
                    font=("Arial", 12, "bold"),  # Slightly smaller font for more columns
                    bg=bg_color,
                    command=lambda p=product: self.render_opties(p)
                )
                btn.pack(fill="both", expand=True)
                card_frame.config(width=60, height=60)  # Smaller cards for more columns
            else:
                btn_text = f"{product['naam']}\n€{product['prijs']:.2f}"
                btn = tk.Button(
                    card_frame,
                    text=btn_text,
                    font=("Arial", 10),
                    bg=bg_color,
                    command=lambda p=product: self.render_opties(p)
                )
                btn.pack(fill="both", expand=True)
                card_frame.config(width=120, height=60)
        
        for c in range(columns):
            if self.product_grid_holder:
                self.product_grid_holder.grid_columnconfigure(c, weight=1)
    
    def on_select_categorie(self, category_name: str) -> None:
        """Handle category selection."""
        logger.debug(f"Geselecteerde categorie: {category_name}")
        if category_name not in self.menu_data:
            try:
                with open("menu.json", "r", encoding="utf-8") as f:
                    self.menu_data = json.load(f)
            except Exception as e:
                logger.error(f"Kon menu.json niet herladen: {e}")
        
        self.state["categorie"] = category_name
        products = list(self.menu_data.get(category_name, []))
        
        # Apply product order if available
        product_order = self.app_settings.get("product_order", {})
        if category_name in product_order:
            preferred_order = product_order[category_name]
            # Create a mapping of product names to products
            product_map = {p.get('naam', ''): p for p in products}
            # Order products according to preferred order
            ordered_products = []
            for name in preferred_order:
                if name in product_map:
                    ordered_products.append(product_map[name])
            # Add any products not in the order list at the end
            for product in products:
                product_name = product.get('naam', '')
                if product_name not in preferred_order:
                    ordered_products.append(product)
            products = ordered_products
        
        self.state["producten"] = products
        logger.info(f"Producten in categorie: {len(self.state['producten'])} items geladen.")
        self.state["gekozen_product"] = None
        
        # Update modern grid selection
        if self.modern_menu_grids:
            self.modern_menu_grids.set_category_selection(category_name)
        
        # Sluit eventuele openstaande optievensters
        if self.current_options_popup_window and self.current_options_popup_window.winfo_exists():
            self.current_options_popup_window.destroy()
            self.current_options_popup_window = None
        
        self.clear_opties()
        
        if self.producten_titel and self.producten_titel.winfo_exists():
            self.producten_titel.config(text=category_name)
        
        # Enable product order button when category is selected
        if self.product_order_btn and self.product_order_btn.winfo_exists():
            self.product_order_btn.config(state=tk.NORMAL)
        
        if self.product_grid_holder and self.product_grid_holder.winfo_exists():
            self.render_producten()
        else:
            if self.root:
                self.root.after(50, self.render_producten)
    
    def setup_ui(self) -> None:
        """Setup the main user interface."""
        # Create root window
        self.root = tk.Tk()
        self._initialize_app_variables()
        
        # Setup cleanup handler for when window is closed
        def on_closing():
            """Cleanup when application closes."""
            try:
                # Stop clipboard monitoring
                if self.clipboard_monitor:
                    self.clipboard_monitor.stop_monitoring()
                logger.info("Application cleanup completed")
            except Exception as e:
                logger.exception(f"Error during cleanup: {e}")
            finally:
                self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Set window title based on mode
        mode_label = "Kassa" if self.mode == "front" else "Admin"
        self.root.title(f"Pizzeria Bestelformulier - {mode_label} Modus")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        self.root.configure(bg="#F3F2F1")
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Setup tabs
        self.setup_tabs()
        
        # Setup customer form and menu interface (only in front mode)
        if self.mode == "front":
            self.setup_customer_form()
            self.setup_menu_interface()
            
            # Start clipboard monitoring (primary method for phone number input)
            self._setup_clipboard_monitoring()
            
            # Load initial category
            categories = load_menu_categories()
            if categories:
                self.root.after(100, lambda: self.on_select_categorie(categories[0]))
    
    def setup_menu_bar(self) -> None:
        """Setup the application menu bar."""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Settings menu (only in front mode)
        if self.mode == "front":
            settings_menu = tk.Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label="Instellingen", menu=settings_menu)
            settings_menu.add_command(label="Printer Instellingen", command=lambda: open_printer_settings(self.root, self.app_settings))
            settings_menu.add_command(label="Bon Footer Instellingen", command=lambda: open_footer_settings(self.root, self.app_settings))
        
        # Mode switch menu (available in both modes)
        mode_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Modus", menu=mode_menu)
        mode_menu.add_command(label="🔄 Modus Selectie", command=self.show_mode_selector)
        mode_menu.add_separator()
        if self.mode == "front":
            mode_menu.add_command(label="🔧 Wissel naar Admin Modus", command=self.switch_to_admin_mode)
        else:
            mode_menu.add_command(label="💰 Wissel naar Kassa Modus", command=self.switch_to_front_mode)
        
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Sneltoetsen", command=self.show_keyboard_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(
            label="Over",
            command=lambda: messagebox.showinfo(
                "Over",
                f"Pizzeria Management System\nVersie {self.VERSION}"
            )
        )
    
    def _is_focus_in_entry(self, widget=None) -> bool:
        """
        Check if focus is currently in an Entry or Text widget.
        
        Args:
            widget: Optional widget to check (defaults to current focus)
            
        Returns:
            True if focus is in Entry/Text widget, False otherwise
        """
        if widget is None:
            widget = self.root.focus_get()
        
        if widget is None:
            return False
        
        # Check if widget is an Entry or Text widget
        widget_class = widget.__class__.__name__
        return widget_class in ('Entry', 'Text', 'ScrolledText')
    
    def _safe_shortcut_handler(self, handler, event=None):
        """
        Wrapper for keyboard shortcuts that checks if focus is in Entry/Text widget.
        Only executes handler if focus is NOT in Entry/Text widget.
        
        Args:
            handler: Function to call if shortcut should execute
            event: Keyboard event (optional)
        """
        if self._is_focus_in_entry():
            # Focus is in Entry/Text widget, don't execute shortcut
            return None
        # Focus is not in Entry/Text widget, execute shortcut
        if event:
            return handler(event)
        else:
            return handler()
    
    def setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        # Print shortcuts - only when NOT typing in Entry/Text
        self.root.bind("<Control-p>", lambda e: self._safe_shortcut_handler(self.show_print_preview, e))
        self.root.bind("<Command-p>", lambda e: self._safe_shortcut_handler(self.show_print_preview, e))
        
        # Help shortcuts - only when NOT typing in Entry/Text
        self.root.bind("<F1>", lambda e: self._safe_shortcut_handler(self.show_keyboard_shortcuts, e))
        self.root.bind("<Control-h>", lambda e: self._safe_shortcut_handler(self.show_keyboard_shortcuts, e))
        self.root.bind("<Command-h>", lambda e: self._safe_shortcut_handler(self.show_keyboard_shortcuts, e))
        
        # New order shortcuts (only in front mode) - only when NOT typing in Entry/Text
        if self.mode == "front":
            self.root.bind("<Control-n>", lambda e: self._safe_shortcut_handler(lambda: self._quick_new_order(), e))
            self.root.bind("<Command-n>", lambda e: self._safe_shortcut_handler(lambda: self._quick_new_order(), e))
            
            # Quick print (without preview) - only when NOT typing in Entry/Text
            self.root.bind("<Control-s>", lambda e: self._safe_shortcut_handler(lambda: self._quick_print(), e))
            self.root.bind("<Command-s>", lambda e: self._safe_shortcut_handler(lambda: self._quick_print(), e))
            
            # Escape to close dialogs - only when NOT typing in Entry/Text
            self.root.bind("<Escape>", lambda e: self._safe_shortcut_handler(self._handle_escape, e))
            
            # Delete to remove selected item - only when NOT typing in Entry/Text
            # Note: Delete and BackSpace should work normally in Entry widgets, so we check focus
            def handle_delete_safe(event):
                if self._is_focus_in_entry():
                    # Let Entry widget handle Delete/BackSpace normally
                    return None
                return self._handle_delete(event)
            
            self.root.bind("<Delete>", handle_delete_safe)
            self.root.bind("<BackSpace>", handle_delete_safe)
            
            # Clipboard paste hotkey for phone number (Ctrl+Shift+V or Ctrl+V in phone field)
            # This one should work even in Entry widgets, so no check needed
            self.root.bind("<Control-Shift-v>", self._handle_paste_phone)
            self.root.bind("<Command-Shift-v>", self._handle_paste_phone)
    
    def setup_tabs(self) -> None:
        """Setup the tab interface."""
        # Configure Notebook style for consistent tab alignment (left-aligned)
        style = ttk.Style()
        # Use a consistent theme for Notebook to ensure uniform tab positioning
        # Try to use 'clam' theme if available, otherwise use default
        try:
            style.theme_use("clam")
        except:
            pass  # Use default theme if 'clam' is not available
        
        # Ensure tabs are consistently left-aligned across all platforms
        style.configure("TNotebook", tabposition="n")
        style.configure("TNotebook.Tab", padding=[12, 8], anchor="w")  # Left-align tab text
        
        self.app_tabs = ttk.Notebook(self.root)
        self.app_tabs.pack(fill=tk.BOTH, expand=True)
        
        self.tab_manager = TabManager(self.app_tabs)
        
        # Create Bestellen tab (only in front mode)
        if self.mode == "front":
            self.bestellen_tab = tk.Frame(self.app_tabs, bg="#F3F2F1")
            self.app_tabs.add(self.bestellen_tab, text="Bestellen")
        
        # Create other tabs
        self.setup_other_tabs()
        
        # Bind tab change event
        self.app_tabs.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def setup_other_tabs(self) -> None:
        """Setup tabs for other modules (lazy load) based on mode."""
        if self.mode == "front":
            # Front mode: Bestellen, Online Bestellingen, Koeriers, Afhaal (geen Geschiedenis)
            self.tab_manager.add_tab("Online Bestellingen")
            self.tab_manager.add_tab("Koeriers")
            self.tab_manager.add_tab("Afhaal")
        else:
            # Back mode: Admin functions + Geschiedenis
            self.tab_manager.add_tab("Menu Management")
            self.tab_manager.add_tab("Extras")
            self.tab_manager.add_tab("Klanten")
            self.tab_manager.add_tab("Geschiedenis")
            self.tab_manager.add_tab("Rapportage")
            self.tab_manager.add_tab("Backup/Restore")
            self.tab_manager.add_tab("Voorraad")
    
    def on_tab_changed(self, event: tk.Event) -> None:
        """Handle tab change event."""
        load_callbacks = {
            "Extras": lambda parent: open_extras_management(parent),
            "Klanten": lambda parent: open_klant_management(parent),
            "Geschiedenis": lambda parent: open_geschiedenis(
                parent, self.menu_data, self.EXTRAS, self.app_settings, self.laad_bestelling_voor_aanpassing
            ),
            "Rapportage": lambda parent: open_rapportage(parent),
            "Backup/Restore": lambda parent: open_backup_tool(parent),
            "Koeriers": lambda parent: open_koeriers(parent),
            "Afhaal": lambda parent: open_afhaal(parent),
            "Voorraad": lambda parent: open_voorraad(parent),
            "Menu Management": lambda parent: open_menu_management(parent),
            "Online Bestellingen": lambda parent: open_online_bestellingen(
                parent, self.app_settings, self.menu_data, self.EXTRAS
            ),
        }
        self.tab_manager.on_tab_changed(event, load_callbacks)
    
    def setup_customer_form(self) -> None:
        """Setup the enhanced customer input form."""
        if not self.bestellen_tab:
            raise RuntimeError("Bestellen tab must be created first")
        
        # Main frame
        self.main_frame = tk.Frame(self.bestellen_tab, padx=14, pady=14, bg="#F3F2F1")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Use enhanced customer form
        self.enhanced_customer_form = EnhancedCustomerForm(
            self.main_frame,
            self.POSTCODES,
            self.root,
            on_search_callback=lambda: open_klanten_zoeken(
                self.root,
                self.enhanced_customer_form.telefoon_entry,
                self.enhanced_customer_form.naam_entry,
                self.enhanced_customer_form.adres_entry,
                self.enhanced_customer_form.nr_entry,
                self.enhanced_customer_form.postcode_var,
                self.POSTCODES
            )
        )
        
        # Store app reference in form for callbacks
        self.enhanced_customer_form.app = self
        
        # Map to existing references for compatibility
        self.klant_frame = self.enhanced_customer_form.klant_frame
        self.telefoon_entry = self.enhanced_customer_form.telefoon_entry
        self.naam_entry = self.enhanced_customer_form.naam_entry
        self.adres_entry = self.enhanced_customer_form.adres_entry
        self.nr_entry = self.enhanced_customer_form.nr_entry
        self.postcode_var = self.enhanced_customer_form.postcode_var
        self.opmerkingen_entry = self.enhanced_customer_form.opmerkingen_entry
        self.levertijd_entry = self.enhanced_customer_form.levertijd_entry
        self.lb_suggesties = self.enhanced_customer_form.lb_suggesties
    
    def setup_menu_interface(self) -> None:
        """Setup menu interface UI."""
        if not self.main_frame:
            raise RuntimeError("Main frame must be created first")
        
        # Hoofdpaneel (links: menu/producten, rechts: besteloverzicht)
        self.menu_main_panel = tk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashpad=4)
        self.menu_main_panel.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        # ========== LINKERKANT ==========
        menu_selection_frame = tk.Frame(self.menu_main_panel)
        self.menu_main_panel.add(menu_selection_frame, minsize=1000)
        
        def get_ordered_categories():
            """Get categories in the preferred order, similar to product order logic."""
            all_categories = list(self.menu_data.keys())
            
            # Get preferred order from settings (read fresh each time)
            preferred_order = self.app_settings.get("category_order", [])
            
            if not preferred_order:
                # No order set, return all categories as-is
                return all_categories
            
            # Create ordered list following preferred order
            ordered_categories = []
            for cat_name in preferred_order:
                if cat_name in all_categories:
                    ordered_categories.append(cat_name)
            
            # Add any categories not in the order list at the end
            for cat_name in all_categories:
                if cat_name not in preferred_order:
                    ordered_categories.append(cat_name)
            
            return ordered_categories
        
        # Header (Snelle Acties verwijderd voor meer ruimte)
        header_bar = tk.Frame(menu_selection_frame, padx=4, pady=4, bg="#ECECEC")
        header_bar.pack(fill=tk.X)
        tk.Label(header_bar, text="Categorieën", font=("Arial", 11, "bold"), bg="#ECECEC").pack(side=tk.LEFT)
        tk.Label(header_bar, text="Kolommen:", bg="#ECECEC").pack(side=tk.LEFT, padx=(12, 4))
        category_columns_var = tk.IntVar(master=header_bar, value=5)
        tk.Spinbox(header_bar, from_=1, to=10, width=3, textvariable=category_columns_var).pack(side=tk.LEFT)
        
        def open_cat_order_dialog():
            """Open category order dialog with all available categories."""
            # Get all categories from menu_data
            all_categories = list(self.menu_data.keys())
            
            # Get current order from settings
            preferred_order = self.app_settings.get("category_order", [])
            
            # If we have a preferred order, use it; otherwise use all categories
            if preferred_order:
                # Ensure all categories from preferred_order exist in menu_data
                categories = [c for c in preferred_order if c in all_categories]
                # Add any missing categories at the end
                for cat in all_categories:
                    if cat not in categories:
                        categories.append(cat)
            else:
                categories = all_categories.copy()
            
            def on_save(new_order: List[str]) -> None:
                """Save the new category order."""
                self.app_settings["category_order"] = new_order
                if save_json_file(self.SETTINGS_FILE, self.app_settings):
                    # Reload categories with new order
                    render_category_buttons()
            
            CategoryOrderDialog(self.root, categories, on_save)
        
        tk.Button(header_bar, text="Volgorde aanpassen", command=open_cat_order_dialog, bg="#E1E1FF").pack(side=tk.LEFT, padx=8)
        
        # Modern category grid
        category_container = tk.Frame(menu_selection_frame, padx=4, pady=4, bg="#ECECEC")
        category_container.pack(fill=tk.X)
        
        self.modern_menu_grids = ModernMenuGrids(
            category_container,
            on_category_select=self.on_select_categorie,
            on_product_select=self.render_opties
        )
        
        def render_category_buttons():
            # Clear existing category frames to prevent duplicates
            for widget in category_container.winfo_children():
                widget.destroy()
            
            cats = get_ordered_categories()
            cols = max(1, int(category_columns_var.get() or 1))
            category_frame = self.modern_menu_grids.create_category_grid(cats, columns=cols, parent_frame=category_container)
            category_frame.pack(fill=tk.X)
            # Update selection if category is already selected
            if self.state.get("categorie"):
                self.modern_menu_grids.set_category_selection(self.state["categorie"])
        
        render_category_buttons()
        category_columns_var.trace_add("write", lambda *_: render_category_buttons())
        
        # Productgrid - original version
        product_display_frame = tk.Frame(menu_selection_frame, padx=5, pady=5)
        product_display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product title and order button frame
        product_header_frame = tk.Frame(product_display_frame)
        product_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.producten_titel = tk.Label(product_header_frame, text="Selecteer Categorie", font=("Arial", 13, "bold"))
        self.producten_titel.pack(side=tk.LEFT, anchor="w")
        
        def open_product_order_dialog():
            category_name = self.state.get("categorie")
            if not category_name:
                messagebox.showwarning("Geen Categorie", "Selecteer eerst een categorie om de product volgorde aan te passen.")
                return
            
            products = self.state.get("producten", [])
            if not products:
                messagebox.showwarning("Geen Producten", "Deze categorie bevat geen producten.")
                return
            
            def on_save(new_order: List[str]) -> None:
                if "product_order" not in self.app_settings:
                    self.app_settings["product_order"] = {}
                self.app_settings["product_order"][category_name] = new_order
                if save_json_file(self.SETTINGS_FILE, self.app_settings):
                    # Reload products with new order
                    self.on_select_categorie(category_name)
            
            ProductOrderDialog(self.root, category_name, products, on_save)
        
        self.product_order_btn = tk.Button(
            product_header_frame,
            text="📋 Product Volgorde",
            font=("Arial", 9),
            bg="#E1E1FF",
            command=open_product_order_dialog,
            state=tk.DISABLED  # Disabled until category is selected
        )
        self.product_order_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.product_grid_holder = tk.Frame(product_display_frame)
        self.product_grid_holder.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # ========== RECHTERKANT: BESTELOVERZICHT ==========
        right_panel = tk.Frame(self.menu_main_panel)
        self.menu_main_panel.add(right_panel, minsize=350)
        
        # Statistics dashboard (only in front mode)
        if self.mode == "front":
            self._setup_statistics_dashboard(right_panel)
        
        self.bestel_frame = tk.LabelFrame(right_panel, text="Besteloverzicht", padx=10, pady=10)
        self.bestel_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollbar for overview
        overview_container = tk.Frame(self.bestel_frame)
        overview_container.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        
        scrollbar_overzicht = tk.Scrollbar(overview_container, orient=tk.VERTICAL)
        scrollbar_overzicht.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.overzicht = tk.Text(
            overview_container,
            height=10,
            width=40,
            font=("Arial", 10),
            bg="#FFFFFF",
            fg="#212529",
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=10,
            wrap=tk.WORD,
            yscrollcommand=scrollbar_overzicht.set,
            cursor="arrow"
        )
        self.overzicht.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_overzicht.config(command=self.overzicht.yview)
        
        # Configure text tags for enhanced styling
        self.overzicht.tag_configure("header", font=("Arial", 12, "bold"), foreground="#212529")
        self.overzicht.tag_configure("section", font=("Arial", 9, "bold"), foreground="#0D6EFD")
        self.overzicht.tag_configure("item_header", font=("Arial", 10, "bold"), foreground="#212529")
        self.overzicht.tag_configure("item_number", font=("Arial", 9), foreground="#6C757D")
        self.overzicht.tag_configure("price", font=("Arial", 10, "bold"), foreground="#198754")
        self.overzicht.tag_configure("free", font=("Arial", 9, "bold"), foreground="#198754", background="#D1E7DD")
        self.overzicht.tag_configure("extra", font=("Arial", 9), foreground="#6C757D")
        self.overzicht.tag_configure("note", font=("Arial", 9, "italic"), foreground="#FFC107")
        self.overzicht.tag_configure("total", font=("Arial", 12, "bold"), foreground="#198754")
        self.overzicht.tag_configure("delivery_time", font=("Arial", 9, "bold"), foreground="#0D6EFD")
        self.overzicht.tag_configure("separator", foreground="#DEE2E6")
        self.overzicht.tag_configure("category_subtotal", font=("Arial", 9, "bold"), foreground="#6C757D")
        
        # Duidelijke regel-selectie in het besteloverzicht (behouden voor functionaliteit)
        self.overzicht.tag_configure("sel_line", background="#FFF3CD")
        self.overzicht.tag_configure("sel_line_text", foreground="#0D47A1")
        
        def _clear_line_highlight():
            self.overzicht.tag_remove("sel_line", "1.0", tk.END)
            self.overzicht.tag_remove("sel_line_text", "1.0", tk.END)
        
        def _highlight_line(line_index_str):
            line_start = f"{line_index_str.split('.')[0]}.0"
            line_end = f"{line_index_str.split('.')[0]}.end"
            self.overzicht.tag_add("sel_line", line_start, line_end)
            self.overzicht.tag_add("sel_line_text", line_start, line_end)
        
        def _on_click_select_line(event):
            try:
                index = self.overzicht.index(f"@{event.x},{event.y}")
                _clear_line_highlight()
                _highlight_line(index)
            except Exception:
                pass
        
        def _on_key_move_selection(event):
            try:
                self.overzicht.after_idle(lambda: (_clear_line_highlight(),
                                                  _highlight_line(self.overzicht.index(tk.INSERT))))
            except Exception:
                pass
        
        self.overzicht.bind("<Button-1>", _on_click_select_line)
        self.overzicht.bind("<Up>", _on_key_move_selection)
        self.overzicht.bind("<Down>", _on_key_move_selection)
        self.overzicht.bind("<Home>", _on_key_move_selection)
        self.overzicht.bind("<End>", _on_key_move_selection)
        
        # Bewerkingknoppen
        btns = tk.Frame(self.bestel_frame)
        btns.pack(fill=tk.X)
        
        # Print knop
        tk.Button(btns, text="Print", command=self.show_print_preview, bg="#D1FFE1").pack(side=tk.LEFT, padx=(0, 8))
        
        def _get_selected_indices_from_text():
            try:
                index = self.overzicht.index("insert")
                line_no = int(index.split('.')[0]) - 2
                if line_no >= 0:
                    line_text = self.overzicht.get(f"{int(index.split('.')[0])}.0", f"{int(index.split('.')[0])}.end")
                    if line_text.startswith('['):
                        shown = int(line_text.split(']')[0][1:])
                        return [shown - 1]
                return []
            except:
                return []
        
        def verwijder_geselecteerd():
            idxs = _get_selected_indices_from_text()
            if not idxs:
                messagebox.showinfo("Selectie", "Plaats de cursor op de regel die je wilt verwijderen.")
                return
            for i in sorted(idxs, reverse=True):
                if 0 <= i < len(self.bestelregels):
                    self.bestelregels.pop(i)
            self.update_overzicht()
        
        def wis_alles():
            if self.bestelregels and messagebox.askyesno("Bevestigen", "Alle items uit de bestelling verwijderen?"):
                self.bestelregels.clear()
                self.update_overzicht()
        
        def verplaats_omhoog():
            idxs = _get_selected_indices_from_text()
            if idxs:
                i = idxs[0]
                if 0 < i < len(self.bestelregels):
                    self.bestelregels[i - 1], self.bestelregels[i] = self.bestelregels[i], self.bestelregels[i - 1]
                    self.update_overzicht()
        
        def verplaats_omlaag():
            idxs = _get_selected_indices_from_text()
            if idxs:
                i = idxs[0]
                if 0 <= i < len(self.bestelregels) - 1:
                    self.bestelregels[i + 1], self.bestelregels[i] = self.bestelregels[i], self.bestelregels[i + 1]
                    self.update_overzicht()
        
        def wijzig_aantal():
            idxs = _get_selected_indices_from_text()
            if not idxs:
                messagebox.showinfo("Selectie", "Plaats de cursor op de regel die je wilt wijzigen.")
                return
            i = idxs[0]
            if 0 <= i < len(self.bestelregels):
                nieuw = simpledialog.askinteger("Aantal wijzigen", "Nieuw aantal:", minvalue=1, maxvalue=99,
                                                initialvalue=self.bestelregels[i]['aantal'])
                if nieuw:
                    self.bestelregels[i]['aantal'] = int(nieuw)
                    self.update_overzicht()
        
        tk.Button(btns, text="Verwijder regel", command=verwijder_geselecteerd, bg="#FFADAD").pack(side=tk.LEFT)
        tk.Button(btns, text="Alles wissen", command=wis_alles, bg="#FFD1D1").pack(side=tk.LEFT, padx=6)
        tk.Button(btns, text="Omhoog", command=verplaats_omhoog, bg="#E1E1FF").pack(side=tk.LEFT, padx=(12, 2))
        tk.Button(btns, text="Omlaag", command=verplaats_omlaag, bg="#E1E1FF").pack(side=tk.LEFT, padx=2)
        tk.Button(btns, text="Wijzig aantal", command=wijzig_aantal, bg="#D1FFD1").pack(side=tk.RIGHT)
        
        self.overzicht.config(cursor="arrow")
        self.update_overzicht()
    
    def _setup_clipboard_monitoring(self) -> None:
        """Setup and start clipboard monitoring for phone numbers."""
        if not self.clipboard_monitor:
            return
        
        # Check if clipboard monitoring is available
        if not self.clipboard_monitor.is_available():
            logger.info("Clipboard monitoring not available (pywin32 not installed)")
            return
        
        # Define callback for detected phone numbers
        def on_phone_detected(phone_number: str) -> None:
            """Handle phone number detected in clipboard - fill in form."""
            if not hasattr(self, 'enhanced_customer_form') or not self.enhanced_customer_form:
                return
            
            # Use root.after to ensure thread-safe UI update
            self.root.after(0, lambda: self._handle_clipboard_phone(phone_number))
        
        # Start monitoring
        if self.clipboard_monitor.start_monitoring(on_phone_detected):
            logger.info("Clipboard monitoring started")
        else:
            logger.warning("Failed to start clipboard monitoring")
    
    def _handle_clipboard_phone(self, phone_number: str) -> None:
        """
        Handle phone number detected from clipboard.
        
        Args:
            phone_number: Phone number detected in clipboard
        """
        if not hasattr(self, 'enhanced_customer_form') or not self.enhanced_customer_form:
            return
        
        # Only fill if phone field is empty or different
        current_phone = self.enhanced_customer_form.telefoon_entry.get().strip() if self.enhanced_customer_form.telefoon_entry else ""
        
        # Only auto-fill if field is empty or user is actively using clipboard
        if not current_phone or current_phone == phone_number:
            try:
                self.enhanced_customer_form.set_phone_number(phone_number, auto_fill=True)
                logger.info(f"Phone number from clipboard filled: {phone_number}")
                
                # Show brief notification
                if hasattr(self, 'root') and self.root:
                    # Visual feedback in status label
                    if hasattr(self.enhanced_customer_form, 'status_label') and self.enhanced_customer_form.status_label:
                        self.enhanced_customer_form.status_label.config(
                            text="📋 Telefoonnummer gekopieerd",
                            bg=self.enhanced_customer_form.COLORS.get('bg_info', '#E3F2FD'),
                            fg=self.enhanced_customer_form.COLORS.get('text_primary', '#000000')
                        )
                        # Clear status after 2 seconds
                        self.root.after(2000, lambda: self.enhanced_customer_form.status_label.config(
                            text="",
                            bg=self.enhanced_customer_form.COLORS.get('bg_primary', '#FFFFFF')
                        ) if hasattr(self.enhanced_customer_form, 'status_label') and self.enhanced_customer_form.status_label else None)
            except Exception as e:
                logger.exception(f"Error handling clipboard phone number: {e}")
    
    def run(self) -> None:
        """Start the application main loop."""
        if not self.root:
            self.setup_ui()
        self.root.mainloop()
    
    def show_mode_selector(self) -> None:
        """Show mode selector dialog to switch modes."""
        # Create a new Tk root for the mode selector (it needs a Tk root, not Toplevel)
        temp_root = tk.Tk()
        temp_root.withdraw()  # Hide it initially
        
        mode_selector = ModeSelector(temp_root)
        selected_mode = mode_selector.show()
        
        # Clean up
        temp_root.destroy()
        
        if selected_mode and selected_mode != self.mode:
            # User selected a different mode, restart application
            self.switch_mode(selected_mode)
    
    def switch_mode(self, new_mode: str) -> None:
        """Switch to a different mode by restarting the application."""
        from tkinter import messagebox
        mode_name = "Admin Modus" if new_mode == "back" else "Kassa Modus"
        result = messagebox.askyesno(
            "Modus wisselen",
            f"Weet u zeker dat u naar {mode_name} wilt wisselen?\n\n"
            "De applicatie wordt opnieuw gestart.",
            parent=self.root
        )
        if result:
            self.root.quit()
            self.root.destroy()
            # Restart in new mode
            import sys
            import os
            python = sys.executable
            # Filter out existing mode arguments
            args = [arg for arg in sys.argv if not arg.startswith("--mode=")]
            args.append(f"--mode={new_mode}")
            os.execl(python, python, *args)
    
    def switch_to_admin_mode(self) -> None:
        """Switch to Admin mode by restarting the application."""
        self.switch_mode("back")
    
    def switch_to_front_mode(self) -> None:
        """Switch to Front (Kassa) mode by restarting the application."""
        self.switch_mode("front")


def main() -> None:
    """Main entry point for the application."""
    import sys
    
    # Check for command line mode argument
    selected_mode = None
    if "--mode=front" in sys.argv:
        selected_mode = "front"
    elif "--mode=back" in sys.argv:
        selected_mode = "back"
    
    # If no mode specified, show mode selector
    if not selected_mode:
        # Create root window for mode selector (will be used as dialog)
        temp_root = tk.Tk()
        
        # Show mode selector (uses temp_root as dialog window)
        mode_selector = ModeSelector(temp_root)
        selected_mode = mode_selector.show()
        
        # Destroy temporary root after selection
        temp_root.destroy()
        
        # If no mode selected, exit
        if not selected_mode:
            logger.warning("No mode selected, exiting application")
            return
    
    # Log selected mode
    logger.info(f"Starting application in {selected_mode.upper()} mode")
    
    # Create and run application with selected mode
    app = PizzeriaApp(mode=selected_mode)
    app.setup_ui()
    app.run()


if __name__ == "__main__":
    main()

