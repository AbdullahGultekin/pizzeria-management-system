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
        
        self.tree.column("Soort", width=80, anchor=tk.CENTER)
        self.tree.column("Nummer", width=100, anchor=tk.CENTER)
        self.tree.column("Totaal", width=80, anchor=tk.RIGHT)
        self.tree.column("Naam", width=150, anchor=tk.W)
        self.tree.column("Telefoon", width=120, anchor=tk.W)
        self.tree.column("Tijd", width=80, anchor=tk.CENTER)
        self.tree.column("Status", width=100, anchor=tk.CENTER)
        
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
            status = "Klaar" if order.get('koerier_id') else "Wachten"
            
            self.tree.insert(
                "",
                tk.END,
                values=(soort, nummer, totaal, naam, telefoon, tijd, status),
                tags=("afhaal",)
            )
        
        # Configure tag colors
        self.tree.tag_configure("afhaal", background="#FFF9C4")  # Light yellow for pickup orders
    
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

