"""
Enhanced Customer Form UI Component

Modern, user-friendly customer input form with improved UX.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, Any, List
from logging_config import get_logger
from business.customer_handler import CustomerHandler
from utils.address_utils import on_adres_entry, selectie_suggestie, reload_straatnamen
from database import DatabaseContext

logger = get_logger("pizzeria.ui.customer_form_enhanced")


class EnhancedCustomerForm:
    """Enhanced customer form with modern UI and better UX."""
    
    # Modern color scheme
    COLORS = {
        'bg_primary': '#F8F9FA',
        'bg_secondary': '#FFFFFF',
        'bg_success': '#D1E7DD',
        'bg_info': '#CFE2FF',
        'bg_warning': '#FFF3CD',
        'text_primary': '#212529',
        'text_secondary': '#6C757D',
        'border': '#DEE2E6',
        'accent': '#0D6EFD',
        'success': '#198754',
        'input_bg': '#FFFFFF',
        'input_focus': '#E7F1FF'
    }
    
    def __init__(
        self,
        parent: tk.Frame,
        postcodes: List[str],
        root_window: tk.Tk,
        on_search_callback: Optional[Callable] = None
    ):
        """
        Initialize enhanced customer form.
        
        Args:
            parent: Parent frame widget
            postcodes: List of available postcodes
            root_window: Root Tkinter window (for StringVar master)
            on_search_callback: Optional callback for search button
        """
        self.parent = parent
        self.postcodes = postcodes
        self.root_window = root_window
        self.on_search_callback = on_search_callback
        self.customer_handler = CustomerHandler()
        
        # Widget references
        self.telefoon_entry: Optional[tk.Entry] = None
        self.naam_entry: Optional[tk.Entry] = None
        self.adres_entry: Optional[tk.Entry] = None
        self.nr_entry: Optional[tk.Entry] = None
        self.postcode_var: Optional[tk.StringVar] = None
        self.opmerkingen_entry: Optional[tk.Entry] = None
        self.levertijd_entry: Optional[tk.Entry] = None
        self.lb_suggesties: Optional[tk.Listbox] = None
        self.status_label: Optional[tk.Label] = None
        self.afhaal_var: Optional[tk.BooleanVar] = None
        
        # Customer found state
        self.customer_found = False
        
        self._create_form()
    
    def _create_form(self) -> None:
        """Create the enhanced customer form."""
        # Main container with compact styling (less padding for more space)
        self.klant_frame = tk.LabelFrame(
            self.parent,
            text="👤 Klantgegevens",
            font=("Arial", 10, "bold"),
            padx=8,
            pady=8,
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary'],
            relief="flat",
            bd=1
        )
        self.klant_frame.pack(fill=tk.X, pady=(0, 0))  # No bottom padding to align with categories
        
        # Create form sections
        self._create_order_type_section()  # Afhaal/Bezorging keuze
        self._create_contact_section()
        self._create_address_section()
        self._create_additional_section()
    
    def _create_order_type_section(self) -> None:
        """Create order type selection (Afhaal/Bezorging)."""
        type_frame = tk.Frame(self.klant_frame, bg=self.COLORS['bg_primary'])
        type_frame.pack(fill=tk.X, pady=(0, 6))
        
        tk.Label(
            type_frame,
            text="📦 Besteltype *",
            font=("Arial", 9, "bold"),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.afhaal_var = tk.BooleanVar(master=self.root_window, value=False)
        
        # Bezorging radio button (default)
        bezorging_radio = tk.Radiobutton(
            type_frame,
            text="🚚 Bezorging",
            variable=self.afhaal_var,
            value=False,
            font=("Arial", 10),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary'],
            activebackground=self.COLORS['bg_primary'],
            command=self._on_order_type_change
        )
        bezorging_radio.pack(side=tk.LEFT, padx=(0, 15))
        
        # Afhaal radio button
        afhaal_radio = tk.Radiobutton(
            type_frame,
            text="🏪 Afhaal (10% korting)",
            variable=self.afhaal_var,
            value=True,
            font=("Arial", 10, "bold"),
            bg=self.COLORS['bg_primary'],
            fg="#198754",
            activebackground=self.COLORS['bg_primary'],
            command=self._on_order_type_change
        )
        afhaal_radio.pack(side=tk.LEFT, padx=(0, 15))
        
        # Nieuw button - clear all customer data
        nieuw_btn = tk.Button(
            type_frame,
            text="Nieuw",
            command=self.clear_form,
            bg="#DC3545",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2"
        )
        nieuw_btn.pack(side=tk.LEFT)
    
    def _on_order_type_change(self) -> None:
        """Handle order type change (Afhaal/Bezorging)."""
        is_afhaal = self.afhaal_var.get()
        
        # Show/hide address fields based on order type
        if hasattr(self, 'adres_entry') and self.adres_entry:
            if is_afhaal:
                # Hide/disable address fields
                self.adres_entry.config(state=tk.DISABLED, bg="#E9ECEF")
                if hasattr(self, 'nr_entry') and self.nr_entry:
                    self.nr_entry.config(state=tk.DISABLED, bg="#E9ECEF")
                if hasattr(self, 'postcode_combo_ref') and self.postcode_combo_ref:
                    self.postcode_combo_ref.config(state=tk.DISABLED)
                if hasattr(self, 'postcode_var') and self.postcode_var:
                    self.postcode_var.set("")
                # Update labels to show fields are not required
                if hasattr(self, 'street_label') and self.street_label:
                    self.street_label.config(text="📍 Adres", fg="#6C757D")
                if hasattr(self, 'nr_label') and self.nr_label:
                    self.nr_label.config(text="Nr", fg="#6C757D")
                if hasattr(self, 'postcode_label') and self.postcode_label:
                    self.postcode_label.config(text="🏘️ Postcode/Gemeente", fg="#6C757D")
                if hasattr(self, 'lb_suggesties') and self.lb_suggesties:
                    self.lb_suggesties.grid_remove()
                # Clear address fields
                self.adres_entry.delete(0, tk.END)
                if hasattr(self, 'nr_entry') and self.nr_entry:
                    self.nr_entry.delete(0, tk.END)
            else:
                # Show/enable address fields
                self.adres_entry.config(state=tk.NORMAL, bg=self.COLORS['input_bg'])
                if hasattr(self, 'nr_entry') and self.nr_entry:
                    self.nr_entry.config(state=tk.NORMAL, bg=self.COLORS['input_bg'])
                if hasattr(self, 'postcode_combo_ref') and self.postcode_combo_ref:
                    self.postcode_combo_ref.config(state="readonly")
                if hasattr(self, 'postcode_var') and self.postcodes:
                    self.postcode_var.set(self.postcodes[0])
                # Restore labels to show fields are required
                if hasattr(self, 'street_label') and self.street_label:
                    self.street_label.config(text="📍 Adres *", fg=self.COLORS['text_primary'])
                if hasattr(self, 'nr_label') and self.nr_label:
                    self.nr_label.config(text="Nr", fg=self.COLORS['text_primary'])
                if hasattr(self, 'postcode_label') and self.postcode_label:
                    self.postcode_label.config(text="🏘️ Postcode/Gemeente *", fg=self.COLORS['text_primary'])
        
        # Trigger overview update if app is available
        try:
            # Check if app reference is stored directly
            if hasattr(self, 'app') and self.app:
                self.app.update_overzicht()
            else:
                # Try to find app through widget hierarchy
                widget = self.klant_frame
                while widget:
                    if hasattr(widget, 'master') and hasattr(widget.master, 'app'):
                        widget.master.app.update_overzicht()
                        break
                    widget = widget.master if hasattr(widget, 'master') else None
        except Exception:
            pass  # Silently fail if update not possible
    
    def _create_contact_section(self) -> None:
        """Create contact information section (phone, name) - horizontal compact layout."""
        contact_frame = tk.Frame(self.klant_frame, bg=self.COLORS['bg_primary'])
        contact_frame.pack(fill=tk.X, pady=(0, 4))
        
        # All contact fields on one line: Tel, Naam, buttons
        phone_label = tk.Label(
            contact_frame,
            text="📞 Tel *",
            font=("Arial", 9, "bold"),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary']
        )
        phone_label.grid(row=0, column=0, sticky="w", padx=(0, 6))
        
        self.telefoon_entry = tk.Entry(
            contact_frame,
            width=18,
            font=("Arial", 10),
            bg=self.COLORS['input_bg'],
            relief="solid",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['accent']
        )
        self.telefoon_entry.grid(row=0, column=1, sticky="w", padx=(0, 6))
        
        # Compact search button
        search_btn = tk.Button(
            contact_frame,
            text="🔍",
            command=self._on_search_click,
            bg=self.COLORS['accent'],
            fg="white",
            font=("Arial", 8),
            relief="flat",
            padx=5,
            pady=2,
            cursor="hand2"
        )
        search_btn.grid(row=0, column=2, sticky="w", padx=(0, 2))
        
        # Status indicator (smaller)
        self.status_label = tk.Label(
            contact_frame,
            text="",
            font=("Arial", 7),
            bg=self.COLORS['bg_primary'],
            width=6,
            anchor="w"
        )
        self.status_label.grid(row=0, column=3, sticky="w", padx=(0, 4))
        
        # Recent customers button (compact)
        recent_btn = tk.Button(
            contact_frame,
            text="📋",
            command=self._show_recent_customers,
            bg="#6C757D",
            fg="white",
            font=("Arial", 8),
            relief="flat",
            padx=5,
            pady=2,
            cursor="hand2"
        )
        recent_btn.grid(row=0, column=4, sticky="w", padx=(0, 8))
        
        # Name on same line
        name_label = tk.Label(
            contact_frame,
            text="👤 Naam",
            font=("Arial", 9, "bold"),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary']
        )
        name_label.grid(row=0, column=5, sticky="w", padx=(0, 6))
        
        self.naam_entry = tk.Entry(
            contact_frame,
            width=20,
            font=("Arial", 10),
            bg=self.COLORS['input_bg'],
            relief="solid",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['accent']
        )
        self.naam_entry.grid(row=0, column=6, sticky="w")
        
        # Bind events for auto-fill
        self.telefoon_entry.bind(
            "<Return>",
            lambda e: self._auto_fill_customer()
        )
        self.telefoon_entry.bind(
            "<FocusOut>",
            lambda e: self._auto_fill_customer()
        )
        self.telefoon_entry.bind(
            "<KeyRelease>",
            lambda e: self._on_phone_change()
        )
        # Auto-normalize phone number on paste (Ctrl+V)
        self.telefoon_entry.bind(
            "<Control-v>",
            lambda e: self._handle_paste_phone(e)
        )
        self.telefoon_entry.bind(
            "<Command-v>",
            lambda e: self._handle_paste_phone(e)
        )
    
    def _create_address_section(self) -> None:
        """Create address section (street, number, postcode) - all on one line."""
        address_frame = tk.Frame(self.klant_frame, bg=self.COLORS['bg_primary'])
        address_frame.pack(fill=tk.X, pady=(0, 4))
        
        # All address fields on one line: Adres, Nr, Postcode
        self.street_label = tk.Label(
            address_frame,
            text="📍 Adres *",
            font=("Arial", 9, "bold"),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary']
        )
        self.street_label.grid(row=0, column=0, sticky="w", padx=(0, 6))
        
        # Address entry - larger
        self.adres_entry = tk.Entry(
            address_frame,
            width=22,
            font=("Arial", 10),
            bg=self.COLORS['input_bg'],
            relief="solid",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['accent']
        )
        self.adres_entry.grid(row=0, column=1, sticky="w", padx=(0, 6))
        
        # House number - larger (optional for addresses like harbor numbers)
        self.nr_label = tk.Label(
            address_frame,
            text="Nr",
            font=("Arial", 9, "bold"),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary']
        )
        self.nr_label.grid(row=0, column=2, sticky="w", padx=(0, 4))
        
        self.nr_entry = tk.Entry(
            address_frame,
            width=8,
            font=("Arial", 10),
            bg=self.COLORS['input_bg'],
            relief="solid",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['accent']
        )
        self.nr_entry.grid(row=0, column=3, sticky="w", padx=(0, 8))
        
        # Postcode on same line
        self.postcode_label = tk.Label(
            address_frame,
            text="🏘️ Postcode *",
            font=("Arial", 9, "bold"),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary']
        )
        self.postcode_label.grid(row=0, column=4, sticky="w", padx=(0, 6))
        
        self.postcode_var = tk.StringVar(master=self.root_window)
        self.postcode_var.set(self.postcodes[0] if self.postcodes else "")
        
        self.postcode_combo_ref = ttk.Combobox(
            address_frame,
            textvariable=self.postcode_var,
            values=self.postcodes,
            state="readonly",
            width=20,
            font=("Arial", 10)
        )
        self.postcode_combo_ref.grid(row=0, column=5, sticky="w")
        
        # Address suggestions listbox - placed below the address entry (compact)
        self.lb_suggesties = tk.Listbox(
            address_frame,
            height=3,
            width=20,
            bg=self.COLORS['input_bg'],
            font=("Arial", 8),
            relief="solid",
            borderwidth=1,
            selectbackground=self.COLORS['accent'],
            selectforeground="white"
        )
        # Start hidden, will be shown with grid when suggestions are available
        self.lb_suggesties.grid(row=1, column=1, sticky="w", pady=(3, 0))
        self.lb_suggesties.grid_remove()
        
        # Bind address autocomplete
        self.adres_entry.bind(
            "<KeyRelease>",
            lambda e: self._on_address_key_release(e)
        )
        self.lb_suggesties.bind(
            "<<ListboxSelect>>",
            lambda e: selectie_suggestie(e, self.adres_entry, self.lb_suggesties)
        )
        # Also bind Enter key to select first suggestion if visible
        self.adres_entry.bind(
            "<Return>",
            lambda e: self._select_first_suggestion()
        )
    
    def _create_additional_section(self) -> None:
        """Create additional information section (notes, delivery time) - compact."""
        additional_frame = tk.Frame(self.klant_frame, bg=self.COLORS['bg_primary'])
        additional_frame.pack(fill=tk.X)
        
        # Notes section - compact, on same line as delivery time
        notes_delivery_frame = tk.Frame(additional_frame, bg=self.COLORS['bg_primary'])
        notes_delivery_frame.pack(fill=tk.X, pady=(0, 4))
        
        notes_label = tk.Label(
            notes_delivery_frame,
            text="📝 Opmerking",
            font=("Arial", 9, "bold"),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary']
        )
        notes_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self.opmerkingen_entry = tk.Entry(
            notes_delivery_frame,
            width=28,
            font=("Arial", 10),
            bg=self.COLORS['input_bg'],
            relief="solid",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['accent']
        )
        self.opmerkingen_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Delivery time section - on same line
        delivery_label = tk.Label(
            notes_delivery_frame,
            text="⏰ Levertijd",
            font=("Arial", 9, "bold"),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary']
        )
        delivery_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self.levertijd_entry = tk.Entry(
            notes_delivery_frame,
            width=16,
            font=("Arial", 10),
            bg=self.COLORS['input_focus'],
            relief="solid",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['accent']
        )
        self.levertijd_entry.pack(side=tk.LEFT)
        
        # Add placeholder
        self.levertijd_entry.insert(0, "bijv. 19:30")
        self.levertijd_entry.config(fg="gray")
        
        def on_levertijd_focus_in(e):
            if self.levertijd_entry.get() == "bijv. 19:30":
                self.levertijd_entry.delete(0, tk.END)
                self.levertijd_entry.config(fg="black")
        
        def on_levertijd_focus_out(e):
            if not self.levertijd_entry.get().strip():
                self.levertijd_entry.insert(0, "bijv. 19:30")
                self.levertijd_entry.config(fg="gray")
        
        self.levertijd_entry.bind("<FocusIn>", on_levertijd_focus_in)
        self.levertijd_entry.bind("<FocusOut>", on_levertijd_focus_out)
        
        # Info label (below the fields)
        info_label = tk.Label(
            notes_delivery_frame,
            text="(Optioneel - laat leeg voor automatische berekening)",
            font=("Arial", 7),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_secondary']
        )
        info_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def _on_phone_change(self) -> None:
        """Handle phone number change - clear status."""
        if self.status_label:
            self.status_label.config(text="", bg=self.COLORS['bg_primary'])
    
    def _handle_paste_phone(self, event: Optional[tk.Event] = None) -> Optional[str]:
        """Handle paste in phone field - normalize phone number."""
        try:
            # Get clipboard content
            clipboard_text = self.root_window.clipboard_get()
            
            if clipboard_text:
                # Normalize phone number
                phone_number = self._normalize_phone_from_text(clipboard_text)
                
                if phone_number:
                    # Clear field and insert normalized number
                    self.telefoon_entry.delete(0, tk.END)
                    self.telefoon_entry.insert(0, phone_number)
                    # Auto-fill customer data
                    self._auto_fill_customer()
                    
                    # Visual feedback
                    if self.status_label:
                        self.status_label.config(
                            text="📋 Telefoonnummer geplakt",
                            bg=self.COLORS['bg_info'],
                            fg=self.COLORS['text_primary']
                        )
                        self.root_window.after(2000, lambda: self.status_label.config(
                            text="",
                            bg=self.COLORS['bg_primary']
                        ) if self.status_label else None)
                    
                    return "break"  # Prevent default paste
        except tk.TclError:
            # Clipboard might be empty or not text
            pass
        except Exception as e:
            from logging_config import get_logger
            logger = get_logger("pizzeria.ui.customer_form")
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
    
    def _on_address_key_release(self, event: tk.Event) -> None:
        """Handle address entry key release - show suggestions."""
        # Reload street names in case new ones were added
        reload_straatnamen()
        on_adres_entry(event, self.adres_entry, self.lb_suggesties)
    
    def _select_first_suggestion(self) -> None:
        """Select first suggestion from listbox if visible."""
        if self.lb_suggesties.winfo_viewable() and self.lb_suggesties.size() > 0:
            self.lb_suggesties.selection_set(0)
            self.lb_suggesties.activate(0)
            selectie_suggestie(None, self.adres_entry, self.lb_suggesties)
    
    def _auto_fill_customer(self) -> None:
        """Auto-fill customer data based on phone number."""
        telefoon = self.telefoon_entry.get().strip()
        if not telefoon:
            if self.status_label:
                self.status_label.config(text="", bg=self.COLORS['bg_primary'])
            return
        
        klant = self.customer_handler.customer_service.find_customer(telefoon)
        
        if klant:
            # Customer found - fill fields
            self.naam_entry.delete(0, tk.END)
            self.naam_entry.insert(0, klant.get('naam', '') or "")
            self.adres_entry.delete(0, tk.END)
            self.adres_entry.insert(0, klant.get('straat', '') or "")
            self.nr_entry.delete(0, tk.END)
            self.nr_entry.insert(0, klant.get('huisnummer', '') or "")
            
            # Set postcode
            plaats = klant.get('plaats', '') or ""
            gevonden_postcode = ""
            for p in self.postcodes:
                if plaats in p:
                    gevonden_postcode = p
                    break
            self.postcode_var.set(gevonden_postcode if gevonden_postcode else self.postcodes[0])
            
            # Visual feedback
            if self.status_label:
                self.status_label.config(
                    text="✓ Klant gevonden",
                    fg=self.COLORS['success'],
                    bg=self.COLORS['bg_success'],
                    font=("Arial", 9, "bold")
                )
            self.customer_found = True
            
            # Highlight filled fields briefly
            self._highlight_field(self.naam_entry)
            self._highlight_field(self.adres_entry)
            self._highlight_field(self.nr_entry)
        else:
            # Customer not found
            if self.status_label:
                self.status_label.config(
                    text="⚠ Nieuw klant",
                    fg="#856404",
                    bg=self.COLORS['bg_warning'],
                    font=("Arial", 9, "bold")
                )
            self.customer_found = False
    
    def _highlight_field(self, entry: tk.Entry) -> None:
        """Briefly highlight a field to show it was auto-filled."""
        original_bg = entry.cget('bg')
        entry.config(bg=self.COLORS['bg_success'])
        self.root_window.after(500, lambda: entry.config(bg=original_bg))
    
    def _on_search_click(self) -> None:
        """Handle search button click."""
        if self.on_search_callback:
            self.on_search_callback()
        else:
            # Default search behavior
            from modules.klanten import open_klanten_zoeken
            open_klanten_zoeken(
                self.root_window,
                self.telefoon_entry,
                self.naam_entry,
                self.adres_entry,
                self.nr_entry,
                self.postcode_var,
                self.postcodes
            )
    
    def _get_recent_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent customers based on last order date.
        
        Args:
            limit: Maximum number of customers to return
            
        Returns:
            List of customer dictionaries with order info
        """
        try:
            with DatabaseContext() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT k.id, k.telefoon, k.naam, k.straat, k.huisnummer, k.plaats,
                           MAX(b.datum || ' ' || b.tijd) as laatste_bestelling,
                           COUNT(b.id) as aantal_bestellingen
                    FROM klanten k
                    LEFT JOIN bestellingen b ON k.id = b.klant_id
                    WHERE b.id IS NOT NULL
                    GROUP BY k.id
                    ORDER BY laatste_bestelling DESC
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.exception(f"Error fetching recent customers: {e}")
            return []
    
    def _show_recent_customers(self) -> None:
        """Show dialog with recent customers for quick selection."""
        recent_customers = self._get_recent_customers(15)
        
        if not recent_customers:
            messagebox.showinfo("Geen recente klanten", "Er zijn nog geen recente klanten gevonden.")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.root_window)
        dialog.title("📋 Recente Klanten")
        dialog.transient(self.root_window)
        dialog.grab_set()
        dialog.geometry("600x400")
        
        # Search frame
        search_frame = tk.Frame(dialog, padx=10, pady=10)
        search_frame.pack(fill=tk.X)
        
        tk.Label(
            search_frame,
            text="Zoek:",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Arial", 10), width=30)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        search_entry.focus()
        
        # Results frame
        results_frame = tk.Frame(dialog)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Treeview for customers
        columns = ('telefoon', 'naam', 'adres', 'laatste_bestelling', 'aantal')
        tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=12)
        
        tree.heading('telefoon', text='Telefoon')
        tree.heading('naam', text='Naam')
        tree.heading('adres', text='Adres')
        tree.heading('laatste_bestelling', text='Laatste Bestelling')
        tree.heading('aantal', text='Aantal')
        
        tree.column('telefoon', width=120)
        tree.column('naam', width=150)
        tree.column('adres', width=180)
        tree.column('laatste_bestelling', width=140)
        tree.column('aantal', width=60)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def populate_tree(customers: List[Dict[str, Any]]) -> None:
            """Populate treeview with customers."""
            tree.delete(*tree.get_children())
            for customer in customers:
                adres = f"{customer.get('straat', '') or ''} {customer.get('huisnummer', '') or ''}".strip()
                laatste = customer.get('laatste_bestelling', '') or 'Nog geen bestelling'
                aantal = customer.get('aantal_bestellingen', 0) or 0
                
                tree.insert("", "end", iid=str(customer['id']), values=(
                    customer.get('telefoon', ''),
                    customer.get('naam', '') or '',
                    adres,
                    laatste[:16] if len(laatste) > 16 else laatste,
                    aantal
                ))
        
        def filter_customers(*args) -> None:
            """Filter customers based on search term."""
            term = search_var.get().strip().lower()
            if not term:
                populate_tree(recent_customers)
                return
            
            filtered = [
                c for c in recent_customers
                if term in (c.get('telefoon', '') or '').lower()
                or term in (c.get('naam', '') or '').lower()
                or term in (c.get('straat', '') or '').lower()
            ]
            populate_tree(filtered)
        
        def select_customer() -> None:
            """Select customer and fill form."""
            selection = tree.selection()
            if not selection:
                messagebox.showinfo("Selectie", "Selecteer een klant uit de lijst.")
                return
            
            customer_id = int(selection[0])
            customer = next((c for c in recent_customers if c['id'] == customer_id), None)
            
            if customer:
                # Fill form with customer data
                self.telefoon_entry.delete(0, tk.END)
                self.telefoon_entry.insert(0, customer.get('telefoon', ''))
                self._auto_fill_customer()
                dialog.destroy()
        
        # Populate initial list
        populate_tree(recent_customers)
        
        # Bind events
        search_var.trace_add("write", filter_customers)
        tree.bind("<Double-1>", lambda e: select_customer())
        search_entry.bind("<Return>", lambda e: select_customer() if tree.selection() else None)
        
        # Buttons
        btn_frame = tk.Frame(dialog, padx=10, pady=10)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(
            btn_frame,
            text="Selecteer Klant",
            command=select_customer,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="Sluiten",
            command=dialog.destroy,
            bg="#6C757D",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT)
    
    def get_customer_data(self) -> Dict[str, Any]:
        """Get current customer data from form."""
        levertijd = self.levertijd_entry.get().strip()
        if levertijd == "bijv. 19:30":
            levertijd = ""
        
        is_afhaal = self.afhaal_var.get() if self.afhaal_var else False
        
        return {
            "telefoon": self.telefoon_entry.get().strip(),
            "naam": self.naam_entry.get().strip(),
            "adres": "" if is_afhaal else self.adres_entry.get().strip(),
            "nr": "" if is_afhaal else self.nr_entry.get().strip(),
            "postcode_gemeente": "" if is_afhaal else self.postcode_var.get(),
            "opmerking": self.opmerkingen_entry.get().strip(),
            "levertijd": levertijd if levertijd else None,
            "afhaal": is_afhaal,
            "korting_percentage": 10.0 if is_afhaal else 0.0
        }
    
    def clear_form(self) -> None:
        """Clear all form fields."""
        self.telefoon_entry.delete(0, tk.END)
        self.naam_entry.delete(0, tk.END)
        self.adres_entry.delete(0, tk.END)
        self.nr_entry.delete(0, tk.END)
        self.opmerkingen_entry.delete(0, tk.END)
        if self.postcodes:
            self.postcode_var.set(self.postcodes[0])
        if self.levertijd_entry:
            self.levertijd_entry.delete(0, tk.END)
            self.levertijd_entry.insert(0, "bijv. 19:30")
            self.levertijd_entry.config(fg="gray")
        if self.status_label:
            self.status_label.config(text="", bg=self.COLORS['bg_primary'])
        if self.afhaal_var:
            self.afhaal_var.set(False)
            self._on_order_type_change()  # Reset address fields
        self.customer_found = False
    
    def set_customer_data(self, data: Dict[str, Any]) -> None:
        """Set form fields from customer data."""
        if data.get('telefoon'):
            self.telefoon_entry.delete(0, tk.END)
            self.telefoon_entry.insert(0, data.get('telefoon', ''))
        if data.get('naam'):
            self.naam_entry.delete(0, tk.END)
            self.naam_entry.insert(0, data.get('naam', ''))
        if data.get('adres'):
            self.adres_entry.delete(0, tk.END)
            self.adres_entry.insert(0, data.get('adres', ''))
        if data.get('nr'):
            self.nr_entry.delete(0, tk.END)
            self.nr_entry.insert(0, data.get('nr', ''))
        if data.get('postcode_gemeente'):
            self.postcode_var.set(data.get('postcode_gemeente', ''))
        if data.get('opmerking'):
            self.opmerkingen_entry.delete(0, tk.END)
            self.opmerkingen_entry.insert(0, data.get('opmerking', ''))
        if data.get('levertijd') and self.levertijd_entry:
            self.levertijd_entry.delete(0, tk.END)
            self.levertijd_entry.insert(0, data.get('levertijd', ''))
            self.levertijd_entry.config(fg="black")
    
    def set_phone_number(self, phone_number: str, auto_fill: bool = True) -> None:
        """
        Set phone number in the form (for external integrations like Webex).
        
        Args:
            phone_number: Phone number to set
            auto_fill: If True, automatically fill customer data if found
        """
        if not self.telefoon_entry:
            return
        
        # Validate phone number
        if not phone_number or not phone_number.strip():
            return
        
        # Clear and set phone number
        try:
            self.telefoon_entry.delete(0, tk.END)
            self.telefoon_entry.insert(0, phone_number.strip())
        except Exception as e:
            from logging_config import get_logger
            logger = get_logger("pizzeria.ui.customer_form")
            logger.exception(f"Error setting phone number in entry: {e}")
            return
        
        # Auto-fill customer data if requested
        if auto_fill:
            self._auto_fill_customer()
        
        # Visual feedback
        if self.status_label:
            self.status_label.config(
                text="📞 Inkomend gesprek",
                bg=self.COLORS['bg_info'],
                fg=self.COLORS['text_primary']
            )
            # Clear status after 3 seconds
            self.root_window.after(3000, lambda: self.status_label.config(
                text="",
                bg=self.COLORS['bg_primary']
            ) if self.status_label else None)

