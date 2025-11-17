"""
Courier Management Module

This module provides the main interface for managing couriers and assigning orders.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from typing import Dict, List, Optional
from database import DatabaseContext
from logging_config import get_logger
from exceptions import DatabaseError
from modules.courier_config import STARTGELD, CARD_COLORS
from modules.courier_service import CourierService
from modules.courier_ui import CourierUI

logger = get_logger("pizzeria.koeriers")


class CourierManager:
    """Main manager class for courier management interface."""
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize courier manager.
        
        Args:
            parent: Parent widget (tab frame)
        """
        self.parent = parent
        self.service = CourierService()
        self.courier_data: Dict[str, int] = {}
        self.courier_names: List[str] = []
        self.ui: Optional[CourierUI] = None
        
        # UI components
        self.paned: Optional[tk.PanedWindow] = None
        self.left_frame: Optional[tk.Frame] = None
        self.right_frame: Optional[tk.Frame] = None
        self.tree: Optional[ttk.Treeview] = None
        self.filter_vars: Dict[str, tk.Variable] = {}
        
        # Variables for totals and calculations
        self.totals_var: Dict[str, tk.DoubleVar] = {}
        self.eind_totals_var: Dict[str, tk.DoubleVar] = {}
        self.extra_km_var: Dict[str, tk.DoubleVar] = {}
        self.extra_uur_var: Dict[str, tk.DoubleVar] = {}
        self.extra_bedrag_var: Dict[str, tk.DoubleVar] = {}
        self.afrekening_var: Dict[str, tk.DoubleVar] = {}
        self.subtotaal_totaal_var: Optional[tk.DoubleVar] = None
        self.totaal_betaald_var: Optional[tk.DoubleVar] = None
        
        # Management UI
        self.new_koerier_entry: Optional[tk.Entry] = None
        self.del_combo: Optional[ttk.Combobox] = None
        self.courier_cards_frame: Optional[tk.Frame] = None
        self.totals_frame: Optional[tk.Frame] = None
    
    def load_couriers(self) -> None:
        """Load couriers from database and initialize variables."""
        try:
            self.courier_data = self.service.get_all_couriers()
            self.courier_names = sorted(list(self.courier_data.keys()), key=str.lower)
            
            # Initialize variables for each courier
            for naam in self.courier_names:
                if naam not in self.totals_var:
                    self.totals_var[naam] = tk.DoubleVar(value=0.0)
                    self.eind_totals_var[naam] = tk.DoubleVar(value=0.0)
                    self.extra_km_var[naam] = tk.DoubleVar(value=0.0)
                    self.extra_uur_var[naam] = tk.DoubleVar(value=0.0)
                    self.extra_bedrag_var[naam] = tk.DoubleVar(value=0.0)
                    self.afrekening_var[naam] = tk.DoubleVar(value=0.0)
            
            # Remove variables for deleted couriers
            for naam in list(self.totals_var.keys()):
                if naam not in self.courier_names:
                    del self.totals_var[naam]
                    del self.eind_totals_var[naam]
                    del self.extra_km_var[naam]
                    del self.extra_uur_var[naam]
                    del self.extra_bedrag_var[naam]
                    del self.afrekening_var[naam]
        except DatabaseError as e:
            logger.exception("Error loading couriers")
            messagebox.showerror("Fout", str(e))
    
    def setup_ui(self) -> None:
        """Setup the main UI."""
        # Clear parent
        for w in self.parent.winfo_children():
            w.destroy()
        
        # Create paned window
        self.paned = tk.PanedWindow(self.parent, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashpad=4)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Create left and right frames
        self.left_frame = tk.Frame(self.paned, padx=10, pady=10)
        self.paned.add(self.left_frame, minsize=400)
        
        self.right_frame = tk.Frame(self.paned, padx=10, pady=10)
        self.paned.add(self.right_frame, minsize=1100)
        
        # Initialize UI helper
        self.ui = CourierUI(self.parent, self.courier_names)
        
        # Setup components
        self.setup_filters()
        self.setup_table()
        self.setup_right_panel()
        
        # Load initial data
        self.load_orders()
    
    def setup_filters(self) -> None:
        """Setup filter bar."""
        self.filter_vars = self.ui.create_filter_bar(
            self.left_frame,
            on_search_change=self.load_orders,
            on_koerier_change=self.load_orders,
            on_date_change=self.load_orders,
            on_reload=lambda: self.load_orders(force=True)
        )
    
    def setup_table(self) -> None:
        """Setup orders table."""
        self.tree = self.ui.create_orders_table(self.left_frame)
        
        # Selection label
        btns = tk.Frame(self.left_frame)
        btns.pack(fill=tk.X, pady=(8, 0))
        geselecteerd_lbl = tk.Label(btns, text="Geen selectie", fg="#666")
        geselecteerd_lbl.pack(side=tk.RIGHT)
        
        def update_selection_label(*_):
            n = len(self.tree.selection())
            geselecteerd_lbl.config(text=f"{n} geselecteerd" if n else "Geen selectie")
        
        self.tree.bind("<<TreeviewSelect>>", update_selection_label)
    
    def setup_right_panel(self) -> None:
        """Setup right panel with courier cards and settlement."""
        tk.Label(self.right_frame, text="Koeriers", font=("Arial", 13, "bold")).pack(anchor="w")
        
        # Courier cards
        self.courier_cards_frame = tk.Frame(self.right_frame)
        self.courier_cards_frame.pack(fill=tk.X)
        self.ui.create_courier_cards(self.courier_cards_frame, self.assign_courier)
        
        # Management frame
        self.setup_management_frame()
        
        # Settlement frame
        self.setup_settlement_frame()
    
    def setup_management_frame(self) -> None:
        """Setup courier management frame."""
        manage_frame = tk.LabelFrame(self.right_frame, text="Koeriers beheren", padx=8, pady=8)
        manage_frame.pack(fill=tk.X, pady=(8, 8))
        
        self.new_koerier_entry = tk.Entry(manage_frame, font=("Arial", 10))
        self.new_koerier_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(
            manage_frame,
            text="Toevoegen",
            command=self.add_courier,
            bg="#D1FFD1"
        ).pack(side=tk.LEFT, padx=6)
        
        del_name_var = tk.StringVar(value=self.courier_names[0] if self.courier_names else "")
        self.del_combo = ttk.Combobox(
            manage_frame,
            values=self.courier_names,
            textvariable=del_name_var,
            width=12,
            state="readonly"
        )
        self.del_combo.pack(side=tk.LEFT, padx=6)
        
        tk.Button(
            manage_frame,
            text="Verwijderen",
            command=lambda: self.delete_courier(del_name_var.get()),
            bg="#FFD1D1"
        ).pack(side=tk.LEFT)
    
    def setup_settlement_frame(self) -> None:
        """Setup settlement frame."""
        self.totals_frame = tk.LabelFrame(
            self.right_frame,
            text="Afrekening per koerier",
            padx=8,
            pady=8,
            bg="#F3F6FC"
        )
        self.totals_frame.pack(fill=tk.X)
        
        # Headers
        headers = [
            "Koerier",
            "Subtotaal (€)",
            f"+ Startgeld (€{STARTGELD:.2f})",
            "Eindtotaal (€)",
            "Km",
            "Uur",
            "Extra €",
            "Definitief (€)"
        ]
        for col, header_text in enumerate(headers):
            tk.Label(
                self.totals_frame,
                text=header_text,
                font=("Arial", 10, "bold"),
                anchor="w",
                bg="#D2F2FF"
            ).grid(row=0, column=col, sticky="we", padx=5, pady=2)
        
        # Rows for each courier
        for i, naam in enumerate(self.courier_names, start=1):
            bg_light, fg_dark = CARD_COLORS[(i - 1) % len(CARD_COLORS)]
            
            tk.Label(
                self.totals_frame,
                text=naam,
                anchor="w",
                bg=bg_light,
                fg=fg_dark,
                font=("Arial", 10, "bold")
            ).grid(row=i, column=0, sticky="we", padx=5)
            
            tk.Label(
                self.totals_frame,
                textvariable=self.totals_var[naam],
                anchor="e",
                bg=bg_light,
                fg=fg_dark,
                font=("Arial", 10)
            ).grid(row=i, column=1, sticky="e", padx=5)
            
            tk.Label(
                self.totals_frame,
                text=f"{STARTGELD:.2f}",
                anchor="e",
                bg=bg_light,
                fg=fg_dark,
                font=("Arial", 10)
            ).grid(row=i, column=2, sticky="e", padx=5)
            
            tk.Label(
                self.totals_frame,
                textvariable=self.eind_totals_var[naam],
                font=("Arial", 10, "bold"),
                anchor="e",
                bg=bg_light,
                fg=fg_dark
            ).grid(row=i, column=3, sticky="e", padx=5)
            
            entry_bg = "#FFFFFF"
            tk.Entry(
                self.totals_frame,
                textvariable=self.extra_km_var[naam],
                font=("Arial", 10, "bold"),
                width=7,
                justify="right",
                bg=entry_bg,
                relief="groove",
                borderwidth=2
            ).grid(row=i, column=4, padx=2)
            
            tk.Entry(
                self.totals_frame,
                textvariable=self.extra_uur_var[naam],
                font=("Arial", 10, "bold"),
                width=5,
                justify="right",
                bg=entry_bg,
                relief="groove",
                borderwidth=2
            ).grid(row=i, column=5, padx=2)
            
            tk.Entry(
                self.totals_frame,
                textvariable=self.extra_bedrag_var[naam],
                font=("Arial", 10, "bold"),
                width=6,
                justify="right",
                bg=entry_bg,
                relief="groove",
                borderwidth=2
            ).grid(row=i, column=6, padx=2)
            
            tk.Label(
                self.totals_frame,
                textvariable=self.afrekening_var[naam],
                font=("Arial", 11, "bold"),
                fg=fg_dark,
                bg=bg_light
            ).grid(row=i, column=7, padx=4, sticky="e")
            
            # Bind recalculation
            def make_recalc(naam_in):
                def recalc(*_):
                    self.recalculate_payment(naam_in)
                    self.recalculate_total_payment()
                return recalc
            
            for var in (
                self.extra_km_var[naam],
                self.extra_uur_var[naam],
                self.extra_bedrag_var[naam],
                self.totals_var[naam],
                self.eind_totals_var[naam]
            ):
                var.trace_add("write", make_recalc(naam))
        
        # Total rows
        subtotal_row = len(self.courier_names) + 1
        self.subtotaal_totaal_var = tk.DoubleVar(value=0)
        tk.Label(
            self.totals_frame,
            text="Totaal Bestellingen",
            font=("Arial", 11, "bold"),
            anchor="e",
            bg="#D2F2FF"
        ).grid(row=subtotal_row, column=0, sticky="ew", padx=5, pady=(8, 4))
        
        tk.Label(
            self.totals_frame,
            textvariable=self.subtotaal_totaal_var,
            font=("Arial", 11, "bold"),
            anchor="e",
            bg="#D2F2FF"
        ).grid(row=subtotal_row, column=1, sticky="ew", padx=5, pady=(8, 4))
        
        total_row = len(self.courier_names) + 2
        self.totaal_betaald_var = tk.DoubleVar(value=0)
        tk.Label(
            self.totals_frame,
            text="Totaal uitbetaling aan koeriers (€):",
            font=("Arial", 12, "bold"),
            fg="#225722",
            bg="#EAFCD5",
            relief="ridge"
        ).grid(row=total_row, column=0, columnspan=6, sticky="e", padx=8, pady=(10, 4))
        
        tk.Label(
            self.totals_frame,
            textvariable=self.totaal_betaald_var,
            font=("Arial", 14, "bold"),
            fg="#268244",
            bg="#EAFCD5",
            relief="ridge"
        ).grid(row=total_row, column=6, columnspan=2, sticky="e", padx=8, pady=(10, 4))
        
        for colindex in range(8):
            self.totals_frame.grid_columnconfigure(colindex, weight=1)
    
    def load_orders(self, force: bool = False) -> None:
        """Load and display orders."""
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
        
        # Get orders
        try:
            orders = self.service.get_orders_for_date(order_date)
        except DatabaseError as e:
            logger.exception("Error loading orders")
            messagebox.showerror("Fout", str(e))
            return
        
        # Get filter values
        search_text = self.filter_vars.get("search", tk.StringVar()).get()
        filter_koerier = self.filter_vars.get("koerier", tk.StringVar(value="Alle")).get()
        
        # Add orders to tree
        for idx, order in enumerate(orders):
            if not force and not self.ui.apply_filters(order, search_text, filter_koerier):
                continue
            
            koerier_naam = order.get('koerier_naam') or ""
            base_tag = "row_a" if idx % 2 == 0 else "row_b"
            
            if koerier_naam:
                tag = f"koerier_{koerier_naam.replace(' ', '_')}"
                tags = (tag,)
            else:
                tags = (base_tag, "unassigned")
            
            koerier_cell = koerier_naam if koerier_naam else "(geen)"
            
            self.tree.insert(
                "",
                tk.END,
                iid=order['id'],
                values=(
                    order['tijd'],
                    order['straat'],
                    order['huisnummer'],
                    order['plaats'],
                    order['telefoon'],
                    f"{order['totaal']:.2f}",
                    koerier_cell
                ),
                tags=tags
            )
        
        # Recalculate totals
        self.recalculate_courier_totals()
        self.recalculate_total_payment()
    
    def recalculate_courier_totals(self) -> None:
        """Recalculate totals for each courier."""
        # Reset totals
        for naam in self.courier_names:
            self.totals_var[naam].set(0.0)
        
        total_orders = 0.0
        
        # Calculate from tree
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, "values")
            try:
                bedrag = float(values[5])
                koerier_naam = values[6]
                total_orders += bedrag
                
                if koerier_naam and koerier_naam != "(geen)" and koerier_naam in self.totals_var:
                    self.totals_var[koerier_naam].set(
                        self.totals_var[koerier_naam].get() + bedrag
                    )
            except (ValueError, IndexError):
                continue
        
        self.subtotaal_totaal_var.set(round(total_orders, 2))
        
        # Calculate final totals
        for naam in self.courier_names:
            subtotal = self.totals_var[naam].get()
            self.eind_totals_var[naam].set(
                self.service.calculate_final_total(subtotal)
            )
    
    def recalculate_payment(self, naam: str) -> None:
        """Recalculate payment for a specific courier."""
        try:
            subtotal = self.totals_var[naam].get()
            km = self.extra_km_var[naam].get()
            uur = self.extra_uur_var[naam].get()
            extra = self.extra_bedrag_var[naam].get()
            
            payment = self.service.calculate_payment(subtotal, km, uur, extra)
            self.afrekening_var[naam].set(payment)
        except Exception:
            self.afrekening_var[naam].set(0.0)
    
    def recalculate_total_payment(self) -> None:
        """Recalculate total payment to all couriers."""
        total = sum(self.afrekening_var[naam].get() for naam in self.courier_names)
        self.totaal_betaald_var.set(round(total, 2))
    
    def add_courier(self) -> None:
        """Add a new courier."""
        naam = self.new_koerier_entry.get().strip()
        if not naam:
            messagebox.showwarning("Invoerfout", "Voer een naam in voor de nieuwe koerier.")
            return
        
        try:
            self.service.add_courier(naam)
            messagebox.showinfo("Succes", f"Koerier '{naam}' is succesvol toegevoegd.")
            self.new_koerier_entry.delete(0, tk.END)
            self.load_couriers()
            self.setup_ui()  # Rebuild UI with new courier
        except DatabaseError as e:
            messagebox.showerror("Fout", str(e))
    
    def delete_courier(self, naam: str) -> None:
        """Delete a courier."""
        if not naam:
            messagebox.showwarning("Selectie", "Kies eerst een koerier om te verwijderen.")
            return
        
        if not messagebox.askyesno("Bevestigen", f"Weet u zeker dat u '{naam}' wilt verwijderen?"):
            return
        
        koerier_id = self.courier_data.get(naam)
        if koerier_id is None:
            messagebox.showerror("Fout", "Koerier niet gevonden in de data.")
            return
        
        try:
            self.service.delete_courier(koerier_id, naam)
            messagebox.showinfo("Succes", f"Koerier '{naam}' is verwijderd.")
            self.load_couriers()
            self.setup_ui()  # Rebuild UI without deleted courier
        except DatabaseError as e:
            messagebox.showerror("Fout", str(e))
    
    def assign_courier(self, naam: str) -> None:
        """Assign selected orders to a courier."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selectie", "Selecteer eerst één of meer rijen.")
            return
        
        koerier_id = self.courier_data.get(naam)
        if koerier_id is None:
            return
        
        try:
            order_ids = [int(item_id) for item_id in selected]
            self.service.assign_courier_to_orders(order_ids, koerier_id)
            self.load_orders(force=True)
        except (ValueError, DatabaseError) as e:
            logger.exception("Error assigning courier")
            messagebox.showerror("Fout", f"Kon koerier niet toewijzen: {e}")
    
    def remove_assignment(self) -> None:
        """Remove courier assignment from selected orders."""
        selected = self.tree.selection()
        if not selected:
            return
        
        try:
            order_ids = [int(item_id) for item_id in selected]
            self.service.remove_courier_from_orders(order_ids)
            self.load_orders(force=True)
        except (ValueError, DatabaseError) as e:
            logger.exception("Error removing assignment")
            messagebox.showerror("Fout", f"Kon toewijzing niet verwijderen: {e}")


def open_koeriers(root: tk.Tk) -> None:
    """
    Open courier management interface.
    
    Args:
        root: Root widget (tab frame)
    """
    manager = CourierManager(root)
    manager.load_couriers()
    manager.setup_ui()
