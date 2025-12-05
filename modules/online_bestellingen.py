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
        
        # API authentication - load credentials from settings
        admin_creds = app_settings.get('admin_credentials', {}).get('admin', {})
        self.api_username = admin_creds.get('username', 'admin')
        self.api_password = admin_creds.get('password', 'admin123')
        
        self.api_token = None
        self.api_session = requests.Session()
        self.last_auth_attempt = 0
        self.auth_backoff = 0  # Seconds to wait before retrying auth
        
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
        
        # Main content area - Full width orders list (no right panel)
        orders_list_frame = tk.Frame(main_frame, bg="white")
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
        
        # Store grid position for grid layout (5 columns, 10 rows = 50 orders per page)
        self.current_row = 0
        self.current_col = 0
        self.grid_columns = 5
        self.grid_rows = 10
        
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
        
        # Footer right - Total (right aligned)
        footer_right = tk.Frame(footer_content, bg="#2E7D32")
        footer_right.pack(side=tk.RIGHT)
        
        self.total_label = tk.Label(
            footer_right,
            text="Totaal: € 0,00",
            font=("Arial", 14, "bold"),
            bg="#2E7D32",
            fg="white"
        )
        self.total_label.pack()
    
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
                    "username": self.api_username,
                    "password": self.api_password
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
                import time
                current_time = time.time()
                # Only try to re-authenticate if enough time has passed (backoff)
                if current_time - self.last_auth_attempt >= self.auth_backoff:
                    logger.debug("Token expired, re-authenticating...")
                    self.last_auth_attempt = current_time
                    if self.authenticate_api():
                        # Reset backoff on success
                        self.auth_backoff = 0
                        # Retry the request
                        response = self.api_session.get(
                            f"{API_BASE_URL}/orders/online/pending",
                            timeout=2
                        )
                        if response.status_code == 200:
                            return response.json()
                    else:
                        # Increase backoff on failure (max 60 seconds)
                        self.auth_backoff = min(self.auth_backoff * 2 + 5, 60)
                        logger.warning(f"Re-authentication failed, backing off for {self.auth_backoff}s")
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
        
        # Reset grid position for grid layout
        self.current_row = 0
        self.current_col = 0
        
        # Recreate all cards to maintain order (simpler approach)
        # Clear all existing cards
        for widget in list(self.orders_frame.winfo_children()):
            widget.destroy()
        
        # Sort orders by status and time (Nieuw first, then In de keuken, then Onderweg)
        status_order = {"Nieuw": 0, "In de keuken": 1, "Onderweg": 2}
        sorted_orders = sorted(orders, key=lambda o: (status_order.get(o.get('status', 'Nieuw'), 99), o.get('tijd', '')))
        
        # Create all cards in grid layout (5 columns, 10 rows)
        for order in sorted_orders:
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
            empty_label.pack(pady=50)
        
        # Calculate and update total
        total = sum(order.get('totaal', 0) for order in new_orders_dict.values())
        if self.total_label:
            # Format: use dot for thousands, comma for decimals
            total_str = f"{total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            self.total_label.config(text=f"Totaal: € {total_str}")
    
    def create_order_card(self, order: Dict[str, Any]) -> None:
        """Create a compact bar widget for an order (matching example design)."""
        status = order.get('status', 'Nieuw')
        klant_adres = order.get('klant_adres', 'Geen adres')
        tijd = order.get('tijd', 'N/A')
        levertijd = order.get('levertijd', 'N/A')
        totaal = order.get('totaal', 0)
        
        # Determine colors based on status
        if status == "In de keuken" or status == "Keuken":
            status_bg = "#81C784"  # Green
            status_text = "Keuken"
            scooter_color = "green"
        elif status == "Nieuw":
            status_bg = "#64B5F6"  # Blue
            status_text = "Nieuw"
            scooter_color = "blue"
        else:  # Onderweg
            status_bg = "#9E9E9E"  # Grey
            status_text = "Onderweg"
            scooter_color = "grey"
        
        # Compact bar frame (grid layout - smaller to fit 5 per row)
        bar_frame = tk.Frame(
            self.orders_frame,
            bg=status_bg,
            relief=tk.FLAT,
            borderwidth=1,
            padx=5,
            pady=4
        )
        # Use grid layout: 5 columns, 10 rows
        bar_frame.grid(
            row=self.current_row,
            column=self.current_col,
            padx=2,
            pady=2,
            sticky="nsew"
        )
        
        # Configure grid weights for equal column distribution
        self.orders_frame.grid_columnconfigure(self.current_col, weight=1, uniform="orders")
        self.orders_frame.grid_rowconfigure(self.current_row, weight=0)
        
        # Store order_id in widget for tracking
        bar_frame.order_id = order.get('id')
        
        # Main content frame (horizontal layout)
        content_frame = tk.Frame(bar_frame, bg=status_bg)
        content_frame.pack(fill=tk.X)
        
        # Vertical layout for compact grid display
        # Top section - Icon and address
        top_section = tk.Frame(content_frame, bg=status_bg)
        top_section.pack(fill=tk.X, pady=(2, 0))
        
        # Scooter icon (smaller for grid)
        scooter_label = tk.Label(
            top_section,
            text="🛵",
            font=("Arial", 12),
            bg=status_bg,
            fg="white"
        )
        scooter_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Address (truncated if too long for grid)
        address_display = klant_adres
        if len(address_display) > 25:
            address_display = address_display[:22] + "..."
        
        address_label = tk.Label(
            top_section,
            text=address_display,
            font=("Arial", 8),
            bg=status_bg,
            fg="white",
            anchor="w"
        )
        address_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Middle section - Status and times
        middle_section = tk.Frame(content_frame, bg=status_bg)
        middle_section.pack(fill=tk.X, pady=(2, 0))
        
        # Status
        status_label = tk.Label(
            middle_section,
            text=status_text,
            font=("Arial", 8, "bold"),
            bg=status_bg,
            fg="white",
            anchor="w"
        )
        status_label.pack(side=tk.LEFT)
        
        # Times (format: "15:49 17:09")
        if ':' in tijd:
            tijd_parts = tijd.split(':')
            tijd_short = f"{tijd_parts[0]}:{tijd_parts[1]}"
        else:
            tijd_short = tijd
        
        if levertijd != 'N/A' and ':' in levertijd:
            levertijd_parts = levertijd.split(':')
            levertijd_short = f"{levertijd_parts[0]}:{levertijd_parts[1]}"
            times_text = f"{tijd_short} {levertijd_short}"
        else:
            times_text = tijd_short
        
        times_label = tk.Label(
            middle_section,
            text=times_text,
            font=("Arial", 7),
            bg=status_bg,
            fg="white"
        )
        times_label.pack(side=tk.RIGHT)
        
        # Bottom section - Price
        bottom_section = tk.Frame(content_frame, bg=status_bg)
        bottom_section.pack(fill=tk.X, pady=(2, 0))
        
        price_str = f"{totaal:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        price_text = f"€ {price_str}"
        price_label = tk.Label(
            bottom_section,
            text=price_text,
            font=("Arial", 10, "bold"),
            bg=status_bg,
            fg="white"
        )
        price_label.pack(anchor=tk.E)
        
        # Make entire bar clickable with hover effects
        def on_bar_click(event, order_data=order):
            """Handle bar click."""
            self.show_order_details_window(order_data)
        
        def on_bar_enter(event):
            """Hover effect - slightly darker."""
            darker_bg = status_bg
            # Make slightly darker
            if status_bg == "#81C784":  # Green
                darker_bg = "#66BB6A"
            elif status_bg == "#64B5F6":  # Blue
                darker_bg = "#42A5F5"
            elif status_bg == "#9E9E9E":  # Grey
                darker_bg = "#757575"
            
            bar_frame.config(bg=darker_bg)
            content_frame.config(bg=darker_bg)
            top_section.config(bg=darker_bg)
            middle_section.config(bg=darker_bg)
            bottom_section.config(bg=darker_bg)
            bar_frame.config(cursor="hand2")
            # Update all labels
            for widget in [scooter_label, address_label, status_label, times_label, price_label]:
                widget.config(bg=darker_bg)
        
        def on_bar_leave(event):
            """Remove hover effect."""
            bar_frame.config(bg=status_bg)
            content_frame.config(bg=status_bg)
            top_section.config(bg=status_bg)
            middle_section.config(bg=status_bg)
            bottom_section.config(bg=status_bg)
            bar_frame.config(cursor="")
            # Update all labels
            for widget in [scooter_label, address_label, status_label, times_label, price_label]:
                widget.config(bg=status_bg)
        
        # Bind events to bar frame
        bar_frame.bind("<Button-1>", on_bar_click)
        bar_frame.bind("<Enter>", on_bar_enter)
        bar_frame.bind("<Leave>", on_bar_leave)
        
        # Bind click to all child widgets recursively
        def bind_click_to_children(widget, order_data=order):
            """Recursively bind click event to all child widgets."""
            widget.bind("<Button-1>", lambda e, o=order_data: self.show_order_details_window(o))
            widget.bind("<Enter>", lambda e: on_bar_enter(None))
            widget.bind("<Leave>", lambda e: on_bar_leave(None))
            for child in widget.winfo_children():
                bind_click_to_children(child, order_data)
        
        # Bind to all children
        bind_click_to_children(bar_frame, order)
        bind_click_to_children(content_frame, order)
        bind_click_to_children(top_section, order)
        bind_click_to_children(middle_section, order)
        bind_click_to_children(bottom_section, order)
        
        # Update grid position (move to next column, wrap to next row after 5 columns)
        self.current_col += 1
        if self.current_col >= self.grid_columns:
            self.current_col = 0
            self.current_row += 1
    
    def show_order_details_window(self, order: Dict[str, Any]) -> None:
        """Show order details in a new window when order is clicked."""
        from tkinter import Toplevel
        
        # Create new window (smaller size)
        details_window = Toplevel(self.parent)
        details_window.title(f"Bestelling Details - {order.get('bonnummer', 'N/A')}")
        details_window.geometry("800x650")
        details_window.configure(bg="#F5F5DC")
        
        # Center the window
        details_window.update_idletasks()
        x = (details_window.winfo_screenwidth() // 2) - (800 // 2)
        y = (details_window.winfo_screenheight() // 2) - (650 // 2)
        details_window.geometry(f"800x650+{x}+{y}")
        
        # Main container with beige background
        main_container = tk.Frame(details_window, bg="#F5F5DC")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
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
        
        # Logo name - "Napoli" style (red text)
        logo_name = tk.Label(
            logo_frame,
            text="Napoli",
            font=("Arial", 16, "bold"),
            fg="#D32F2F",  # Red
            bg="#F5F5DC"
        )
        logo_name.pack(side=tk.LEFT)
        
        # Date/time (right) - red text
        now = datetime.datetime.now()
        date_label = tk.Label(
            logo_date_frame,
            text=f"Datum: {now.strftime('%d/%m/%Y %H:%M')}",
            font=("Arial", 11, "bold"),
            fg="#D32F2F",  # Red
            bg="#F5F5DC"
        )
        date_label.pack(side=tk.RIGHT)
        
        # Instruction text
        instruction_text = "De knoppen onderaan zijn gekoppeld aan het systeem van de website. Deze gegevens zijn door te klant in te zien, zodat zij op de hoogte zijn van de status van hun bestelling."
        instruction_label = tk.Label(
            header_section,
            text=instruction_text,
            font=("Arial", 9),
            fg="#8B4513",
            bg="#F5F5DC",
            wraplength=700,
            justify=tk.LEFT
        )
        instruction_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Status buttons section (beige buttons with icons)
        status_section = tk.Frame(header_section, bg="#F5F5DC")
        status_section.pack(fill=tk.X, pady=(0, 10))
        
        status = order.get('status', 'Nieuw')
        # Normalize status names
        if status == "In de keuken":
            status = "Keuken"
        
        # Status buttons frame (no label, just buttons)
        status_buttons_frame = tk.Frame(status_section, bg="#F5F5DC")
        status_buttons_frame.pack()
        
        # Nieuw button (beige with printer icon)
        nieuw_active = status == "Nieuw"
        nieuw_btn = tk.Button(
            status_buttons_frame,
            text="🖨️ Nieuw",
            font=("Arial", 11, "bold"),
            bg="#D2B48C" if nieuw_active else "#F5DEB3",  # Beige
            fg="#8B4513",
            relief=tk.RAISED if nieuw_active else tk.FLAT,
            borderwidth=2,
            padx=20,
            pady=10,
            command=lambda: self.update_order_status(order['id'], "Nieuw")
        )
        nieuw_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Keuken button (beige with pot icon)
        keuken_active = status == "Keuken" or status == "In de keuken"
        keuken_btn = tk.Button(
            status_buttons_frame,
            text="🍳 Keuken",
            font=("Arial", 11, "bold"),
            bg="#D2B48C" if keuken_active else "#F5DEB3",  # Beige
            fg="#8B4513",
            relief=tk.RAISED if keuken_active else tk.FLAT,
            borderwidth=2,
            padx=20,
            pady=10,
            command=lambda: self.update_order_status(order['id'], "In de keuken")
        )
        keuken_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Onderweg button (green with scooter icon when active)
        onderweg_active = status == "Onderweg"
        onderweg_btn = tk.Button(
            status_buttons_frame,
            text="🛵 Onderweg",
            font=("Arial", 11, "bold"),
            bg="#4CAF50" if onderweg_active else "#F5DEB3",  # Green when active, beige otherwise
            fg="white" if onderweg_active else "#8B4513",
            relief=tk.RAISED if onderweg_active else tk.FLAT,
            borderwidth=2,
            padx=20,
            pady=10,
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
        content_paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
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
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#000"
        )
        items_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Scrollable frame for items
        items_canvas = tk.Canvas(left_panel, bg="white", highlightthickness=0)
        items_scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=items_canvas.yview)
        items_list_frame = tk.Frame(items_canvas, bg="white")
        
        items_canvas_window = items_canvas.create_window((0, 0), window=items_list_frame, anchor="nw")
        items_canvas.configure(yscrollcommand=items_scrollbar.set)
        
        def _on_items_canvas_configure(event):
            canvas_width = event.width
            items_canvas.itemconfig(items_canvas_window, width=canvas_width)
        
        def _on_items_frame_configure(event):
            items_canvas.configure(scrollregion=items_canvas.bbox("all"))
        
        items_canvas.bind('<Configure>', _on_items_canvas_configure)
        items_list_frame.bind('<Configure>', _on_items_frame_configure)
        
        items_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        items_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        items = order.get('items', [])
        if not items:
            no_items_label = tk.Label(
                items_list_frame,
                text="Geen items in deze bestelling",
                font=("Arial", 11),
                bg="white",
                fg="#999"
            )
            no_items_label.pack(pady=20)
        else:
            for item in items:
                item_frame = tk.Frame(items_list_frame, bg="white", relief=tk.FLAT, borderwidth=1)
                item_frame.pack(fill=tk.X, pady=4, padx=5)
            
                naam = item.get('product_naam', '')
                aantal = item.get('aantal', 1)
                prijs = item.get('prijs', 0)
                
                # Find category from menu_data
                categorie = ""
                if hasattr(self, 'menu_data') and self.menu_data:
                    naam_lower = naam.lower()
                    
                    # Method 1: Use product_id if available (MOST RELIABLE - use this first and stop if found)
                    product_id = item.get('product_id')
                    if product_id:
                        # Search by product ID - this is the most reliable method
                        for cat_name, cat_items in self.menu_data.items():
                            if isinstance(cat_items, list):
                                for menu_item in cat_items:
                                    menu_item_id = menu_item.get('id')
                                    # Handle both integer and string comparisons
                                    if menu_item_id == product_id or str(menu_item_id) == str(product_id):
                                        categorie = cat_name
                                        break
                                if categorie:
                                    break
                    
                    # Only use other methods if product_id was not available or did not find a match
                    if not categorie:
                        # Method 2: Detect pizza categories by size prefix and search in pizza categories
                        # BUT: Only if it's actually a pizza (check pasta and other categories first)
                        # First, check if it's NOT a pizza by checking other categories that might start with L/M/S
                        # Check pasta's first (they might start with "L" like "Lams verdure")
                        if "pasta's" in self.menu_data:
                            pasta_items = self.menu_data["pasta's"]
                            if isinstance(pasta_items, list):
                                naam_clean_for_check = naam_lower.replace('l ', '').replace('m ', '').replace('s ', '').strip()
                                if '. ' in naam_clean_for_check:
                                    parts = naam_clean_for_check.split('. ', 1)
                                    if len(parts) > 1:
                                        naam_clean_for_check = parts[1].strip()
                                
                                for menu_item in pasta_items:
                                    menu_item_naam = menu_item.get('naam', '')
                                    if menu_item_naam:
                                        menu_naam_clean = menu_item_naam.lower().strip()
                                        if '. ' in menu_naam_clean:
                                            parts = menu_naam_clean.split('. ', 1)
                                            if len(parts) > 1:
                                                menu_naam_clean = parts[1].strip()
                                        
                                        # Exact or close match in pasta category
                                        if naam_clean_for_check == menu_naam_clean or naam_clean_for_check in menu_naam_clean or menu_naam_clean in naam_clean_for_check:
                                            categorie = "pasta's"
                                            break
                                if categorie:
                                    pass  # Found in pasta, skip pizza detection
                        
                        # Only do pizza detection if not found in pasta and has clear pizza indicators
                        if not categorie:
                            # Check size prefix - but be more strict
                            is_large = (' large' in naam_lower or naam_lower.startswith('large ') or '38cm' in naam_lower) and not naam_lower.startswith('lams') and not naam_lower.startswith('l ')
                            is_medium = (' medium' in naam_lower or naam_lower.startswith('medium ') or '30cm' in naam_lower) and not naam_lower.startswith('m ')
                            is_small = (' small' in naam_lower or naam_lower.startswith('small ')) and not naam_lower.startswith('s ')
                            
                            # Also check if it starts with L/M/S followed by a space AND a known pizza name pattern
                            # Pizza names often have numbers or specific patterns
                            starts_with_l_space = naam_lower.startswith('l ') and len(naam_lower) > 2
                            starts_with_m_space = naam_lower.startswith('m ') and len(naam_lower) > 2
                            starts_with_s_space = naam_lower.startswith('s ') and len(naam_lower) > 2
                            
                            # Clean pizza name (remove size prefix and number prefix)
                            pizza_naam_clean = naam_lower
                            if '. ' in pizza_naam_clean:
                                parts = pizza_naam_clean.split('. ', 1)
                                if len(parts) > 1:
                                    pizza_naam_clean = parts[1].strip()
                            
                            # Remove size prefixes
                            if starts_with_l_space:
                                pizza_naam_clean = pizza_naam_clean[2:].strip()
                                is_large = True
                            elif starts_with_m_space:
                                pizza_naam_clean = pizza_naam_clean[2:].strip()
                                is_medium = True
                            elif starts_with_s_space:
                                pizza_naam_clean = pizza_naam_clean[2:].strip()
                                is_small = True
                            
                            pizza_naam_clean = pizza_naam_clean.replace('large ', '').replace('medium ', '').replace('small ', '').strip()
                            
                            # Only search in pizza categories if we have a size indicator OR if name matches a known pizza
                            if is_large or is_medium or is_small:
                                # Search in pizza categories
                                pizza_categories = [
                                    ('Large pizza\'s', is_large),
                                    ('Medium pizza\'s', is_medium),
                                    ('Small pizza\'s', is_small)
                                ]
                                
                                for pizza_cat, is_size_match in pizza_categories:
                                    if not is_size_match:
                                        continue  # Skip if size doesn't match
                                    if pizza_cat in self.menu_data:
                                        cat_items = self.menu_data[pizza_cat]
                                        if isinstance(cat_items, list):
                                            for menu_item in cat_items:
                                                menu_item_naam = menu_item.get('naam', '')
                                                if menu_item_naam:
                                                    menu_naam_clean = menu_item_naam.lower().strip()
                                                    # Remove number prefix if present
                                                    if '. ' in menu_naam_clean:
                                                        parts = menu_naam_clean.split('. ', 1)
                                                        if len(parts) > 1:
                                                            menu_naam_clean = parts[1].strip()
                                                    
                                                    # Match pizza name - must be exact or very close
                                                    if pizza_naam_clean == menu_naam_clean:
                                                        categorie = pizza_cat
                                                        break
                                                    # Partial match only if it's a clear pizza name (not a pasta name)
                                                    elif (pizza_naam_clean in menu_naam_clean or menu_naam_clean in pizza_naam_clean) and len(pizza_naam_clean) > 3:
                                                        # Additional check: make sure it's not a pasta name
                                                        pasta_keywords = ['verdure', 'spaghetti', 'pasta', 'carbonara', 'bolognese']
                                                        is_pasta_name = any(keyword in pizza_naam_clean for keyword in pasta_keywords)
                                                        if not is_pasta_name:
                                                            categorie = pizza_cat
                                                            break
                                            if categorie:
                                                break
                        
                        # Method 3: Detect category from product name hints
                        if not categorie:
                            category_hints = {
                                'groot broodje': 'grote-broodjes',
                                'grote broodje': 'grote-broodjes',
                                'klein broodje': 'klein-broodjes',
                                'kleine broodje': 'klein-broodjes',
                                'durum': 'durum',
                                'turks brood': 'turks-brood',
                                'turks-brood': 'turks-brood',
                                'vis schotel': 'visgerechten',
                                'visschotel': 'visgerechten',
                                'vis schotels': 'visgerechten',
                                'visschotels': 'visgerechten',
                                'vis gerecht': 'visgerechten',
                                'visgerecht': 'visgerechten',
                                'pasta': "pasta's",
                                'spaghetti': "pasta's",
                                'kapsalon': 'Kapsalons',
                            }
                            
                            for hint, cat_name in category_hints.items():
                                if hint in naam_lower and cat_name in self.menu_data:
                                    categorie = cat_name
                                    break
                        
                        # Method 4: Name + price matching (for products that exist in multiple categories)
                        if not categorie:
                            naam_clean = naam.lower().replace('l ', '').replace('m ', '').replace('s ', '').replace('large ', '').replace('medium ', '').replace('small ', '').strip()
                            # Remove number prefixes like "22. "
                            if '. ' in naam_clean:
                                parts = naam_clean.split('. ', 1)
                                if len(parts) > 1:
                                    naam_clean = parts[1].strip()
                            
                            # Try exact name match with price validation
                            best_match = None
                            exact_matches = []
                            partial_matches = []
                            
                            # Search ALL categories including pizza categories
                            for cat_name, cat_items in self.menu_data.items():
                                if not isinstance(cat_items, list):
                                    continue
                                for menu_item in cat_items:
                                    menu_item_naam = menu_item.get('naam', '')
                                    menu_item_prijs = menu_item.get('prijs', 0)
                                    if menu_item_naam:
                                        menu_naam_clean = menu_item_naam.lower().strip()
                                        # Remove number prefix if present
                                        if '. ' in menu_naam_clean:
                                            parts = menu_naam_clean.split('. ', 1)
                                            if len(parts) > 1:
                                                menu_naam_clean = parts[1].strip()
                                        
                                        # Exact match
                                        if naam_clean == menu_naam_clean:
                                            # Check if price matches (within 0.5 euro tolerance)
                                            if abs(prijs - menu_item_prijs) <= 0.5:
                                                exact_matches.append((cat_name, menu_item_prijs, 0))
                                            elif not best_match:
                                                best_match = (cat_name, abs(prijs - menu_item_prijs), 0)
                                        # Partial match (one contains the other)
                                        elif naam_clean in menu_naam_clean or menu_naam_clean in naam_clean:
                                            if abs(prijs - menu_item_prijs) <= 0.5:
                                                partial_matches.append((cat_name, menu_item_prijs, len(naam_clean)))
                            
                            # Use exact match with price validation if available
                            if exact_matches:
                                # If multiple exact matches, use the one with closest price
                                exact_matches.sort(key=lambda x: (x[2], abs(prijs - x[1])))
                                categorie = exact_matches[0][0]
                            elif partial_matches:
                                # Use partial match with closest price
                                partial_matches.sort(key=lambda x: (x[2], abs(prijs - x[1])))
                                categorie = partial_matches[0][0]
                            elif best_match:
                                categorie = best_match[0]
                        
                        # Method 5: Fallback - comprehensive search through ALL categories
                        if not categorie:
                            naam_clean = naam.lower().replace('l ', '').replace('m ', '').replace('s ', '').replace('large ', '').replace('medium ', '').replace('small ', '').strip()
                            if '. ' in naam_clean:
                                parts = naam_clean.split('. ', 1)
                                if len(parts) > 1:
                                    naam_clean = parts[1].strip()
                            
                            # Priority order (most specific first, pizza categories included)
                            priority_categories = [
                                'Large pizza\'s', 'Medium pizza\'s', 'Small pizza\'s',  # Pizza's first
                                'klein-broodjes', 'grote-broodjes', 'durum', 'turks-brood',
                                'visgerechten', "pasta's", 'Kapsalons',
                                'schotels', 'lookbrood', 'mix schotels', 'vegetarisch broodjes',
                                'dranken', 'salades', 'extra\'s', 'desserten', 'alforno'
                            ]
                            
                            # First try priority categories
                            for cat_name in priority_categories:
                                if cat_name not in self.menu_data:
                                    continue
                                cat_items = self.menu_data[cat_name]
                                if isinstance(cat_items, list):
                                    for menu_item in cat_items:
                                        menu_item_naam = menu_item.get('naam', '')
                                        if menu_item_naam:
                                            menu_naam_clean = menu_item_naam.lower().strip()
                                            # Remove number prefix if present
                                            if '. ' in menu_naam_clean:
                                                parts = menu_naam_clean.split('. ', 1)
                                                if len(parts) > 1:
                                                    menu_naam_clean = parts[1].strip()
                                            
                                            if naam_clean == menu_naam_clean:
                                                categorie = cat_name
                                                break
                                if categorie:
                                    break
                            
                            # If still no match, search ALL remaining categories
                            if not categorie:
                                for cat_name, cat_items in self.menu_data.items():
                                    if cat_name in priority_categories:
                                        continue  # Already searched
                                    if not isinstance(cat_items, list):
                                        continue
                                    for menu_item in cat_items:
                                        menu_item_naam = menu_item.get('naam', '')
                                        if menu_item_naam:
                                            menu_naam_clean = menu_item_naam.lower().strip()
                                            # Remove number prefix if present
                                            if '. ' in menu_naam_clean:
                                                parts = menu_naam_clean.split('. ', 1)
                                                if len(parts) > 1:
                                                    menu_naam_clean = parts[1].strip()
                                            
                                            if naam_clean == menu_naam_clean or naam_clean in menu_naam_clean or menu_naam_clean in naam_clean:
                                                categorie = cat_name
                                                break
                                    if categorie:
                                        break
                
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
                
                # Category label - ALWAYS show category (even if empty, show "Onbekend")
                category_display = categorie if categorie else "Onbekend"
                category_label = tk.Label(
                    item_frame,
                    text=f"[{category_display}]",
                    font=("Arial", 9, "italic"),
                    bg="white",
                    fg="#666" if categorie else "#999",
                    anchor="w"
                )
                category_label.pack(anchor=tk.W, pady=(5, 2))
                
                # Main item label (larger, bold, better contrast)
                item_label = tk.Label(
                    item_frame,
                    text=item_text,
                    font=("Arial", 11, "bold"),
                    bg="white",
                    fg="#000",
                    anchor="w",
                    wraplength=350
                )
                item_label.pack(anchor=tk.W, pady=(2, 2))
                
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
                                font=("Arial", 10),
                                bg="white",
                                fg="#333",
                                anchor="w"
                            ).pack(anchor=tk.W, padx=(10, 0))
                
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
                            font=("Arial", 10),
                            bg="white",
                            fg="#444",
                            anchor="w"
                        ).pack(anchor=tk.W, padx=(10, 0))
        
        # Opmerkingen (comments) as separate item if exists - format: "1x Opmerkingen"
        order_opmerking = order.get('opmerking')
        if order_opmerking:
            opmerking_frame = tk.Frame(items_list_frame, bg="white", relief=tk.FLAT, borderwidth=1)
            opmerking_frame.pack(fill=tk.X, pady=4, padx=5)
            
            # Note: In example, opmerkingen has a price, but we'll show it without price
            # unless there's a specific charge for it
            tk.Label(
                opmerking_frame,
                text="Opmerkingen:",
                font=("Arial", 11, "bold"),
                bg="white",
                fg="#000",
                anchor="w"
            ).pack(anchor=tk.W, pady=(5, 2))
            
            # Opmerking text (indented for clarity, larger font)
            tk.Label(
                opmerking_frame,
                text=order_opmerking,
                font=("Arial", 10),
                bg="white",
                fg="#000",
                anchor="w",
                wraplength=350,
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=(15, 0), pady=(0, 5))
        
        # RIGHT PANEL - Customer info and actions
        # Action buttons at top (matching example)
        actions_frame = tk.Frame(right_panel, bg="white")
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Bestelling afdrukken button
        print_btn = tk.Button(
            actions_frame,
            text="🖨️ Bestelling afdrukken",
            command=lambda: self.print_order(order),
            bg="#FF9800",  # Orange
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.RAISED,
            borderwidth=2
        )
        print_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Routebeschrijving button
        route_btn = tk.Button(
            actions_frame,
            text="🌐 Routebeschrijving",
            command=lambda: self.show_route(order),
            bg="#2196F3",  # Blue
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.RAISED,
            borderwidth=2
        )
        route_btn.pack(side=tk.LEFT)
        
        # Klantgegevens section - scrollable
        klant_label_frame = tk.LabelFrame(
            right_panel,
            text="Klantgegevens",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#000",
            padx=10,
            pady=10,
            relief=tk.RAISED,
            borderwidth=2
        )
        klant_label_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Scrollable canvas for customer details
        klant_canvas = tk.Canvas(klant_label_frame, bg="white", highlightthickness=0)
        klant_scrollbar = ttk.Scrollbar(klant_label_frame, orient="vertical", command=klant_canvas.yview)
        klant_frame = tk.Frame(klant_canvas, bg="white")
        
        klant_canvas_window = klant_canvas.create_window((0, 0), window=klant_frame, anchor="nw")
        klant_canvas.configure(yscrollcommand=klant_scrollbar.set)
        
        def _on_klant_canvas_configure(event):
            canvas_width = event.width
            klant_canvas.itemconfig(klant_canvas_window, width=canvas_width)
        
        def _on_klant_frame_configure(event):
            klant_canvas.configure(scrollregion=klant_canvas.bbox("all"))
        
        klant_canvas.bind('<Configure>', _on_klant_canvas_configure)
        klant_frame.bind('<Configure>', _on_klant_frame_configure)
        
        klant_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        klant_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
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
            detail_frame.pack(fill=tk.X, pady=4, padx=5)
            
            label_widget = tk.Label(
                detail_frame,
                text=f"{label}:",
                font=("Arial", 11, "bold"),
                bg="white",
                fg="#000",
                anchor="w",
                width=14
            )
            label_widget.pack(side=tk.LEFT)
            
            value_widget = tk.Label(
                detail_frame,
                text=value,
                font=("Arial", 11),
                bg="white",
                fg="#000",
                anchor="w",
                wraplength=250
            )
            value_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Opmerkingen section (matching example) - make it more visible
        opmerkingen_frame = tk.LabelFrame(
            right_panel,
            text="Opmerkingen",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#000",
            padx=15,
            pady=15,
            relief=tk.RAISED,
            borderwidth=2
        )
        opmerkingen_frame.pack(fill=tk.X, pady=(0, 0))
        
        if order_opmerking:
            opmerking_label = tk.Label(
                opmerkingen_frame,
                text=order_opmerking,
                font=("Arial", 11),
                bg="white",
                fg="#000",
                anchor="w",
                justify=tk.LEFT,
                wraplength=300
            )
            opmerking_label.pack(anchor=tk.W, fill=tk.X, padx=5, pady=5)
        else:
            opmerking_label = tk.Label(
                opmerkingen_frame,
                text="Geen opmerkingen beschikbaar",
                font=("Arial", 11),
                bg="white",
                fg="#999",
                anchor="w"
            )
            opmerking_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # Footer buttons (matching example - flat buttons, no extra space)
        footer_frame = tk.Frame(details_frame, bg="#F5F5DC")
        footer_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
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
                # Status updated successfully, refresh orders silently
                self.refresh_orders()
            elif response.status_code == 401:
                # Token expired, try to re-authenticate
                import time
                current_time = time.time()
                # Only try to re-authenticate if enough time has passed (backoff)
                if current_time - self.last_auth_attempt >= self.auth_backoff:
                    logger.debug("Token expired, re-authenticating...")
                    self.last_auth_attempt = current_time
                    if self.authenticate_api():
                        # Reset backoff on success
                        self.auth_backoff = 0
                        # Retry the request
                        response = self.api_session.put(
                            f"{API_BASE_URL}/orders/{order_id}/status",
                            json=payload
                        )
                        if response.status_code == 200:
                            # Status updated successfully, refresh orders silently
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
                        # Increase backoff on failure
                        self.auth_backoff = min(self.auth_backoff * 2 + 5, 60)
                        logger.warning(f"Re-authentication failed, backing off for {self.auth_backoff}s")
                        messagebox.showerror("Fout", "Kon niet opnieuw authenticeren met API")
                else:
                    messagebox.showerror("Fout", "Authenticatie mislukt. Probeer het later opnieuw.")
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
            # Check if order is pickup (afhaal) - can be boolean or integer (0/1)
            is_afhaal = order.get('afhaal', False)
            if isinstance(is_afhaal, int):
                is_afhaal = bool(is_afhaal)
            
            klant_data = {
                "naam": order.get('klant_naam', 'Onbekend'),
                "telefoon": order.get('klant_telefoon', ''),
                "adres": order.get('klant_adres', '').split(',')[0] if order.get('klant_adres') else '',
                "huisnummer": "",
                "postcode": "",
                "gemeente": "",
                "levertijd": order.get('levertijd', ''),
                "afhaal": is_afhaal,
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

