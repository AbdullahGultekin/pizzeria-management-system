"""
Order History Module

This module provides a modern interface for viewing, searching, and managing order history.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, List, Optional, Any, Callable
import json
from datetime import date
from database import DatabaseContext
from logging_config import get_logger
from exceptions import DatabaseError
from modules.history_service import HistoryService
from modules.history_ui import HistoryUI

logger = get_logger("pizzeria.geschiedenis")


class HistoryManager:
    """Manager class for order history interface."""
    
    def __init__(
        self,
        parent: tk.Widget,
        menu_data: Dict[str, Any],
        extras_data: Dict[str, Any],
        app_settings: Dict[str, Any],
        load_order_callback: Callable
    ):
        """
        Initialize history manager.
        
        Args:
            parent: Parent widget (tab frame)
            menu_data: Menu data dictionary
            extras_data: Extras data dictionary
            app_settings: Application settings
            load_order_callback: Callback to load order for editing
        """
        self.parent = parent
        self.menu_data = menu_data
        self.extras_data = extras_data
        self.app_settings = app_settings
        self.load_order_callback = load_order_callback
        
        self.service = HistoryService()
        self.ui = HistoryUI()
        
        # UI components
        self.tree: Optional[ttk.Treeview] = None
        self.filter_vars: Dict[str, tk.Variable] = {}
        self.stats_vars: Optional[Dict[str, tk.StringVar]] = None
        
    def setup_ui(self) -> None:
        """Setup the main UI."""
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Configure parent background
        self.parent.configure(bg=HistoryUI.COLORS['bg_primary'])
        
        # Main container with proper layout
        main_container = tk.Frame(self.parent, bg=HistoryUI.COLORS['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Top section (filters)
        top_section = tk.Frame(main_container, bg=HistoryUI.COLORS['bg_primary'])
        top_section.pack(fill=tk.X, padx=0, pady=0)
        
        # Setup filter bar in top section
        self.filter_vars = self.ui.create_filter_bar(
            top_section,
            on_search_change=self.refresh_data,
            on_date_change=self.refresh_data,
            on_refresh=lambda: self.refresh_data(force=True)
        )
        
        # Buttons section - above statistics, clearly visible
        buttons_section = tk.Frame(main_container, bg=HistoryUI.COLORS['bg_primary'])
        buttons_section.pack(fill=tk.X, padx=0, pady=(5, 5))
        
        # Setup action buttons in buttons section
        self.setup_buttons(buttons_section)
        
        # Statistics section - below buttons
        stats_section = tk.Frame(main_container, bg=HistoryUI.COLORS['bg_primary'])
        stats_section.pack(fill=tk.X, padx=0, pady=0)
        
        # Setup statistics panel in stats section
        initial_stats = {'count': 0, 'total': 0.0, 'average': 0.0}
        stats_frame, self.stats_vars = self.ui.create_statistics_panel(stats_section, initial_stats)
        
        # Middle section (table) - expandable
        middle_section = tk.Frame(main_container, bg=HistoryUI.COLORS['bg_primary'])
        middle_section.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 0))
        
        # Setup orders table in middle section
        self.tree = self.ui.create_orders_table(middle_section)
        
        # Bind double-click to show details
        self.tree.bind("<Double-1>", lambda e: self.show_order_details())
        
        # Bind single click to show details (optional, can be removed if not needed)
        self.tree.bind("<Button-1>", lambda e: self._on_table_click(e))
        
        # Load initial data
        self.refresh_data()
    
    def setup_buttons(self, parent: tk.Widget) -> None:
        """Setup action buttons."""
        # Create button frame with more prominent styling
        button_frame = tk.Frame(parent, bg=HistoryUI.COLORS['bg_primary'], padx=15, pady=15)
        button_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # Add a subtle border/background to make buttons more visible
        button_container = tk.Frame(button_frame, bg=HistoryUI.COLORS['bg_secondary'], relief="flat", borderwidth=1)
        button_container.pack(fill=tk.X, padx=5, pady=5)
        
        # Left side - primary actions
        left_buttons = tk.Frame(button_container, bg=HistoryUI.COLORS['bg_secondary'])
        left_buttons.pack(side=tk.LEFT, padx=10, pady=8)
        
        # Edit button
        edit_btn = tk.Button(
            left_buttons,
            text="✏️ Bewerk & Herdruk",
            command=self.edit_order,
            bg=HistoryUI.COLORS['bg_success'],
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=25,
            pady=10,
            cursor="hand2"
        )
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Reopen button (to add items without deleting old order)
        reopen_btn = tk.Button(
            left_buttons,
            text="➕ Heropen Bon",
            command=self.reopen_order,
            bg=HistoryUI.COLORS['bg_info'],
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=25,
            pady=10,
            cursor="hand2"
        )
        reopen_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Renumber button
        renumber_btn = tk.Button(
            left_buttons,
            text="🔢 Hernummer Bonnen",
            command=self.renumber_receipts,
            bg="#FFA500",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=25,
            pady=10,
            cursor="hand2"
        )
        renumber_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Details button
        details_btn = tk.Button(
            left_buttons,
            text="👁️ Details",
            command=self.show_order_details,
            bg=HistoryUI.COLORS['bg_accent'],
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=25,
            pady=10,
            cursor="hand2"
        )
        details_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Right side - danger actions
        right_buttons = tk.Frame(button_container, bg=HistoryUI.COLORS['bg_secondary'])
        right_buttons.pack(side=tk.RIGHT, padx=10, pady=8)
        
        # Delete button
        delete_btn = tk.Button(
            right_buttons,
            text="🗑️ Verwijder Bestelling",
            command=self.delete_order,
            bg=HistoryUI.COLORS['bg_danger'],
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=25,
            pady=10,
            cursor="hand2"
        )
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Delete all button
        delete_all_btn = tk.Button(
            right_buttons,
            text="⚠️ Verwijder Alles",
            command=self.delete_all_orders,
            bg="#8B0000",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=25,
            pady=10,
            cursor="hand2"
        )
        delete_all_btn.pack(side=tk.LEFT)
        
        # Hover effects
        def add_hover_effect(btn, original_color):
            def on_enter(e):
                btn.config(bg=HistoryUI._lighten_color(original_color))
            
            def on_leave(e):
                btn.config(bg=original_color)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        add_hover_effect(edit_btn, HistoryUI.COLORS['bg_success'])
        add_hover_effect(reopen_btn, HistoryUI.COLORS['bg_info'])
        add_hover_effect(details_btn, HistoryUI.COLORS['bg_accent'])
        add_hover_effect(delete_btn, HistoryUI.COLORS['bg_danger'])
        add_hover_effect(delete_all_btn, "#8B0000")
    
    def refresh_data(self, force: bool = False) -> None:
        """Refresh order data and update display."""
        if not self.tree:
            return
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get filter values
        search_term = self.filter_vars.get("search", tk.StringVar()).get()
        date_filter = self.filter_vars.get("date", tk.StringVar()).get()
        
        # Clean search term (remove placeholder)
        if search_term == "Naam, telefoon of adres...":
            search_term = ""
        
        # Get orders
        try:
            orders = self.service.search_orders(
                search_term=search_term if search_term else None,
                date_filter=date_filter if date_filter else None
            )
        except DatabaseError as e:
            logger.exception("Error loading orders")
            messagebox.showerror("Fout", str(e), parent=self.parent)
            return
        
        # Add orders to tree with zebra striping
        for idx, order in enumerate(orders):
            adres = f"{order.get('straat', '')} {order.get('huisnummer', '')}".strip()
            tag = "even" if idx % 2 == 0 else "odd"
            
            levertijd = order.get('levertijd', '') or ''
            
            self.tree.insert(
                "",
                "end",
                iid=order['id'],
                values=(
                    order['datum'],
                    order['tijd'],
                    order['bonnummer'],
                    order.get('naam', ''),
                    order.get('telefoon', ''),
                    adres,
                    levertijd,
                    f"€{order['totaal']:.2f}"
                ),
                tags=(tag,)
            )
        
        # Update statistics
        self.update_statistics(search_term, date_filter)
    
    def update_statistics(self, search_term: Optional[str] = None, date_filter: Optional[str] = None) -> None:
        """Update statistics panel."""
        if not self.stats_vars:
            return
        
        stats = self.service.get_statistics(search_term, date_filter)
        self.stats_vars['count'].set(str(int(stats['count'])))
        self.stats_vars['total'].set(f"€{stats['total']:.2f}")
        self.stats_vars['average'].set(f"€{stats['average']:.2f}")
    
    def edit_order(self) -> None:
        """Load selected order for editing."""
        selected_item_id = self.tree.focus()
        if not selected_item_id:
            messagebox.showwarning(
                "Selectie Fout",
                "Selecteer alstublieft een bestelling om te bewerken.",
                parent=self.parent
            )
            return
        
        bestelling_id = int(selected_item_id)
        
        if not messagebox.askyesno(
            "Bevestigen",
            "Weet u zeker dat u deze bestelling wilt laden om te bewerken?\n\n"
            "De originele bestelling wordt hierbij verwijderd en vervangen door de nieuwe versie na het opslaan.",
            icon='warning',
            parent=self.parent
        ):
            return
        
        try:
            order_details = self.service.get_order_details(bestelling_id)
            if not order_details:
                messagebox.showerror("Fout", "Bestelling niet gevonden in de database.", parent=self.parent)
                return
            
            order = order_details['order']
            items = order_details['items']
            
            # Format customer data
            klant_data = {
                "klant_id": order['klant_id'],
                "telefoon": order['telefoon'],
                "adres": order['straat'],
                "nr": order['huisnummer'],
                "postcode_gemeente": order['plaats'],
                "opmerking": order['opmerking'] or "",
                "naam": order['naam'] or "",
                "levertijd": order.get('levertijd') or None
            }
            
            # Format order items
            formatted_items = []
            for item in items:
                formatted_items.append({
                    'categorie': item['categorie'],
                    'product': item['product'],
                    'aantal': item['aantal'],
                    'prijs': item['prijs'],
                    'extras': json.loads(item['extras']) if item.get('extras') else {},
                    'opmerking': ''  # opmerking is not stored in bestelregels table
                })
            
            # Load in main screen
            self.load_order_callback(klant_data, formatted_items, bestelling_id)
            
            # Refresh list
            self.refresh_data(force=True)
            
            messagebox.showinfo(
                "Geladen",
                "Bestelling is geladen in het hoofdscherm. U kunt deze nu bewerken.",
                parent=self.parent
            )
        except DatabaseError as e:
            logger.exception("Error loading order for editing")
            messagebox.showerror("Fout", f"Er is een fout opgetreden: {e}", parent=self.parent)
    
    def delete_order(self) -> None:
        """Delete selected order."""
        selected_item_id = self.tree.focus()
        if not selected_item_id:
            messagebox.showwarning(
                "Selectie Fout",
                "Selecteer een bestelling om te verwijderen.",
                parent=self.parent
            )
            return
        
        if not messagebox.askyesno(
            "Zeker weten?",
            "Weet u zeker dat u deze bestelling definitief wilt verwijderen?\n"
            "Dit kan niet ongedaan worden gemaakt.",
            icon='warning',
            parent=self.parent
        ):
            return
        
        bestelling_id = int(selected_item_id)
        
        try:
            klant_id = self.service.delete_order(bestelling_id)
            
            # Update customer statistics if needed
            if klant_id:
                from database import update_klant_statistieken
                update_klant_statistieken(klant_id)
            
            messagebox.showinfo("Succes", "Bestelling succesvol verwijderd.", parent=self.parent)
            self.refresh_data(force=True)
        except DatabaseError as e:
            logger.exception("Error deleting order")
            messagebox.showerror("Fout", f"Kon bestelling niet verwijderen: {e}", parent=self.parent)
    
    def delete_all_orders(self) -> None:
        """Delete all orders after confirmation."""
        if not messagebox.askyesno(
            "Alles verwijderen?",
            "Weet u zeker dat u ALLE bestellingen permanent wilt verwijderen?\n"
            "Dit kan niet ongedaan worden gemaakt.",
            icon='warning',
            parent=self.parent
        ):
            return
        
        confirm = simpledialog.askstring(
            "Bevestig",
            "Typ VERWIJDER ALLES om te bevestigen:",
            parent=self.parent
        )
        
        if (confirm or "").strip().upper() != "VERWIJDER ALLES":
            messagebox.showinfo("Geannuleerd", "Verwijderen geannuleerd.", parent=self.parent)
            return
        
        try:
            klant_ids = self.service.delete_all_orders()
            
            # Update customer statistics
            if klant_ids:
                from database import update_klant_statistieken
                for klant_id in set(klant_ids):
                    if klant_id:
                        update_klant_statistieken(klant_id)
            
            messagebox.showinfo("Gereed", "Alle bestellingen zijn verwijderd.", parent=self.parent)
            self.refresh_data(force=True)
        except DatabaseError as e:
            logger.exception("Error deleting all orders")
            messagebox.showerror("Fout", f"Kon alle bestellingen niet verwijderen: {e}", parent=self.parent)
    
    def _on_table_click(self, event) -> None:
        """Handle table click event."""
        # This can be used for single-click selection if needed
        pass
    
    def show_order_details(self) -> None:
        """Show detailed view of selected order."""
        selected_item_id = self.tree.focus()
        if not selected_item_id:
            messagebox.showwarning(
                "Selectie Fout",
                "Selecteer een bestelling om details te bekijken.",
                parent=self.parent
            )
            return
        
        bestelling_id = int(selected_item_id)
        
        try:
            order_details = self.service.get_order_details(bestelling_id)
            if not order_details:
                messagebox.showerror("Fout", "Bestelling niet gevonden.", parent=self.parent)
                return
            
            order = order_details['order']
            items = order_details['items']
            
            # Create details window
            details_win = tk.Toplevel(self.parent)
            details_win.title(f"Bestelling Details - Bon {order['bonnummer']}")
            details_win.geometry("700x600")
            details_win.transient(self.parent)
            details_win.configure(bg=HistoryUI.COLORS['bg_primary'])
            
            # Main frame with scroll
            main_frame = tk.Frame(details_win, bg=HistoryUI.COLORS['bg_primary'], padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Customer info section
            customer_frame = tk.LabelFrame(
                main_frame,
                text="Klantgegevens",
                font=("Arial", 11, "bold"),
                bg=HistoryUI.COLORS['bg_secondary'],
                padx=15,
                pady=10
            )
            customer_frame.pack(fill=tk.X, pady=(0, 15))
            
            customer_info = f"""
Naam: {order.get('naam', 'N/A')}
Telefoon: {order.get('telefoon', 'N/A')}
Adres: {order.get('straat', '')} {order.get('huisnummer', '')}
Plaats: {order.get('plaats', 'N/A')}
            """.strip()
            
            tk.Label(
                customer_frame,
                text=customer_info,
                font=("Arial", 10),
                bg=HistoryUI.COLORS['bg_secondary'],
                justify=tk.LEFT,
                anchor="w"
            ).pack(anchor="w")
            
            # Order info section
            order_info_frame = tk.LabelFrame(
                main_frame,
                text="Bestelling Informatie",
                font=("Arial", 11, "bold"),
                bg=HistoryUI.COLORS['bg_secondary'],
                padx=15,
                pady=10
            )
            order_info_frame.pack(fill=tk.X, pady=(0, 15))
            
            levertijd = order.get('levertijd', '') or 'Niet opgegeven'
            order_info = f"""
Bonnummer: {order['bonnummer']}
Datum: {order.get('datum', 'N/A')}
Tijd: {order.get('tijd', 'N/A')}
Levertijd: {levertijd}
Opmerking: {order.get('opmerking', 'Geen')}
            """.strip()
            
            tk.Label(
                order_info_frame,
                text=order_info,
                font=("Arial", 10),
                bg=HistoryUI.COLORS['bg_secondary'],
                justify=tk.LEFT,
                anchor="w"
            ).pack(anchor="w")
            
            # Items section
            items_frame = tk.LabelFrame(
                main_frame,
                text="Bestelde Items",
                font=("Arial", 11, "bold"),
                bg=HistoryUI.COLORS['bg_secondary'],
                padx=15,
                pady=10
            )
            items_frame.pack(fill=tk.BOTH, expand=True)
            
            # Scrollable text for items
            items_text = tk.Text(
                items_frame,
                wrap=tk.WORD,
                font=("Courier New", 10),
                bg=HistoryUI.COLORS['bg_primary'],
                fg=HistoryUI.COLORS['text_primary'],
                padx=10,
                pady=10,
                relief="flat"
            )
            items_text.pack(fill=tk.BOTH, expand=True)
            
            # Scrollbar for items
            items_scroll = tk.Scrollbar(items_frame, orient=tk.VERTICAL, command=items_text.yview)
            items_text.configure(yscrollcommand=items_scroll.set)
            items_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Format and display items
            total = 0.0
            items_text.insert(tk.END, "Bestellingsoverzicht\n")
            items_text.insert(tk.END, "=" * 50 + "\n\n")
            
            for idx, item in enumerate(items, 1):
                try:
                    extras = json.loads(item['extras']) if item.get('extras') else {}
                except (json.JSONDecodeError, TypeError):
                    extras = {}
                
                aantal = item.get('aantal', 1)
                prijs = float(item.get('prijs', 0))
                regel_totaal = prijs * aantal
                total += regel_totaal
                
                # Format product name
                product_naam = item.get('product', 'Onbekend')
                categorie = item.get('categorie', '')
                
                # Handle half-half pizzas
                if extras.get('half_half') and isinstance(extras['half_half'], list):
                    product_display = f"Half-Half: Pizza {extras['half_half'][0]}/{extras['half_half'][1]}"
                else:
                    # Use get_pizza_num for pizza numbers
                    from utils.menu_utils import get_pizza_num
                    if "pizza" in categorie.lower():
                        nummer = get_pizza_num(product_naam)
                        product_display = f"Pizza {nummer}"
                    else:
                        product_display = product_naam
                
                items_text.insert(tk.END, f"[{idx}] {product_display}\n")
                items_text.insert(tk.END, f"    Categorie: {categorie}\n")
                items_text.insert(tk.END, f"    Aantal: {aantal} x €{prijs:.2f} = €{regel_totaal:.2f}\n")
                
                # Display extras
                if extras:
                    items_text.insert(tk.END, "    Extras:\n")
                    for key, value in extras.items():
                        if key == 'half_half':
                            continue  # Already shown
                        if key == 'sauzen_toeslag':
                            try:
                                items_text.insert(tk.END, f"      • Sauzen extra: €{float(value):.2f}\n")
                            except (ValueError, TypeError):
                                pass
                        elif isinstance(value, list):
                            items_text.insert(tk.END, f"      • {key}: {', '.join(map(str, value))}\n")
                        elif value:
                            items_text.insert(tk.END, f"      • {key}: {value}\n")
                
                # Display item note if present
                if item.get('opmerking'):
                    items_text.insert(tk.END, f"    Opmerking: {item['opmerking']}\n")
                
                items_text.insert(tk.END, "\n")
            
            items_text.insert(tk.END, "=" * 50 + "\n")
            items_text.insert(tk.END, f"Totaal: €{total:.2f}\n")
            
            items_text.config(state=tk.DISABLED)
            
            # Close button
            close_btn = tk.Button(
                details_win,
                text="Sluiten",
                command=details_win.destroy,
                bg=HistoryUI.COLORS['bg_accent'],
                fg="white",
                font=("Arial", 10, "bold"),
                relief="flat",
                padx=30,
                pady=8
            )
            close_btn.pack(pady=10)
        except DatabaseError as e:
            logger.exception("Error showing order details")
            messagebox.showerror("Fout", f"Er is een fout opgetreden: {e}", parent=self.parent)
    
    def reopen_order(self) -> None:
        """Reopen order to add items without deleting the original order."""
        selected_item_id = self.tree.focus()
        if not selected_item_id:
            messagebox.showwarning(
                "Selectie Fout",
                "Selecteer een bestelling om te heropenen.",
                parent=self.parent
            )
            return
        
        bestelling_id = int(selected_item_id)
        
        if not messagebox.askyesno(
            "Bon Heropenen",
            "Wilt u deze bon heropenen om items toe te voegen?\n\n"
            "De originele bestelling blijft behouden. Nieuwe items worden toegevoegd aan een nieuwe bestelling.",
            icon='question',
            parent=self.parent
        ):
            return
        
        try:
            order_details = self.service.get_order_details(bestelling_id)
            if not order_details:
                messagebox.showerror("Fout", "Bestelling niet gevonden in de database.", parent=self.parent)
                return
            
            order = order_details['order']
            items = order_details['items']
            
            # Format customer data
            klant_data = {
                "klant_id": order['klant_id'],
                "telefoon": order['telefoon'],
                "adres": order['straat'],
                "nr": order['huisnummer'],
                "postcode_gemeente": order['plaats'],
                "opmerking": "",  # Start with empty note for new order
                "naam": order['naam'] or "",
                "levertijd": order.get('levertijd') or None
            }
            
            # Format order items (empty list - user can add new items)
            formatted_items = []
            
            # Load in main screen WITHOUT the old order ID (so it creates a new order)
            self.load_order_callback(klant_data, formatted_items, None)
            
            messagebox.showinfo(
                "Heropend",
                "Bon is heropend met klantgegevens. U kunt nu nieuwe items toevoegen.\n\n"
                "De originele bestelling blijft behouden.",
                parent=self.parent
            )
        except DatabaseError as e:
            logger.exception("Error reopening order")
            messagebox.showerror("Fout", f"Er is een fout opgetreden: {e}", parent=self.parent)
    
    def renumber_receipts(self) -> None:
        """Hernummer alle bonnen zodat ze weer in de juiste volgorde zijn."""
        from tkinter import messagebox
        from datetime import datetime
        import database
        
        # Bevestiging vragen
        result = messagebox.askyesno(
            "Bonnen hernummeren",
            "Weet u zeker dat u alle bonnen wilt hernummeren?\n\n"
            "Dit zorgt ervoor dat alle bonnen opnieuw worden genummerd in volgorde van datum en tijd.\n"
            "Deze actie kan niet ongedaan worden gemaakt.",
            parent=self.parent
        )
        
        if not result:
            return
        
        try:
            conn = database.get_db_connection()
            cur = conn.cursor()
            
            # Haal alle bestellingen op, gesorteerd op datum en tijd
            cur.execute("""
                SELECT id, datum, tijd
                FROM bestellingen
                ORDER BY datum ASC, tijd ASC
            """)
            
            orders = cur.fetchall()
            
            if not orders:
                messagebox.showinfo("Info", "Geen bestellingen gevonden om te hernummeren.", parent=self.parent)
                conn.close()
                return
            
            # Hernummer per dag
            current_date = None
            day_counter = {}
            updates = []
            
            for order in orders:
                order_id = order['id']
                order_date = order['datum']
                
                # Reset teller voor nieuwe dag
                if order_date != current_date:
                    current_date = order_date
                    # Parse jaar uit datum
                    try:
                        year = int(order_date.split('-')[0])
                    except (ValueError, IndexError):
                        year = datetime.now().year
                    
                    # Start teller voor deze dag
                    day_counter[order_date] = {'year': year, 'counter': 0}
                
                # Verhoog teller
                day_counter[order_date]['counter'] += 1
                counter = day_counter[order_date]['counter']
                year = day_counter[order_date]['year']
                
                # Genereer nieuw bonnummer: YYYYNNNN
                new_bonnummer = f"{year}{counter:04d}"
                
                updates.append((new_bonnummer, order_id))
            
            # Update alle bonnummers
            updated_count = 0
            for new_bonnummer, order_id in updates:
                cur.execute("""
                    UPDATE bestellingen
                    SET bonnummer = ?
                    WHERE id = ?
                """, (new_bonnummer, order_id))
                updated_count += 1
            
            conn.commit()
            conn.close()
            
            # Update bon_teller tabel voor alle betrokken dagen
            conn = database.get_db_connection()
            cur = conn.cursor()
            
            for date_str, info in day_counter.items():
                try:
                    # Parse datum om jaar en dag te krijgen
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    year = date_obj.year
                    day_of_year = date_obj.timetuple().tm_yday
                    last_number = info['counter']
                    
                    # Update bon_teller
                    cur.execute("""
                        INSERT OR REPLACE INTO bon_teller (jaar, dag, laatste_nummer)
                        VALUES (?, ?, ?)
                    """, (year, day_of_year, last_number))
                except Exception as e:
                    logger.warning(f"Kon bon_teller niet updaten voor {date_str}: {e}")
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo(
                "Succes",
                f"Bonnen succesvol hernummerd!\n\n"
                f"Aantal bijgewerkte bonnen: {updated_count}\n\n"
                f"De lijst wordt nu ververst.",
                parent=self.parent
            )
            
            # Refresh data
            self.refresh_data()
            
        except Exception as e:
            logger.exception("Error renumbering receipts")
            messagebox.showerror(
                "Fout",
                f"Er is een fout opgetreden bij het hernummeren:\n{e}",
                parent=self.parent
            )


def open_geschiedenis(
    root: tk.Widget,
    menu_data_global: Dict[str, Any],
    extras_data_global: Dict[str, Any],
    app_settings_global: Dict[str, Any],
    laad_bestelling_callback: Callable
) -> None:
    """
    Open order history interface.
    
    Args:
        root: Root widget (tab frame)
        menu_data_global: Menu data dictionary
        extras_data_global: Extras data dictionary
        app_settings_global: Application settings
        laad_bestelling_callback: Callback to load order for editing
    """
    manager = HistoryManager(
        root,
        menu_data_global,
        extras_data_global,
        app_settings_global,
        laad_bestelling_callback
    )
    manager.setup_ui()
