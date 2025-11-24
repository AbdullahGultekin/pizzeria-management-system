"""
Afhaal (Pickup) Orders Management Module

This module provides an interface for managing pickup orders separately from delivery orders.
"""
from datetime import date, datetime
from typing import Dict, List, Optional
import tkinter as tk
from tkinter import ttk, messagebox
from logging_config import get_logger
from database import DatabaseContext
from exceptions import DatabaseError

logger = get_logger("pizzeria.afhaal")


class AfhaalManager:
    """Main manager class for pickup orders interface."""
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize afhaal manager.
        
        Args:
            parent: Parent widget (usually a tab frame)
        """
        self.parent = parent
        self.tree: Optional[ttk.Treeview] = None
        self.filter_vars: Dict[str, tk.Variable] = {}
        self.total_label: Optional[tk.Label] = None
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Setup the user interface."""
        # Clear existing widgets
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = tk.Frame(self.parent, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top section - Title and controls
        top_frame = tk.Frame(main_frame, bg="white", padx=10, pady=10)
        top_frame.pack(fill=tk.X)
        
        tk.Label(
            top_frame,
            text="Afhaal Bestellingen",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#333"
        ).pack(side=tk.LEFT)
        
        # Date filter
        date_frame = tk.Frame(top_frame, bg="white")
        date_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Label(date_frame, text="Datum:", bg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.filter_vars["datum"] = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        date_entry = tk.Entry(date_frame, textvariable=self.filter_vars["datum"], width=12, font=("Arial", 9))
        date_entry.pack(side=tk.LEFT, padx=(0, 5))
        date_entry.bind("<Return>", lambda e: self.load_orders(force=True))
        
        tk.Button(
            date_frame,
            text="Vernieuwen",
            command=lambda: self.load_orders(force=True),
            bg="#FF9800",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=10,
            pady=3
        ).pack(side=tk.LEFT)
        
        # Table frame
        table_frame = tk.Frame(main_frame, bg="white", padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Setup table
        self.setup_table(table_frame)
        
        # Total label at bottom
        total_frame = tk.Frame(main_frame, bg="white", padx=10, pady=5)
        total_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Label(
            total_frame,
            text="Totaal alle bestellingen:",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#333"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.total_label = tk.Label(
            total_frame,
            text="€0.00",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#FF9800"
        )
        self.total_label.pack(side=tk.LEFT)
        
        # Load initial data
        self.load_orders()
    
    def setup_table(self, parent: tk.Widget) -> None:
        """Setup the orders table."""
        # Create treeview with scrollbars
        tree_frame = tk.Frame(parent, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ("Soort", "Nummer", "Totaal", "Naam", "Telefoon", "Tijd", "Status")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            selectmode=tk.EXTENDED
        )
        
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading("Soort", text="Soort")
        self.tree.heading("Nummer", text="Nummer")
        self.tree.heading("Totaal", text="Totaal")
        self.tree.heading("Naam", text="Naam")
        self.tree.heading("Telefoon", text="Telefoon")
        self.tree.heading("Tijd", text="Tijd")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("Soort", width=80, anchor="center")
        self.tree.column("Nummer", width=100, anchor="center")
        self.tree.column("Totaal", width=80, anchor="e")
        self.tree.column("Naam", width=150, anchor="w")
        self.tree.column("Telefoon", width=120, anchor="w")
        self.tree.column("Tijd", width=80, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Double-click to view details
        self.tree.bind("<Double-Button-1>", self.view_order_details)
    
    def load_orders(self, force: bool = False) -> None:
        """Load and display pickup orders."""
        if not self.tree:
            return
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get date
        datum_str = self.filter_vars.get("datum", tk.StringVar(value=date.today().strftime('%Y-%m-%d'))).get()
        try:
            order_date = datetime.strptime(datum_str, '%Y-%m-%d').date()
        except ValueError:
            order_date = date.today()
        
        # Get pickup orders from database
        try:
            orders = self.get_afhaal_orders_for_date(order_date)
        except DatabaseError as e:
            logger.exception("Error loading pickup orders")
            messagebox.showerror("Fout", str(e))
            return
        
        # Display orders
        for order in orders:
            soort = "Lokaal"
            nummer = order.get('bonnummer', 'N/A')
            totaal = f"€{order.get('totaal', 0):.2f}"
            naam = order.get('klant_naam', 'N/A')
            telefoon = order.get('telefoon', 'N/A')
            tijd = order.get('tijd', 'N/A')
            # Get status from database, default to "Nieuw" if not set
            status = order.get('status', 'Nieuw')
            if not status or status not in ['Nieuw', 'Afgehaald']:
                status = 'Nieuw'
            
            # Store order ID in item for status updates
            item_id = f"order_{order.get('id')}"
            
            self.tree.insert(
                "",
                tk.END,
                iid=item_id,
                values=(soort, nummer, totaal, naam, telefoon, tijd, status),
                tags=("afhaal", f"status_{status.lower()}")
            )
        
        # Configure tag colors
        self.tree.tag_configure("afhaal", background="#FFF9C4")  # Light yellow for pickup orders
        self.tree.tag_configure("status_nieuw", background="#FFF9C4")  # Light yellow for new orders
        self.tree.tag_configure("status_afgehaald", background="#C8E6C9")  # Light green for picked up orders
        
        # Bind click on status column to change status
        self.tree.bind("<Button-1>", self._on_tree_click)
        
        # Update total
        self._update_total(orders)
    
    def _on_tree_click(self, event: tk.Event) -> None:
        """Handle click on tree to change status."""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            # Status is column 7 (index 6)
            if column == "#7":
                item = self.tree.identify_row(event.y)
                if item:
                    self._toggle_status(item)
    
    def _toggle_status(self, item_id: str) -> None:
        """Toggle status between Nieuw and Afgehaald."""
        if not item_id or not item_id.startswith("order_"):
            return
        
        try:
            order_id = int(item_id.replace("order_", ""))
            values = self.tree.item(item_id, "values")
            if not values or len(values) < 7:
                return
            
            current_status = values[6] if len(values) > 6 else "Nieuw"
            new_status = "Afgehaald" if current_status == "Nieuw" else "Nieuw"
            
            # Update database
            with DatabaseContext() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE bestellingen SET status = ? WHERE id = ?",
                    (new_status, order_id)
                )
            
            # Update tree display
            new_values = list(values)
            new_values[6] = new_status
            self.tree.item(item_id, values=tuple(new_values))
            
            # Update tags for color
            self.tree.item(item_id, tags=("afhaal", f"status_{new_status.lower()}"))
            
            logger.info(f"Status updated for order {order_id}: {current_status} -> {new_status}")
            
            # Update total (recalculate from all orders in tree)
            self._update_total_from_tree()
            
        except (ValueError, Exception) as e:
            logger.exception(f"Error toggling status: {e}")
            messagebox.showerror("Fout", f"Kon status niet wijzigen: {e}")
    
    def get_afhaal_orders_for_date(self, order_date: date) -> List[Dict]:
        """
        Get all pickup orders for a specific date.
        
        Args:
            order_date: Date to get orders for
            
        Returns:
            List of order dictionaries
        """
        try:
            with DatabaseContext() as conn:
                cursor = conn.cursor()
                # Check if afhaal column exists
                cursor.execute("PRAGMA table_info(bestellingen)")
                columns = [row[1] for row in cursor.fetchall()]
                has_afhaal = 'afhaal' in columns
                
                if has_afhaal:
                    query = """
                        SELECT b.id,
                               b.bonnummer,
                               b.totaal,
                               b.tijd,
                               b.koerier_id,
                               COALESCE(b.status, 'Nieuw') AS status,
                               k.naam AS klant_naam,
                               k.telefoon
                        FROM bestellingen b
                        JOIN klanten k ON b.klant_id = k.id
                        WHERE b.datum = ? AND b.afhaal = 1
                        ORDER BY b.tijd
                    """
                else:
                    # If afhaal column doesn't exist, return empty list
                    # (old database without afhaal support)
                    return []
                
                cursor.execute(query, (order_date.strftime('%Y-%m-%d'),))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.exception(f"Error fetching pickup orders: {e}")
            raise DatabaseError(f"Kon afhaal bestellingen niet ophalen: {e}") from e
    
    def _update_total(self, orders: List[Dict]) -> None:
        """Update the total label with sum of all orders."""
        if not self.total_label:
            return
        
        total = sum(order.get('totaal', 0) for order in orders)
        self.total_label.config(text=f"€{total:.2f}")
    
    def _update_total_from_tree(self) -> None:
        """Update total by recalculating from all items in tree."""
        if not self.total_label or not self.tree:
            return
        
        total = 0.0
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, "values")
            if values and len(values) > 2:
                # Totaal is in column 2 (index 2), format: "€XX.XX"
                totaal_str = values[2]
                try:
                    # Remove € and convert to float
                    totaal_value = float(totaal_str.replace("€", "").replace(",", "."))
                    total += totaal_value
                except (ValueError, AttributeError):
                    continue
        
        self.total_label.config(text=f"€{total:.2f}")
    
    def view_order_details(self, event: Optional[tk.Event] = None) -> None:
        """View details of selected order."""
        selected = self.tree.selection()
        if not selected:
            return
        
        item_id = selected[0]
        values = self.tree.item(item_id, "values")
        
        if not values:
            return
        
        bonnummer = values[1] if len(values) > 1 else "N/A"
        messagebox.showinfo(
            "Bestelling Details",
            f"Bonnummer: {bonnummer}\n\n"
            f"Details kunnen hier worden getoond.\n"
            f"(Implementatie volgt)"
        )


def open_afhaal(parent: tk.Widget) -> None:
    """
    Open the afhaal (pickup) orders management interface.
    
    Args:
        parent: Parent widget (usually a tab frame)
    """
    manager = AfhaalManager(parent)
    return manager

