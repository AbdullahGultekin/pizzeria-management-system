"""
Online Bestellingen Module voor Kassa Systeem

Deze module toont online bestellingen in real-time en maakt het mogelijk om:
- Bestellingen te bekijken en beheren
- Status te wijzigen (Nieuw -> In de keuken -> Onderweg)
- Koeriers toe te wijzen
- Bonnen af te drukken
- Routes te bekijken
- Levertijden aan te passen
"""

import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, scrolledtext
from typing import Dict, List, Optional, Any
import json
import datetime
import threading
import time
import requests
import webbrowser
from logging_config import get_logger

logger = get_logger("pizzeria.modules.online_bestellingen")

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
API_USERNAME = "admin"  # TODO: Load from config
API_PASSWORD = "admin123"  # Default password from backend

# Sound configuration
SOUND_ENABLED = True
SOUND_FILE = None  # Will be set to a default sound or user-configured sound


class OnlineBestellingenManager:
    """Manager voor online bestellingen interface."""
    
    def __init__(self, parent: tk.Widget, app_settings: Dict[str, Any], menu_data: Dict[str, Any], extras_data: Dict[str, Any]):
        """
        Initialize online bestellingen manager.
        
        Args:
            parent: Parent widget (tab frame)
            app_settings: Application settings dict
            menu_data: Menu data dict
            extras_data: Extras data dict
        """
        self.parent = parent
        self.app_settings = app_settings
        self.menu_data = menu_data
        self.extras_data = extras_data
        
        # API authentication
        self.api_token = None
        self.api_session = requests.Session()
        
        # Polling state
        self.polling_active = False
        self.polling_thread = None
        self.poll_interval = 7  # seconds
        
        # Order tracking
        self.orders: Dict[int, Dict[str, Any]] = {}
        self.confirmed_orders: set = set()  # Orders that have been confirmed (stop sound)
        self.order_timestamps: Dict[int, datetime.datetime] = {}  # Track when orders were created
        self.orders_with_levertijd: set = set()  # Orders that already have levertijd set
        
        # Auto status
        self.auto_status_enabled = True
        self.auto_status_interval = 300  # 5 minutes in seconds
        
        # UI components
        self.orders_frame = None
        self.orders_canvas = None
        self.orders_scrollbar = None
        self.status_label = None
        
        # Setup UI
        self.setup_ui()
        
        # Authenticate with API
        auth_success = self.authenticate_api()
        if not auth_success:
            self.update_status("❌ Authenticatie mislukt - controleer backend")
        else:
            self.update_status("Verbonden")
        
        # Start polling
        self.start_polling()
    
    def setup_ui(self) -> None:
        """Setup the main UI (matching the example layout)."""
        # Clear parent
        for w in self.parent.winfo_children():
            w.destroy()
        
        # Main container (no padding to match example)
        main_frame = tk.Frame(self.parent, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header bar (dark green)
        header_bar = tk.Frame(main_frame, bg="#2E7D32", height=50)
        header_bar.pack(fill=tk.X)
        header_bar.pack_propagate(False)
        
        header_content = tk.Frame(header_bar, bg="#2E7D32")
        header_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
        
        title_label = tk.Label(
            header_content,
            text="ONLINE BESTELLINGEN",
            font=("Arial", 14, "bold"),
            bg="#2E7D32",
            fg="white"
        )
        title_label.pack(side=tk.LEFT)
        
        # Refresh button
        refresh_btn = tk.Button(
            header_content,
            text="Vernieuwen (F5)",
            command=self.refresh_orders,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            relief=tk.RAISED,
            borderwidth=2
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        # Status label (hidden but kept for functionality)
        self.status_label = tk.Label(
            header_content,
            text="",
            font=("Arial", 9),
            bg="#2E7D32",
            fg="white"
        )
        self.status_label.pack(side=tk.RIGHT, padx=(0, 15))
        
        # Main content area - PanedWindow for left/right split
        content_paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashpad=2)
        content_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Orders list
        left_panel = tk.Frame(content_paned, bg="white")
        content_paned.add(left_panel, minsize=400, width=500)
        
        # Right panel - Details (empty for now)
        right_panel = tk.Frame(content_paned, bg="white")
        content_paned.add(right_panel, minsize=300)
        
        # Store right panel for future use
        self.right_panel = right_panel
        
        # Orders list container with scrollbar (grid layout like example)
        orders_list_frame = tk.Frame(left_panel, bg="white")
        orders_list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Canvas for scrolling
        self.orders_canvas = tk.Canvas(
            orders_list_frame,
            bg="#F5F5F5",  # Light gray background like example
            highlightthickness=0
        )
        self.orders_scrollbar = ttk.Scrollbar(
            orders_list_frame,
            orient="vertical",
            command=self.orders_canvas.yview
        )
        self.orders_frame = tk.Frame(self.orders_canvas, bg="#F5F5F5")
        
        self.orders_canvas_window = self.orders_canvas.create_window(
            (0, 0),
            window=self.orders_frame,
            anchor="nw"
        )
        
        self.orders_canvas.configure(yscrollcommand=self.orders_scrollbar.set)
        
        self.orders_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.orders_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind canvas resize
        self.orders_canvas.bind('<Configure>', self._on_canvas_configure)
        self.orders_frame.bind('<Configure>', self._on_frame_configure)
        
        # Bind mousewheel
        self.orders_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Store grid position for layout
        self.current_grid_row = 0
        self.current_grid_col = 0
        self.max_cols = 3  # 3 columns like in example
        
        # Footer bar (dark green)
        footer_bar = tk.Frame(main_frame, bg="#2E7D32", height=60)
        footer_bar.pack(fill=tk.X, side=tk.BOTTOM)
        footer_bar.pack_propagate(False)
        
        footer_content = tk.Frame(footer_bar, bg="#2E7D32")
        footer_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
        
        # Footer left - Date and message
        footer_left = tk.Frame(footer_content, bg="#2E7D32")
        footer_left.pack(side=tk.LEFT)
        
        now = datetime.datetime.now()
        date_text = now.strftime("%A %d/%m/%Y")
        # Translate day names
        day_translation = {
            "Monday": "Maandag", "Tuesday": "Dinsdag", "Wednesday": "Woensdag",
            "Thursday": "Donderdag", "Friday": "Vrijdag", "Saturday": "Zaterdag", "Sunday": "Zondag"
        }
        day_name = day_translation.get(now.strftime("%A"), now.strftime("%A"))
        date_text = f"{day_name} {now.strftime('%d/%m/%Y')}"
        
        date_label = tk.Label(
            footer_left,
            text=f"Online Bestellingen - {date_text}",
            font=("Arial", 10, "bold"),
            bg="#2E7D32",
            fg="white"
        )
        date_label.pack(anchor=tk.W)
        
        message_label = tk.Label(
            footer_left,
            text="Controleer de bestelling zorgvuldig voordat u verder gaat.",
            font=("Arial", 9),
            bg="#2E7D32",
            fg="white"
        )
        message_label.pack(anchor=tk.W, pady=(3, 0))
        
        # Footer right - Total
        self.total_label = tk.Label(
            footer_content,
            text="Totaal: € 0,00",
            font=("Arial", 12, "bold"),
            bg="#2E7D32",
            fg="white"
        )
        self.total_label.pack(side=tk.RIGHT)
    
    def _on_canvas_configure(self, event):
        """Update canvas window width."""
        canvas_width = event.width
        self.orders_canvas.itemconfig(self.orders_canvas_window, width=canvas_width)
    
    def _on_frame_configure(self, event):
        """Update canvas scroll region."""
        self.orders_canvas.configure(scrollregion=self.orders_canvas.bbox("all"))
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        self.orders_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def authenticate_api(self) -> bool:
        """Authenticate with the API and get token."""
        try:
            # OAuth2PasswordRequestForm expects form data, not JSON
            response = self.api_session.post(
                f"{API_BASE_URL}/auth/login",
                data={
                    "username": API_USERNAME,
                    "password": API_PASSWORD
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=2  # Short timeout
            )
            if response.status_code == 200:
                data = response.json()
                self.api_token = data.get("access_token")
                if self.api_token:
                    self.api_session.headers.update({
                        "Authorization": f"Bearer {self.api_token}"
                    })
                    logger.info("API authentication successful")
                    return True
            else:
                error_detail = response.text
                logger.debug(f"API authentication failed: {response.status_code} - {error_detail}")
            return False
        except requests.exceptions.ConnectionError:
            # Backend not available - silent fail
            return False
        except requests.exceptions.Timeout:
            return False
        except Exception as e:
            logger.debug(f"Error authenticating with API: {e}")
            return False
    
    def fetch_orders(self) -> List[Dict[str, Any]]:
        """Fetch pending online orders from API."""
        try:
            response = self.api_session.get(
                f"{API_BASE_URL}/orders/online/pending",
                timeout=2  # Short timeout to avoid hanging
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # Token expired or invalid, try to re-authenticate
                logger.warning("Token expired, re-authenticating...")
                if self.authenticate_api():
                    # Retry the request
                    response = self.api_session.get(
                        f"{API_BASE_URL}/orders/online/pending",
                        timeout=2
                    )
                    if response.status_code == 200:
                        return response.json()
                logger.debug("Re-authentication failed")
                return []
            else:
                logger.debug(f"Failed to fetch orders: {response.status_code} - {response.text}")
                return []
        except requests.exceptions.ConnectionError:
            # Backend not available - only log once per session
            if not hasattr(self, '_api_connection_logged'):
                logger.debug("Backend API not available (connection refused)")
                self._api_connection_logged = True
            return []
        except requests.exceptions.Timeout:
            return []  # Silent timeout
        except Exception as e:
            logger.debug(f"Error fetching orders: {e}")
            return []
    
    def refresh_orders(self) -> None:
        """Manually refresh orders."""
        orders = self.fetch_orders()
        self.update_orders_display(orders)
    
    def start_polling(self) -> None:
        """Start polling for new orders."""
        if self.polling_active:
            return
        
        self.polling_active = True
        
        def poll_loop():
            while self.polling_active:
                try:
                    orders = self.fetch_orders()
                    # Check for new orders
                    new_order_ids = {order['id'] for order in orders}
                    existing_order_ids = set(self.orders.keys())
                    
                    # Find new orders
                    new_orders = new_order_ids - existing_order_ids
                    if new_orders:
                        logger.info(f"New orders detected: {new_orders}")
                        # Play sound for new orders and show levertijd dialog
                        for order_id in new_orders:
                            if order_id not in self.confirmed_orders:
                                self.play_notification_sound()
                                # Track timestamp for new orders
                                for order in orders:
                                    if order['id'] == order_id:
                                        # Parse time from order
                                        try:
                                            tijd_str = order.get('tijd', '')
                                            datum_str = order.get('datum', '')
                                            if tijd_str and datum_str:
                                                # Parse time (format: HH:MM:SS or HH:MM)
                                                tijd_parts = tijd_str.split(':')
                                                if len(tijd_parts) >= 2:
                                                    uur = int(tijd_parts[0])
                                                    minuut = int(tijd_parts[1])
                                                    # Parse date (format: YYYY-MM-DD)
                                                    datum_parts = datum_str.split('-')
                                                    if len(datum_parts) == 3:
                                                        jaar = int(datum_parts[0])
                                                        maand = int(datum_parts[1])
                                                        dag = int(datum_parts[2])
                                                        self.order_timestamps[order_id] = datetime.datetime(
                                                            jaar, maand, dag, uur, minuut
                                                        )
                                        except Exception as e:
                                            logger.warning(f"Could not parse order timestamp: {e}")
                                            # Use current time as fallback
                                            self.order_timestamps[order_id] = datetime.datetime.now()
                                        
                                        # Show levertijd dialog for new orders without levertijd
                                        if order_id not in self.orders_with_levertijd and not order.get('levertijd'):
                                            self.parent.after(0, lambda o=order: self.show_levertijd_dialog(o))
                    
                    # Check for auto status updates
                    if self.auto_status_enabled:
                        self.check_auto_status_updates(orders)
                    
                    # Mark orders with levertijd
                    for order in orders:
                        if order.get('levertijd'):
                            self.orders_with_levertijd.add(order['id'])
                    
                    # Update display
                    self.parent.after(0, lambda: self.update_orders_display(orders))
                    
                    # Update status
                    self.parent.after(0, lambda: self.update_status(f"{len(orders)} bestellingen"))
                    
                except requests.exceptions.ConnectionError:
                    # Backend not available - only log once per session
                    if not hasattr(self, '_api_connection_logged'):
                        logger.debug("Backend API not available in polling loop")
                        self._api_connection_logged = True
                    self.parent.after(0, lambda: self.update_status("❌ Geen verbinding met backend"))
                except requests.exceptions.Timeout:
                    # Timeout - silent fail
                    pass
                except Exception as e:
                    logger.debug(f"Error in polling loop: {e}")
                    self.parent.after(0, lambda: self.update_status(f"Fout: {str(e)[:30]}"))
                
                time.sleep(self.poll_interval)
        
        self.polling_thread = threading.Thread(target=poll_loop, daemon=True)
        self.polling_thread.start()
    
    def stop_polling(self) -> None:
        """Stop polling for new orders."""
        self.polling_active = False
        if self.polling_thread:
            self.polling_thread.join(timeout=2)
    
    def update_status(self, message: str) -> None:
        """Update status label."""
        if self.status_label:
            self.status_label.config(text=message)
    
    def play_notification_sound(self) -> None:
        """Play notification sound for new orders."""
        if not SOUND_ENABLED:
            return
        
        try:
            import winsound
            # Play system beep (can be replaced with custom sound file)
            winsound.Beep(1000, 200)  # Frequency 1000Hz, duration 200ms
        except ImportError:
            # On non-Windows systems, try other methods
            try:
                import os
                # Try to play a system sound
                os.system("afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || echo -e '\a'")
            except:
                pass
    
    def update_orders_display(self, orders: List[Dict[str, Any]]) -> None:
        """Update the orders display (smart update - only update changed orders)."""
        # Store orders
        new_orders_dict = {order['id']: order for order in orders}
        
        # Get existing order IDs from displayed cards
        existing_order_ids = set()
        for widget in self.orders_frame.winfo_children():
            if hasattr(widget, 'order_id'):
                existing_order_ids.add(widget.order_id)
        
        # Find orders to add, update, or remove
        new_order_ids = set(new_orders_dict.keys())
        orders_to_add = new_order_ids - existing_order_ids
        orders_to_remove = existing_order_ids - new_order_ids
        orders_to_update = new_order_ids & existing_order_ids
        
        # Remove orders that are no longer in the list
        widgets_to_remove = []
        for widget in self.orders_frame.winfo_children():
            if hasattr(widget, 'order_id') and widget.order_id in orders_to_remove:
                widgets_to_remove.append(widget)
        
        for widget in widgets_to_remove:
            widget.destroy()
        
        # Reset grid position for reordering
        self.current_grid_row = 0
        self.current_grid_col = 0
        
        # Recreate all cards to maintain grid order (simpler approach for grid layout)
        # Clear all existing cards
        for widget in list(self.orders_frame.winfo_children()):
            widget.destroy()
        
        # Create all cards in order
        for order in orders:
            self.create_order_card(order)
        
        # Update stored orders
        self.orders = new_orders_dict
        
        if not new_orders_dict:
            # Show empty message if no orders
            empty_label = tk.Label(
                self.orders_frame,
                text="Geen online bestellingen",
                font=("Arial", 14),
                bg="#F5F5F5",
                fg="#999"
            )
            empty_label.grid(row=0, column=0, columnspan=self.max_cols, pady=50)
        
        # Calculate and update total
        total = sum(order.get('totaal', 0) for order in new_orders_dict.values())
        if self.total_label:
            # Format: use dot for thousands, comma for decimals
            total_str = f"{total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            self.total_label.config(text=f"Totaal: € {total_str}")
    
    def create_order_card(self, order: Dict[str, Any]) -> None:
        """Create a card widget for an order (improved professional design, compact)."""
        status = order.get('status', 'Nieuw')
        klant_adres = order.get('klant_adres', 'Geen adres')
        tijd = order.get('tijd', 'N/A')
        levertijd = order.get('levertijd', 'N/A')
        totaal = order.get('totaal', 0)
        betaalmethode = order.get('betaalmethode', 'cash')
        
        # Determine colors based on status
        if status == "In de keuken":
            status_bg = "#81C784"  # Green
            scooter_color = "#4CAF50"  # Green scooter
            status_text = "Keuken"
        elif status == "Nieuw":
            status_bg = "#64B5F6"  # Blue
            scooter_color = "#42A5F5"  # Blue scooter
            status_text = "Nieuw"
        else:  # Onderweg
            status_bg = "#9E9E9E"  # Grey
            scooter_color = "#757575"  # Grey scooter
            status_text = "Onderweg"
        
        # Card frame (white background, subtle border, compact)
        # Use grid layout for multi-column display
        card_frame = tk.Frame(
            self.orders_frame,
            bg="#F8F8F8",
            relief=tk.FLAT,
            borderwidth=1,
            padx=4,
            pady=4
        )
        # Calculate grid position
        row = self.current_grid_row // self.max_cols
        col = self.current_grid_col % self.max_cols
        card_frame.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
        
        # Set fixed width for cards (compact size)
        card_frame.config(width=160)  # Fixed width for compact cards
        
        # Update grid position
        self.current_grid_col += 1
        if self.current_grid_col % self.max_cols == 0:
            self.current_grid_row = (self.current_grid_row // self.max_cols + 1) * self.max_cols
        
        # Configure grid weights for equal column widths
        for c in range(self.max_cols):
            self.orders_frame.grid_columnconfigure(c, weight=1, uniform="orders", minsize=150)
        
        # Store order_id in widget for tracking
        card_frame.order_id = order.get('id')
        
        # Inner white frame for content (creates subtle border effect)
        inner_frame = tk.Frame(
            card_frame,
            bg="white",
            relief=tk.FLAT,
            borderwidth=0,
            padx=6,
            pady=5
        )
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Main content frame
        content_frame = tk.Frame(inner_frame, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top row: Icon and address
        top_row = tk.Frame(content_frame, bg="white")
        top_row.pack(fill=tk.X, pady=(0, 3))
        
        # Scooter icon (more refined, compact)
        icon_canvas = tk.Canvas(
            top_row,
            width=26,
            height=26,
            bg="white",
            highlightthickness=0
        )
        icon_canvas.pack(side=tk.LEFT, padx=(0, 6))
        
        # Draw better scooter icon
        # Wheels
        icon_canvas.create_oval(3, 11, 13, 21, fill=scooter_color, outline=scooter_color, width=1)
        icon_canvas.create_oval(13, 11, 23, 21, fill=scooter_color, outline=scooter_color, width=1)
        # Package box
        icon_canvas.create_rectangle(9, 5, 17, 13, fill=scooter_color, outline=scooter_color, width=1)
        # Handlebar
        icon_canvas.create_line(17, 9, 21, 7, fill=scooter_color, width=2)
        
        # Address (2 lines, compact)
        address_frame = tk.Frame(top_row, bg="white")
        address_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Split address if it contains comma
        address_parts = klant_adres.split(',')
        if len(address_parts) >= 2:
            line1 = address_parts[0].strip()
            line2 = address_parts[1].strip()
        else:
            # Try to split by length (shorter for compact cards)
            if len(klant_adres) > 28:
                mid = len(klant_adres) // 2
                space_idx = klant_adres.rfind(' ', 0, mid)
                if space_idx > 0:
                    line1 = klant_adres[:space_idx]
                    line2 = klant_adres[space_idx+1:]
                else:
                    line1 = klant_adres[:28]
                    line2 = klant_adres[28:] if len(klant_adres) > 28 else ""
            else:
                line1 = klant_adres
                line2 = ""
        
        address_label1 = tk.Label(
            address_frame,
            text=line1,
            font=("Arial", 8, "bold"),
            bg="white",
            fg="#222",
            anchor="w"
        )
        address_label1.pack(anchor=tk.W)
        
        if line2:
            address_label2 = tk.Label(
                address_frame,
                text=line2,
                font=("Arial", 7),
                bg="white",
                fg="#666",
                anchor="w"
            )
            address_label2.pack(anchor=tk.W)
        
        # Status bar (compact, professional)
        status_bar = tk.Frame(content_frame, bg=status_bg, height=22)
        status_bar.pack(fill=tk.X, pady=(3, 0))
        status_bar.pack_propagate(False)
        
        status_bar_content = tk.Frame(status_bar, bg=status_bg)
        status_bar_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Status text
        status_label = tk.Label(
            status_bar_content,
            text=status_text,
            font=("Arial", 8, "bold"),
            bg=status_bg,
            fg="white"
        )
        status_label.pack(side=tk.LEFT)
        
        # Times (compact)
        times_text = f"{tijd} {levertijd}" if levertijd != 'N/A' else tijd
        times_label = tk.Label(
            status_bar_content,
            text=times_text,
            font=("Arial", 7),
            bg=status_bg,
            fg="white"
        )
        times_label.pack(side=tk.LEFT, padx=(8, 0))
        
        # Payment indicator (small badge)
        if betaalmethode == "online":
            payment_badge = tk.Label(
                status_bar_content,
                text="ONLINE",
                font=("Arial", 6, "bold"),
                bg="#4CAF50",
                fg="white",
                padx=3,
                pady=0
            )
            payment_badge.pack(side=tk.LEFT, padx=(6, 0))
        
        # Price (right aligned) - format: € 28,00
        price_str = f"{totaal:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        price_text = f"€ {price_str}"
        price_label = tk.Label(
            status_bar_content,
            text=price_text,
            font=("Arial", 8, "bold"),
            bg=status_bg,
            fg="white"
        )
        price_label.pack(side=tk.RIGHT)
        
        # Make entire card clickable with hover effects
        def on_card_click(event, order_data=order):
            """Handle card click."""
            self.show_order_details_in_panel(order_data)
        
        def on_card_enter(event):
            """Hover effect - highlight card."""
            card_frame.config(bg="#E8E8E8")
            inner_frame.config(bg="#F5F5F5")
            card_frame.config(cursor="hand2")
        
        def on_card_leave(event):
            """Remove hover effect."""
            card_frame.config(bg="#F8F8F8")
            inner_frame.config(bg="white")
            card_frame.config(cursor="")
        
        # Bind events to card frame
        card_frame.bind("<Button-1>", on_card_click)
        card_frame.bind("<Enter>", on_card_enter)
        card_frame.bind("<Leave>", on_card_leave)
        
        # Bind click to all child widgets recursively
        def bind_click_to_children(widget, order_data=order):
            """Recursively bind click event to all child widgets."""
            widget.bind("<Button-1>", lambda e, o=order_data: self.show_order_details_in_panel(o))
            widget.bind("<Enter>", lambda e: on_card_enter(None))
            widget.bind("<Leave>", lambda e: on_card_leave(None))
            for child in widget.winfo_children():
                bind_click_to_children(child, order_data)
        
        # Bind to all children
        bind_click_to_children(card_frame, order)
        bind_click_to_children(inner_frame, order)
        
        # Store reference for hover effects
        self.current_selected_order = None
    
    def show_order_details_in_panel(self, order: Dict[str, Any]) -> None:
        """Show order details in the right panel when card is clicked (matching example layout)."""
        # Clear right panel
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        # Main container with beige background
        main_container = tk.Frame(self.right_panel, bg="#F5F5DC")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable canvas for the content
        details_canvas = tk.Canvas(main_container, bg="#F5F5DC", highlightthickness=0)
        details_scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=details_canvas.yview)
        details_frame = tk.Frame(details_canvas, bg="#F5F5DC")
        
        details_canvas_window = details_canvas.create_window((0, 0), window=details_frame, anchor="nw")
        details_canvas.configure(yscrollcommand=details_scrollbar.set)
        
        details_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def _on_canvas_configure(event):
            canvas_width = event.width
            details_canvas.itemconfig(details_canvas_window, width=canvas_width)
        
        def _on_frame_configure(event):
            details_canvas.configure(scrollregion=details_canvas.bbox("all"))
        
        details_canvas.bind('<Configure>', _on_canvas_configure)
        details_frame.bind('<Configure>', _on_frame_configure)
        
        # Header section
        header_section = tk.Frame(details_frame, bg="#F5F5DC", padx=20, pady=15)
        header_section.pack(fill=tk.X)
        
        # Logo and date row
        logo_date_frame = tk.Frame(header_section, bg="#F5F5DC")
        logo_date_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo (left)
        logo_frame = tk.Frame(logo_date_frame, bg="#F5F5DC")
        logo_frame.pack(side=tk.LEFT)
        
        try:
            from PIL import Image, ImageTk
            import os
            
            possible_paths = [
                "LOGO-MAGNEET.jpg",
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "LOGO-MAGNEET.jpg"),
                os.path.join(os.getcwd(), "LOGO-MAGNEET.jpg"),
            ]
            
            logo_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    logo_path = path
                    break
            
            if logo_path:
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((40, 40), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                
                logo_label = tk.Label(logo_frame, image=logo_photo, bg="#F5F5DC")
                logo_label.image = logo_photo
                logo_label.pack(side=tk.LEFT, padx=(0, 8))
            else:
                logo_text = tk.Label(logo_frame, text="🍕", font=("Arial", 20), bg="#F5F5DC")
                logo_text.pack(side=tk.LEFT, padx=(0, 8))
        except Exception as e:
            logger.warning(f"Could not load logo: {e}")
            logo_text = tk.Label(logo_frame, text="🍕", font=("Arial", 20), bg="#F5F5DC")
            logo_text.pack(side=tk.LEFT, padx=(0, 8))
        
        logo_name = tk.Label(
            logo_frame,
            text="Pita Pizza Napoli",
            font=("Arial", 14, "bold"),
            fg="#FF9800",
            bg="#F5F5DC"
        )
        logo_name.pack(side=tk.LEFT)
        
        # Date/time (right)
        now = datetime.datetime.now()
        date_label = tk.Label(
            logo_date_frame,
            text=f"Datum: {now.strftime('%d/%m/%Y %H:%M')}",
            font=("Arial", 11, "bold"),
            fg="#8B4513",
            bg="#F5F5DC"
        )
        date_label.pack(side=tk.RIGHT)
        
        # Instruction text
        instruction_text = "De knoppen onderaan zijn gekoppeld aan het systeem van de website. Deze gegevens zijn door de klant in te zien, zodat zij op de hoogte zijn van de status van hun bestelling."
        instruction_label = tk.Label(
            header_section,
            text=instruction_text,
            font=("Arial", 9),
            fg="#8B4513",
            bg="#F5F5DC",
            wraplength=600,
            justify=tk.LEFT
        )
        instruction_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Status buttons
        status_buttons_frame = tk.Frame(header_section, bg="#F5F5DC")
        status_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        status = order.get('status', 'Nieuw')
        
        # Nieuw button
        nieuw_btn = tk.Button(
            status_buttons_frame,
            text="🖨️ Nieuw",
            font=("Arial", 10, "bold"),
            bg="#F5F5DC" if status != "Nieuw" else "#E0E0E0",
            fg="#333",
            relief=tk.RAISED if status == "Nieuw" else tk.FLAT,
            borderwidth=2 if status == "Nieuw" else 1,
            padx=20,
            pady=8,
            command=lambda: self.update_order_status(order['id'], "Nieuw")
        )
        nieuw_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Keuken button
        keuken_btn = tk.Button(
            status_buttons_frame,
            text="🍳 Keuken",
            font=("Arial", 10, "bold"),
            bg="#F5F5DC" if status != "In de keuken" else "#E0E0E0",
            fg="#333",
            relief=tk.RAISED if status == "In de keuken" else tk.FLAT,
            borderwidth=2 if status == "In de keuken" else 1,
            padx=20,
            pady=8,
            command=lambda: self.update_order_status(order['id'], "In de keuken")
        )
        keuken_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Onderweg button
        onderweg_btn = tk.Button(
            status_buttons_frame,
            text="🚗 Onderweg",
            font=("Arial", 10, "bold"),
            bg="#4CAF50" if status == "Onderweg" else "#F5F5DC",
            fg="white" if status == "Onderweg" else "#333",
            relief=tk.RAISED,
            borderwidth=2,
            padx=20,
            pady=8,
            command=lambda: self.update_order_status(order['id'], "Onderweg")
        )
        onderweg_btn.pack(side=tk.LEFT)
        
        # Payment status bar (if online paid)
        betaalmethode = order.get('betaalmethode', 'cash')
        if betaalmethode == "online":
            payment_frame = tk.Frame(header_section, bg="#4CAF50", height=35)
            payment_frame.pack(fill=tk.X, pady=(0, 15))
            payment_frame.pack_propagate(False)
            
            payment_label = tk.Label(
                payment_frame,
                text="De klant heeft de bestelling online betaald!",
                font=("Arial", 11, "bold"),
                fg="white",
                bg="#4CAF50"
            )
            payment_label.pack(expand=True)
        
        # Main content area - two columns
        content_paned = tk.PanedWindow(details_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashpad=2, bg="#F5F5DC")
        content_paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Left panel - Order items
        left_panel = tk.Frame(content_paned, bg="white", padx=15, pady=15)
        content_paned.add(left_panel, minsize=300, width=400)
        
        # Right panel - Customer info and actions
        right_panel = tk.Frame(content_paned, bg="white", padx=15, pady=15)
        content_paned.add(right_panel, minsize=300, width=400)
        
        # LEFT PANEL - Order items (exact match to example)
        items_title = tk.Label(
            left_panel,
            text="Bestelling",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333"
        )
        items_title.pack(anchor=tk.W, pady=(0, 10))
        
        items_list_frame = tk.Frame(left_panel, bg="white")
        items_list_frame.pack(fill=tk.BOTH, expand=True)
        
        items = order.get('items', [])
        for item in items:
            item_frame = tk.Frame(items_list_frame, bg="white")
            item_frame.pack(fill=tk.X, pady=2)
            
            naam = item.get('product_naam', '')
            aantal = item.get('aantal', 1)
            prijs = item.get('prijs', 0)
            
            # Parse extras
            extras = item.get('extras')
            if extras:
                if isinstance(extras, str):
                    try:
                        extras = json.loads(extras)
                    except:
                        extras = {}
                else:
                    extras = extras or {}
            else:
                extras = {}
            
            # Determine size prefix (L, M, S, etc.) and format name
            size_prefix = ""
            naam_lower = naam.lower()
            display_naam = naam
            
            # Check if it's a pizza and determine size
            if "large" in naam_lower or "38cm" in naam_lower or (naam_lower.startswith("l ") and len(naam_lower) > 2):
                size_prefix = "L "
                # Remove "L " prefix if it exists in the name
                if naam_lower.startswith("l "):
                    display_naam = naam[2:].strip()
            elif "medium" in naam_lower or "30cm" in naam_lower or (naam_lower.startswith("m ") and len(naam_lower) > 2):
                size_prefix = "M "
                if naam_lower.startswith("m "):
                    display_naam = naam[2:].strip()
            elif "small" in naam_lower or (naam_lower.startswith("s ") and len(naam_lower) > 2):
                size_prefix = "S "
                if naam_lower.startswith("s "):
                    display_naam = naam[2:].strip()
            
            # Check for half-half
            half_half_value = extras.get('half_half') or extras.get('half-half') or extras.get('half half') or extras.get('Half half')
            is_half_half = bool(half_half_value)
            
            # Clean up pizza name - remove number prefix if present (e.g., "22. Romantica" -> "Romantica")
            # Also handle special cases like "Romantica lams" -> "LAMS ROMANTICA"
            clean_naam = display_naam
            if '. ' in clean_naam:
                # Remove number prefix like "22. "
                parts = clean_naam.split('. ', 1)
                if len(parts) > 1:
                    clean_naam = parts[1]
            
            # Handle special case: "Romantica lams" -> "LAMS ROMANTICA"
            clean_naam_lower = clean_naam.lower()
            if "romantica" in clean_naam_lower and "lams" in clean_naam_lower:
                # Reorder to "LAMS ROMANTICA"
                clean_naam = "LAMS ROMANTICA"
            else:
                # Convert to uppercase for display
                clean_naam = clean_naam.upper()
            
            clean_naam_upper = clean_naam
            
            # Format item line - match example exactly: "1x L LAMS ROMANTICA 38CM € 24,00"
            if is_half_half:
                # For half-half, show "1x L HALF HALF 38CM"
                item_text = f"{aantal}x {size_prefix}HALF HALF"
                # Add size suffix if available
                if "38cm" in naam_lower or "large" in naam_lower or size_prefix == "L ":
                    item_text += " 38CM"
                elif "30cm" in naam_lower or "medium" in naam_lower or size_prefix == "M ":
                    item_text += " 30CM"
            else:
                item_text = f"{aantal}x {size_prefix}{clean_naam_upper}"
                # Add size suffix if not already in name
                if "38cm" not in naam_lower and "30cm" not in naam_lower:
                    if size_prefix == "L ":
                        item_text += " 38CM"
                    elif size_prefix == "M ":
                        item_text += " 30CM"
            
            # Format price: € 24,00
            price_str = f"{prijs:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            item_text += f" € {price_str}"
            
            item_label = tk.Label(
                item_frame,
                text=item_text,
                font=("Arial", 10),
                bg="white",
                fg="#333",
                anchor="w"
            )
            item_label.pack(anchor=tk.W)
            
            # Half-half display - show sub-items with ">"
            if half_half_value:
                half_frame = tk.Frame(item_frame, bg="white")
                half_frame.pack(anchor=tk.W, padx=(0, 0))
                
                # Get pizza names from menu if we have menu_data
                half_names = []
                if isinstance(half_half_value, list):
                    half_names = half_half_value[:2]
                elif isinstance(half_half_value, dict):
                    # Try to get values from dict
                    values = [v for v in half_half_value.values() if v and v != True]
                    if len(values) >= 2:
                        half_names = values[:2]
                    else:
                        # Try keys
                        keys = [k for k in half_half_value.keys() if k != 'halve_pizza_keuze_lijst']
                        if len(keys) >= 2:
                            half_names = keys[:2]
                
                # If we have menu_data, try to convert pizza numbers to names
                if hasattr(self, 'menu_data') and self.menu_data and half_names:
                    try:
                        # Try to find pizza names in menu
                        pizza_categories = ['large pizza\'s', 'medium pizza\'s', 'small pizza\'s']
                        for cat in pizza_categories:
                            if cat in self.menu_data:
                                pizzas = self.menu_data[cat]
                                for i, half_val in enumerate(half_names):
                                    # Try to match by number or name
                                    if isinstance(half_val, (int, str)) and str(half_val).isdigit():
                                        pizza_num = int(half_val)
                                        if 0 < pizza_num <= len(pizzas):
                                            half_names[i] = pizzas[pizza_num - 1].get('naam', str(half_val))
                    except Exception as e:
                        logger.warning(f"Could not convert pizza numbers to names: {e}")
                
                if half_names and len(half_names) >= 2:
                    # First show "HALF HALF" label if it's a medium pizza (like in example)
                    if size_prefix == "M " or "30cm" in naam_lower or "medium" in naam_lower:
                        tk.Label(
                            half_frame,
                            text="HALF HALF 30CM",
                            font=("Arial", 9, "bold"),
                            bg="white",
                            fg="#666",
                            anchor="w"
                        ).pack(anchor=tk.W)
                    
                    for half in half_names:
                        # Format as "> POLLO HAWAÏ" (uppercase)
                        # Clean up name - remove number prefix if present
                        half_str = str(half)
                        if '. ' in half_str:
                            parts = half_str.split('. ', 1)
                            if len(parts) > 1:
                                half_str = parts[1]
                        half_display = half_str.upper()
                        tk.Label(
                            half_frame,
                            text=f"> {half_display}",
                            font=("Arial", 9),
                            bg="white",
                            fg="#666",
                            anchor="w"
                        ).pack(anchor=tk.W)
            
            # Other extras - show with "+" prefix
            for key, value in extras.items():
                if key in ['half_half', 'half-half', 'half half', 'Half half', 'opmerking'] or not value:
                    continue
                
                extra_text = ""
                if isinstance(value, list):
                    if value:
                        extra_text = f"+ {', '.join(map(str, value))}"
                else:
                    extra_text = f"+ {value}"
                
                if extra_text:
                    tk.Label(
                        item_frame,
                        text=extra_text,
                        font=("Arial", 9),
                        bg="white",
                        fg="#666",
                        anchor="w"
                    ).pack(anchor=tk.W)
        
        # Opmerkingen (comments) as separate item if exists - format: "1x Opmerkingen € 20,00"
        order_opmerking = order.get('opmerking')
        if order_opmerking:
            opmerking_frame = tk.Frame(items_list_frame, bg="white")
            opmerking_frame.pack(fill=tk.X, pady=2)
            
            # Note: In example, opmerkingen has a price, but we'll show it without price
            # unless there's a specific charge for it
            tk.Label(
                opmerking_frame,
                text="1x Opmerkingen",
                font=("Arial", 10),
                bg="white",
                fg="#333",
                anchor="w"
            ).pack(anchor=tk.W)
            
            # Opmerking text (indented for clarity)
            tk.Label(
                opmerking_frame,
                text=order_opmerking,
                font=("Arial", 9),
                bg="white",
                fg="#666",
                anchor="w",
                wraplength=350,
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=(15, 0))
        
        # RIGHT PANEL - Customer info and actions
        # Action buttons at top (matching example - flat buttons)
        actions_frame = tk.Frame(right_panel, bg="white")
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        print_btn = tk.Button(
            actions_frame,
            text="Bestelling afdrukken",
            command=lambda: self.print_order(order),
            bg="#FF9800",  # Orange like example
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            relief=tk.FLAT,
            borderwidth=0
        )
        print_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        route_btn = tk.Button(
            actions_frame,
            text="Routebeschrijving",
            command=lambda: self.show_route(order),
            bg="#2196F3",  # Blue
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            relief=tk.FLAT,
            borderwidth=0
        )
        route_btn.pack(side=tk.LEFT)
        
        # Klantgegevens section (matching example exactly)
        klant_frame = tk.LabelFrame(
            right_panel,
            text="Klantgegevens",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#333",
            padx=10,
            pady=10,
            relief=tk.FLAT,
            borderwidth=0
        )
        klant_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Get customer details - prefer separate fields if available
        klant_naam = order.get('klant_naam', 'Onbekend')
        klant_telefoon = order.get('klant_telefoon', 'Geen telefoon')
        
        # Try to get separate address fields first (from API)
        straat = order.get('klant_straat', '')
        huisnummer = order.get('klant_huisnummer', '')
        postcode = order.get('klant_postcode', '')
        gemeente = order.get('klant_gemeente', '')
        
        # If separate fields not available, parse from klant_adres
        if not straat or not huisnummer:
            klant_adres = order.get('klant_adres', 'Geen adres')
            if klant_adres and klant_adres != 'Geen adres':
                # Split by comma first
                parts = klant_adres.split(',')
                if len(parts) >= 1:
                    # First part: "Straat Huisnummer"
                    address_part = parts[0].strip()
                    # Try to separate street and house number
                    address_words = address_part.split()
                    if len(address_words) > 1:
                        # Last word is likely house number
                        huisnummer = address_words[-1] if not huisnummer else huisnummer
                        straat = ' '.join(address_words[:-1]) if not straat else straat
                    else:
                        straat = address_part if not straat else straat
                
                if len(parts) >= 2 and (not postcode or not gemeente):
                    # Second part: "Postcode Gemeente" or just "Gemeente"
                    postcode_gemeente = parts[1].strip()
                    # Try to extract postcode (usually 4 digits at start)
                    import re
                    postcode_match = re.match(r'^(\d{4})\s+(.+)$', postcode_gemeente)
                    if postcode_match:
                        postcode = postcode_match.group(1) if not postcode else postcode
                        gemeente = postcode_match.group(2) if not gemeente else gemeente
                    else:
                        # No postcode, just gemeente
                        gemeente = postcode_gemeente if not gemeente else gemeente
        
        # Display customer details (matching example format)
        # Each field on its own line with clear label
        details = [
            ("Naam", klant_naam if klant_naam and klant_naam != 'Onbekend' else "Geen naam"),
            ("Straat", straat if straat else "Geen straat"),
            ("Huisnummer", huisnummer if huisnummer else "Geen huisnummer"),
            ("Postcode", postcode if postcode else "Geen postcode"),
            ("Gemeente", gemeente if gemeente else "Geen gemeente"),
            ("Telefoonnummer", klant_telefoon if klant_telefoon and klant_telefoon != 'Geen telefoon' else "Geen telefoon")
        ]
        
        for label, value in details:
            detail_frame = tk.Frame(klant_frame, bg="white")
            detail_frame.pack(fill=tk.X, pady=2)
            
            label_widget = tk.Label(
                detail_frame,
                text=f"{label}:",
                font=("Arial", 10, "bold"),
                bg="white",
                fg="#333",
                anchor="w",
                width=12
            )
            label_widget.pack(side=tk.LEFT)
            
            value_widget = tk.Label(
                detail_frame,
                text=value,
                font=("Arial", 10),
                bg="white",
                fg="#333",
                anchor="w"
            )
            value_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Opmerkingen section (matching example)
        opmerkingen_frame = tk.LabelFrame(
            right_panel,
            text="Opmerkingen",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#333",
            padx=10,
            pady=10,
            relief=tk.FLAT,
            borderwidth=0
        )
        opmerkingen_frame.pack(fill=tk.BOTH, expand=True)
        
        if order_opmerking:
            opmerking_label = tk.Label(
                opmerkingen_frame,
                text=order_opmerking,
                font=("Arial", 10),
                bg="white",
                fg="#333",
                anchor="w",
                justify=tk.LEFT,
                wraplength=350
            )
            opmerking_label.pack(anchor=tk.W, fill=tk.X)
        else:
            opmerking_label = tk.Label(
                opmerkingen_frame,
                text="Geen opmerkingen beschikbaar",
                font=("Arial", 10),
                bg="white",
                fg="#999",
                anchor="w"
            )
            opmerking_label.pack(anchor=tk.W)
        
        # Footer buttons (matching example - flat buttons)
        footer_frame = tk.Frame(details_frame, bg="#F5F5DC")
        footer_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        totaal = order.get('totaal', 0)
        totaal_str = f"{totaal:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        # Total button (green, left side)
        total_btn = tk.Button(
            footer_frame,
            text=f"Totaal: € {totaal_str}",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",  # Green
            fg="white",
            relief=tk.FLAT,
            borderwidth=0,
            padx=30,
            pady=12
        )
        total_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Delivery time button (red, right side)
        levertijd = order.get('levertijd', 'N/A')
        levertijd_btn = tk.Button(
            footer_frame,
            text=f"Bezorgtijd: {levertijd}",
            font=("Arial", 12, "bold"),
            bg="#D32F2F",  # Red
            fg="white",
            relief=tk.FLAT,
            borderwidth=0,
            padx=30,
            pady=12
        )
        levertijd_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
    
    def confirm_order(self, order_id: int) -> None:
        """Mark order as confirmed (stop sound)."""
        self.confirmed_orders.add(order_id)
        logger.info(f"Order {order_id} confirmed")
    
    def show_levertijd_dialog(self, order: Dict[str, Any]) -> None:
        """Show dialog to select delivery time for new order (MyMenu style)."""
        order_id = order.get('id')
        bonnummer = order.get('bonnummer', 'N/A')
        klant_naam = order.get('klant_naam', 'Onbekend')
        klant_adres = order.get('klant_adres', 'Geen adres')
        totaal = order.get('totaal', 0)
        betaalmethode = order.get('betaalmethode', 'cash')
        items = order.get('items', [])
        
        # Create dialog window
        dialog = Toplevel(self.parent)
        dialog.title("Nieuwe bestelling")
        dialog.geometry("550x450")
        dialog.transient(self.parent)
        dialog.grab_set()  # Make dialog modal
        dialog.configure(bg="#F5F5DC")  # Beige background
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (450 // 2)
        dialog.geometry(f"550x450+{x}+{y}")
        
        # Main container
        main_frame = tk.Frame(dialog, bg="#F5F5DC", padx=25, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header frame
        header_frame = tk.Frame(main_frame, bg="#F5F5DC")
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Logo (left) - Napoli logo
        logo_frame = tk.Frame(header_frame, bg="#F5F5DC")
        logo_frame.pack(side=tk.LEFT)
        
        # Try to load Napoli logo
        try:
            from PIL import Image, ImageTk
            import os
            
            # Try multiple possible paths for the logo
            possible_paths = [
                "LOGO-MAGNEET.jpg",
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "LOGO-MAGNEET.jpg"),
                os.path.join(os.getcwd(), "LOGO-MAGNEET.jpg"),
            ]
            
            logo_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    logo_path = path
                    break
            
            if logo_path:
                logo_img = Image.open(logo_path)
                # Resize to appropriate size
                logo_img = logo_img.resize((40, 40), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                
                logo_label = tk.Label(
                    logo_frame,
                    image=logo_photo,
                    bg="#F5F5DC"
                )
                logo_label.image = logo_photo  # Keep a reference
                logo_label.pack(side=tk.LEFT, padx=(0, 8))
            else:
                # Fallback: text logo
                logo_text = tk.Label(
                    logo_frame,
                    text="🍕",
                    font=("Arial", 20),
                    bg="#F5F5DC"
                )
                logo_text.pack(side=tk.LEFT, padx=(0, 8))
        except Exception as e:
            logger.warning(f"Could not load logo: {e}")
            # Fallback: text logo
            logo_text = tk.Label(
                logo_frame,
                text="🍕",
                font=("Arial", 20),
                bg="#F5F5DC"
            )
            logo_text.pack(side=tk.LEFT, padx=(0, 8))
        
        logo_text_label = tk.Label(
            logo_frame,
            text="Pita Pizza Napoli",
            font=("Arial", 14, "bold"),
            fg="#FF9800",
            bg="#F5F5DC"
        )
        logo_text_label.pack(side=tk.LEFT)
        
        # Date/time (right)
        now = datetime.datetime.now()
        date_label = tk.Label(
            header_frame,
            text=f"Datum: {now.strftime('%d/%m/%Y %H:%M')}",
            font=("Arial", 11, "bold"),
            fg="#8B4513",  # Brown-red color
            bg="#F5F5DC"
        )
        date_label.pack(side=tk.RIGHT)
        
        # Instruction text
        instruction_text = "U heeft zojuist een nieuwe bestelling ontvangen via pitapizzanapoli.be! Maak een keuze hoelang de verwachte bezorgtijd in minuten is."
        instruction_label = tk.Label(
            main_frame,
            text=instruction_text,
            font=("Arial", 10),
            fg="#333",
            bg="#F5F5DC",
            wraplength=500,
            justify=tk.LEFT
        )
        instruction_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Payment status bar (if online paid)
        if betaalmethode == "online":
            payment_frame = tk.Frame(main_frame, bg="#4CAF50", height=35)
            payment_frame.pack(fill=tk.X, pady=(0, 15))
            payment_frame.pack_propagate(False)
            
            payment_label = tk.Label(
                payment_frame,
                text="De klant heeft de bestelling online betaald!",
                font=("Arial", 11, "bold"),
                fg="white",
                bg="#4CAF50"
            )
            payment_label.pack(expand=True)
        
        # Order details
        details_frame = tk.Frame(main_frame, bg="#F5F5DC")
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Address and total (green)
        address_text = f"{klant_adres} - € {totaal:.2f}"
        address_label = tk.Label(
            details_frame,
            text=address_text,
            font=("Arial", 11, "bold"),
            fg="#2E7D32",  # Dark green
            bg="#F5F5DC"
        )
        address_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Items list
        items_text = ", ".join([f"{item.get('aantal', 1)}x {item.get('product_naam', '')}" for item in items])
        if len(items_text) > 60:
            items_text = items_text[:57] + "..."
        
        items_label = tk.Label(
            details_frame,
            text=items_text,
            font=("Arial", 9),
            fg="#666",
            bg="#F5F5DC",
            wraplength=500,
            justify=tk.LEFT
        )
        items_label.pack(anchor=tk.W)
        
        # Delivery time selection
        time_prompt = tk.Label(
            main_frame,
            text="Kies de verwachte levertijd in minuten",
            font=("Arial", 11, "bold"),
            fg="#8B4513",  # Brown-red
            bg="#F5F5DC"
        )
        time_prompt.pack(pady=(15, 10))
        
        # Time selection buttons frame
        time_frame = tk.Frame(main_frame, bg="#F5F5DC")
        time_frame.pack(pady=10)
        
        selected_minutes = [30]  # Default to 30 minutes
        
        def update_time_display():
            """Update the time display."""
            for widget in time_frame.winfo_children():
                widget.destroy()
            
            # Left arrow
            left_btn = tk.Button(
                time_frame,
                text="<",
                font=("Arial", 14, "bold"),
                fg="#D32F2F",
                bg="white",
                relief=tk.RAISED,
                borderwidth=2,
                width=3,
                height=2,
                command=lambda: (selected_minutes.__setitem__(0, max(15, selected_minutes[0] - 15)), update_time_display())
            )
            left_btn.pack(side=tk.LEFT, padx=5)
            
            # Time options
            time_options = [15, 30, 45, 60, 75]
            current_index = time_options.index(selected_minutes[0]) if selected_minutes[0] in time_options else 1
            
            # Show current and adjacent options
            start_idx = max(0, current_index - 1)
            end_idx = min(len(time_options), current_index + 3)
            visible_options = time_options[start_idx:end_idx]
            
            for minutes in visible_options:
                is_selected = minutes == selected_minutes[0]
                btn = tk.Button(
                    time_frame,
                    text=str(minutes),
                    font=("Arial", 16, "bold"),
                    fg="#D32F2F" if is_selected else "#666",
                    bg="white",
                    relief=tk.RAISED if is_selected else tk.FLAT,
                    borderwidth=3 if is_selected else 1,
                    width=4,
                    height=2,
                    command=lambda m=minutes: (selected_minutes.__setitem__(0, m), update_time_display())
                )
                btn.pack(side=tk.LEFT, padx=3)
            
            # Right arrow
            right_btn = tk.Button(
                time_frame,
                text=">",
                font=("Arial", 14, "bold"),
                fg="#D32F2F",
                bg="white",
                relief=tk.RAISED,
                borderwidth=2,
                width=3,
                height=2,
                command=lambda: (selected_minutes.__setitem__(0, min(75, selected_minutes[0] + 15)), update_time_display())
            )
            right_btn.pack(side=tk.LEFT, padx=5)
        
        update_time_display()
        
        # Confirm button
        def confirm_levertijd():
            """Confirm and save levertijd."""
            minutes = selected_minutes[0]
            now = datetime.datetime.now()
            delivery_time = now + datetime.timedelta(minutes=minutes)
            levertijd_str = delivery_time.strftime('%H:%M')
            
            # Update order via API
            try:
                response = self.api_session.put(
                    f"{API_BASE_URL}/orders/{order_id}/status",
                    json={
                        "new_status": order.get('status', 'Nieuw'),
                        "levertijd": levertijd_str
                    }
                )
                
                if response.status_code == 200:
                    self.orders_with_levertijd.add(order_id)
                    messagebox.showinfo("Succes", f"Levertijd ingesteld op {levertijd_str} ({minutes} minuten)")
                    dialog.destroy()
                    self.refresh_orders()
                elif response.status_code == 401:
                    # Token expired, try to re-authenticate
                    logger.warning("Token expired during levertijd update, re-authenticating...")
                    if self.authenticate_api():
                        # Retry the request
                        response = self.api_session.put(
                            f"{API_BASE_URL}/orders/{order_id}/status",
                            json={
                                "new_status": order.get('status', 'Nieuw'),
                                "levertijd": levertijd_str
                            }
                        )
                        if response.status_code == 200:
                            self.orders_with_levertijd.add(order_id)
                            messagebox.showinfo("Succes", f"Levertijd ingesteld op {levertijd_str} ({minutes} minuten)")
                            dialog.destroy()
                            self.refresh_orders()
                        else:
                            error_text = response.text if hasattr(response, 'text') else ""
                            logger.error(f"Failed to set levertijd after re-auth: {response.status_code} - {error_text}")
                            messagebox.showerror("Fout", f"Kon levertijd niet instellen na her-authenticatie: {response.status_code}")
                    else:
                        messagebox.showerror("Fout", "Kon niet opnieuw authenticeren met API")
                else:
                    error_text = response.text if hasattr(response, 'text') else ""
                    logger.error(f"Failed to set levertijd: {response.status_code} - {error_text}")
                    try:
                        error_json = response.json()
                        error_detail = error_json.get('detail', error_text)
                    except:
                        error_detail = error_text or str(response.status_code)
                    messagebox.showerror("Fout", f"Kon levertijd niet instellen: {error_detail}")
            except requests.exceptions.ConnectionError as e:
                logger.debug(f"Connection error setting levertijd: {e}")
                messagebox.showerror("Fout", "Kan geen verbinding maken met backend. Is de server gestart?")
            except Exception as e:
                logger.exception(f"Error setting levertijd: {e}")
                messagebox.showerror("Fout", f"Fout bij instellen levertijd: {e}")
        
        confirm_btn = tk.Button(
            main_frame,
            text="BEVESTIGEN",
            command=confirm_levertijd,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=12,
            relief=tk.RAISED,
            borderwidth=2
        )
        confirm_btn.pack(pady=(20, 0))
    
    def update_order_status(self, order_id: int, new_status: str, levertijd: Optional[str] = None) -> None:
        """Update order status."""
        try:
            payload = {"new_status": new_status}
            if levertijd:
                payload["levertijd"] = levertijd
            
            response = self.api_session.put(
                f"{API_BASE_URL}/orders/{order_id}/status",
                json=payload
            )
            
            if response.status_code == 200:
                messagebox.showinfo("Succes", f"Status bijgewerkt naar: {new_status}")
                self.refresh_orders()
            elif response.status_code == 401:
                # Token expired, try to re-authenticate
                logger.warning("Token expired, re-authenticating...")
                if self.authenticate_api():
                    # Retry the request
                    response = self.api_session.put(
                        f"{API_BASE_URL}/orders/{order_id}/status",
                        json=payload
                    )
                    if response.status_code == 200:
                        messagebox.showinfo("Succes", f"Status bijgewerkt naar: {new_status}")
                        self.refresh_orders()
                    else:
                        error_text = response.text if hasattr(response, 'text') else ""
                        try:
                            error_json = response.json()
                            error_detail = error_json.get('detail', error_text)
                        except:
                            error_detail = error_text or str(response.status_code)
                        logger.error(f"Failed to update status after re-auth: {response.status_code} - {error_detail}")
                        messagebox.showerror("Fout", f"Kon status niet bijwerken: {error_detail}")
                else:
                    messagebox.showerror("Fout", "Kon niet opnieuw authenticeren met API")
            else:
                error_text = response.text if hasattr(response, 'text') else ""
                try:
                    error_json = response.json()
                    error_detail = error_json.get('detail', error_text)
                except:
                    error_detail = error_text or str(response.status_code)
                logger.error(f"Failed to update status: {response.status_code} - {error_detail}")
                messagebox.showerror("Fout", f"Kon status niet bijwerken: {error_detail}")
        except requests.exceptions.ConnectionError as e:
            logger.debug(f"Connection error: {e}")
            messagebox.showerror("Fout", "Kan geen verbinding maken met backend. Is de server gestart?")
        except Exception as e:
            logger.exception(f"Error updating order status: {e}")
            messagebox.showerror("Fout", f"Fout bij bijwerken status: {e}")
    
    def show_order_details(self, order: Dict[str, Any]) -> None:
        """Show order details in a new window."""
        details_window = Toplevel(self.parent)
        details_window.title(f"Bestelling Details - {order.get('bonnummer', 'N/A')}")
        details_window.geometry("600x700")
        
        # Create scrolled text for order details
        text_widget = scrolledtext.ScrolledText(
            details_window,
            wrap=tk.WORD,
            font=("Courier", 10),
            width=70,
            height=35
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Generate order details text (similar to bon format)
        details_text = self.generate_order_details_text(order)
        text_widget.insert(tk.END, details_text)
        text_widget.config(state=tk.DISABLED)
        
        # Buttons frame
        buttons_frame = tk.Frame(details_window)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        print_btn = tk.Button(
            buttons_frame,
            text="🖨️ Afdrukken",
            command=lambda: self.print_order(order),
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        print_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = tk.Button(
            buttons_frame,
            text="Sluiten",
            command=details_window.destroy,
            bg="#9E9E9E",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        close_btn.pack(side=tk.LEFT)
    
    def generate_order_details_text(self, order: Dict[str, Any]) -> str:
        """Generate order details text (similar to bon format)."""
        # This will use the existing bon_generator logic
        # For now, create a simple text representation
        lines = []
        lines.append("=" * 50)
        lines.append("BESTELLING DETAILS")
        lines.append("=" * 50)
        lines.append("")
        lines.append(f"Bonnummer: {order.get('bonnummer', 'N/A')}")
        lines.append(f"Status: {order.get('status', 'N/A')}")
        lines.append(f"Datum: {order.get('datum', 'N/A')}")
        lines.append(f"Tijd: {order.get('tijd', 'N/A')}")
        lines.append(f"Levertijd: {order.get('levertijd', 'N/A')}")
        lines.append("")
        lines.append("KLANTGEGEVENS:")
        lines.append("-" * 50)
        lines.append(f"Naam: {order.get('klant_naam', 'N/A')}")
        lines.append(f"Adres: {order.get('klant_adres', 'N/A')}")
        lines.append(f"Telefoon: {order.get('klant_telefoon', 'N/A')}")
        lines.append("")
        lines.append("BESTELLING:")
        lines.append("-" * 50)
        
        items = order.get('items', [])
        for item in items:
            naam = item.get('product_naam', 'N/A')
            aantal = item.get('aantal', 1)
            prijs = item.get('prijs', 0)
            totaal_item = aantal * prijs
            
            lines.append(f"{naam} x{aantal} = €{totaal_item:.2f}")
            
            # Show extras if available
            extras = item.get('extras')
            if extras:
                if isinstance(extras, str):
                    try:
                        extras = json.loads(extras)
                    except:
                        pass
                if isinstance(extras, dict):
                    for key, value in extras.items():
                        if value and key != 'opmerking':
                            lines.append(f"  - {key}: {value}")
            
            opmerking = item.get('opmerking')
            if opmerking:
                lines.append(f"  Opmerking: {opmerking}")
        
        lines.append("")
        lines.append("-" * 50)
        lines.append(f"TOTAAL: €{order.get('totaal', 0):.2f}")
        lines.append(f"Betaalmethode: {order.get('betaalmethode', 'cash').upper()}")
        lines.append("")
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def print_order(self, order: Dict[str, Any]) -> None:
        """Print order using existing bon printing system."""
        try:
            from bon_generator import generate_bon_text
            from utils.print_utils import _save_and_print_from_preview
            
            # Convert order to bon format
            klant_data = {
                "naam": order.get('klant_naam', 'Onbekend'),
                "telefoon": order.get('klant_telefoon', ''),
                "adres": order.get('klant_adres', '').split(',')[0] if order.get('klant_adres') else '',
                "huisnummer": "",
                "postcode": "",
                "gemeente": "",
                "levertijd": order.get('levertijd', ''),
                "afhaal": False,
                "korting_percentage": 0.0
            }
            
            # Parse address if available
            if order.get('klant_adres'):
                # Try to parse address (format: "Straat Huisnummer, Postcode Gemeente")
                parts = order.get('klant_adres', '').split(',')
                if len(parts) >= 2:
                    address_part = parts[0].strip()
                    # Try to split street and house number
                    address_words = address_part.split()
                    if address_words:
                        klant_data["adres"] = " ".join(address_words[:-1])
                        klant_data["huisnummer"] = address_words[-1]
                    
                    postcode_gemeente = parts[1].strip().split()
                    if len(postcode_gemeente) >= 2:
                        klant_data["postcode"] = postcode_gemeente[0]
                        klant_data["gemeente"] = " ".join(postcode_gemeente[1:])
            
            # Convert items to bon format
            bestelregels = []
            for item in order.get('items', []):
                bestelregel = {
                    "product": item.get('product_naam', ''),
                    "categorie": "",  # Not available in API response
                    "aantal": item.get('aantal', 1),
                    "prijs": float(item.get('prijs', 0)),
                    "extras": item.get('extras', {})
                }
                bestelregels.append(bestelregel)
            
            # Generate bon text
            bonnummer = order.get('bonnummer', 'N/A')
            bon_text = generate_bon_text(
                klant_data,
                bestelregels,
                bonnummer,
                menu_data_for_drinks=self.menu_data,
                extras_data=self.extras_data
            )
            
            # Print using existing print system
            def save_and_print():
                _save_and_print_from_preview(
                    bon_text,
                    None,  # address_for_qr
                    klant_data,
                    None,  # bestelling_opslaan_func (not needed for reprint)
                    self.app_settings
                )
            
            save_and_print()
            
        except Exception as e:
            logger.error(f"Error printing order: {e}")
            messagebox.showerror("Fout", f"Kon bon niet afdrukken: {e}")
    
    def show_route(self, order: Dict[str, Any]) -> None:
        """Show route to customer address using Google Maps."""
        klant_adres = order.get('klant_adres', '')
        if not klant_adres:
            messagebox.showwarning("Geen adres", "Geen adres beschikbaar voor deze bestelling")
            return
        
        # Restaurant address (from settings or hardcoded)
        restaurant_address = "Brugstraat 12, 9120 Vrasene, België"
        
        # Create Google Maps URL
        destination = klant_adres.replace(" ", "+")
        origin = restaurant_address.replace(" ", "+")
        
        maps_url = f"https://www.google.com/maps/dir/{origin}/{destination}"
        
        # Open in browser
        webbrowser.open(maps_url)
        
        # TODO: Calculate distance using Google Maps API
        # For now, just open the route in browser
    
    def check_auto_status_updates(self, orders: List[Dict[str, Any]]) -> None:
        """Check if any orders need automatic status updates."""
        now = datetime.datetime.now()
        
        for order in orders:
            order_id = order['id']
            current_status = order.get('status', 'Nieuw')
            
            # Only auto-update orders with status "Nieuw"
            if current_status == "Nieuw" and order_id in self.order_timestamps:
                order_time = self.order_timestamps[order_id]
                time_diff = (now - order_time).total_seconds()
                
                # If 5 minutes have passed, auto-update to "In de keuken"
                if time_diff >= self.auto_status_interval:
                    logger.info(f"Auto-updating order {order_id} to 'In de keuken' after {time_diff:.0f} seconds")
                    try:
                        response = self.api_session.put(
                            f"{API_BASE_URL}/orders/{order_id}/status",
                            json={"new_status": "In de keuken"}
                        )
                        if response.status_code == 200:
                            # Update timestamp to prevent repeated updates
                            self.order_timestamps[order_id] = now
                    except Exception as e:
                        logger.error(f"Error auto-updating order status: {e}")
    
    def toggle_auto_status(self) -> None:
        """Toggle automatic status updates."""
        self.auto_status_enabled = not self.auto_status_enabled
        status_text = "ingeschakeld" if self.auto_status_enabled else "uitgeschakeld"
        messagebox.showinfo("Auto Status", f"Automatische status updates zijn nu {status_text}")


def open_online_bestellingen(parent: tk.Widget, app_settings: Dict[str, Any], menu_data: Dict[str, Any], extras_data: Dict[str, Any]) -> None:
    """
    Open online bestellingen interface.
    
    Args:
        parent: Parent widget (tab frame)
        app_settings: Application settings dict
        menu_data: Menu data dict
        extras_data: Extras data dict
    """
    manager = OnlineBestellingenManager(parent, app_settings, menu_data, extras_data)
    return manager

