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
from modules.courier_config import STARTGELD, CARD_COLORS, KM_TARIEF, UUR_TARIEF
from modules.courier_service import CourierService
from modules.courier_ui import CourierUI
import requests

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
        
        # API configuration for online orders
        self.api_base_url = "http://localhost:8000/api/v1"
        self.api_token = None
        self.api_session = requests.Session()
    
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
        """Setup the main UI (matching example layout)."""
        # Clear parent
        for w in self.parent.winfo_children():
            w.destroy()
        
        # Main container
        main_frame = tk.Frame(self.parent, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top section - Action buttons
        top_buttons_frame = tk.Frame(main_frame, bg="white", padx=10, pady=5)
        top_buttons_frame.pack(fill=tk.X)
        
        tk.Button(
            top_buttons_frame,
            text="Totalen afdrukken",
            command=self.print_totals,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            top_buttons_frame,
            text="Routebeschrijving",
            command=self.show_route_for_selected,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Filter checkbox for orders without courier
        if not hasattr(self, 'filter_without_courier'):
            self.filter_without_courier = tk.BooleanVar(value=False)
        filter_checkbox = tk.Checkbutton(
            top_buttons_frame,
            text="Alleen zonder koerier",
            variable=self.filter_without_courier,
            command=lambda: self.load_orders(force=True),
            bg="white",
            font=("Arial", 9),
            padx=10
        )
        filter_checkbox.pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Button(
            top_buttons_frame,
            text="Vernieuwen",
            command=lambda: self.load_orders(force=True),
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT)
        
        # Main content area - Split into table and settlement
        content_paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashpad=2)
        content_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Table
        left_panel = tk.Frame(content_paned, bg="white")
        content_paned.add(left_panel, minsize=500, width=600)
        
        # Right panel - Settlement frame
        right_panel = tk.Frame(content_paned, bg="white")
        content_paned.add(right_panel, minsize=400, width=500)
        
        # Initialize UI helper
        self.ui = CourierUI(self.parent, self.courier_names)
        
        # Setup table with new columns
        self.setup_table_new(left_panel)
        
        # Setup settlement frame (right panel)
        self.right_frame = right_panel
        self.setup_settlement_frame()
        
        # Bottom section - Courier buttons
        courier_buttons_frame = tk.Frame(main_frame, bg="white", padx=10, pady=10)
        courier_buttons_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Label(
            courier_buttons_frame,
            text="Koeriers:",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#333"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Courier buttons in a horizontal row
        for naam in self.courier_names:
            btn = tk.Button(
                courier_buttons_frame,
                text=naam,
                command=lambda n=naam: self.assign_courier(n),
                bg="#4CAF50",
                fg="white",
                font=("Arial", 10, "bold"),
                padx=12,
                pady=6,
                relief=tk.RAISED,
                borderwidth=2
            )
            btn.pack(side=tk.LEFT, padx=3)
        
        # Store reference to courier buttons frame for updates
        self.courier_buttons_frame = courier_buttons_frame
        
        # Load initial data
        self.load_orders()
    
    def setup_courier_buttons(self) -> None:
        """Setup/update courier buttons in bottom frame."""
        if not hasattr(self, 'courier_buttons_frame'):
            return
        
        # Clear existing buttons (except label)
        for widget in self.courier_buttons_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()
        
        # Add buttons for each courier
        for naam in self.courier_names:
            btn = tk.Button(
                self.courier_buttons_frame,
                text=naam,
                command=lambda n=naam: self.assign_courier(n),
                bg="#4CAF50",
                fg="white",
                font=("Arial", 10, "bold"),
                padx=12,
                pady=6,
                relief=tk.RAISED,
                borderwidth=2
            )
            btn.pack(side=tk.LEFT, padx=3)
    
    def print_totals(self) -> None:
        """Print totals for all couriers."""
        if not hasattr(self, 'totals_var') or not self.totals_var:
            messagebox.showwarning("Geen data", "Geen koerier data beschikbaar om af te drukken.")
            return
        
        try:
            from datetime import datetime
            import sys
            import os
            
            # Try to import win32print for Windows
            try:
                import win32print
                WIN32PRINT_AVAILABLE = True
            except ImportError:
                WIN32PRINT_AVAILABLE = False
            
            if not WIN32PRINT_AVAILABLE:
                messagebox.showwarning(
                    "Platform Error",
                    "Windows printer support niet beschikbaar.\n\n"
                    "De afrekening kan niet worden afgedrukt op dit platform."
                )
                return
            
            # Load printer settings
            try:
                import json
                settings_file = "settings.json"
                if os.path.exists(settings_file):
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        app_settings = json.load(f)
                else:
                    app_settings = {}
                
                printer_name = app_settings.get("thermal_printer_name", "Default")
                
                if not printer_name or printer_name == "Default":
                    messagebox.showwarning(
                        "Printer niet geconfigureerd",
                        "Er is geen printer geconfigureerd.\n\n"
                        "Ga naar Instellingen > Printer Instellingen om een printer te selecteren."
                    )
                    return
            except Exception as e:
                logger.error(f"Error loading printer settings: {e}")
                messagebox.showerror("Fout", f"Kon printer instellingen niet laden: {e}")
                return
            
            # Build settlement report text
            lines = []
            lines.append("=" * 50)
            lines.append("AFREKENING KOERIERS")
            lines.append("=" * 50)
            lines.append(f"Datum: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            lines.append("")
            lines.append("-" * 50)
            
            # Header
            lines.append(f"{'Koerier':<20} {'Subtotaal':>10} {'Startgeld':>10} {'Eindtotaal':>12} {'Km':>6} {'Uur':>6} {'Extra':>8} {'Totaal':>10}")
            lines.append("-" * 50)
            
            total_payment = 0.0
            total_orders = 0.0
            
            # Data for each courier
            for naam in self.courier_names:
                if naam not in self.totals_var:
                    continue
                
                subtotal = self.totals_var[naam].get()
                eindtotaal = self.eind_totals_var[naam].get() if naam in self.eind_totals_var else subtotal + STARTGELD
                km = self.extra_km_var[naam].get() if naam in self.extra_km_var else 0.0
                uur = self.extra_uur_var[naam].get() if naam in self.extra_uur_var else 0.0
                extra = self.extra_bedrag_var[naam].get() if naam in self.extra_bedrag_var else 0.0
                afrekening = self.afrekening_var[naam].get() if naam in self.afrekening_var else 0.0
                
                total_orders += subtotal
                total_payment += afrekening
                
                lines.append(
                    f"{naam[:18]:<20} "
                    f"{subtotal:>10.2f} "
                    f"{STARTGELD:>10.2f} "
                    f"{eindtotaal:>12.2f} "
                    f"{km:>6.1f} "
                    f"{uur:>6.1f} "
                    f"{extra:>8.2f} "
                    f"{afrekening:>10.2f}"
                )
            
            lines.append("-" * 50)
            lines.append(f"{'TOTAAL BESTELLINGEN':<20} {total_orders:>10.2f}")
            lines.append(f"{'TOTAAL UITBETALING':<20} {total_payment:>10.2f}")
            lines.append("=" * 50)
            lines.append("")
            lines.append(f"Tarief per km: €{KM_TARIEF:.2f}")
            lines.append(f"Tarief per uur: €{UUR_TARIEF:.2f}")
            lines.append(f"Startgeld per koerier: €{STARTGELD:.2f}")
            
            # Print the report using win32print
            report_text = "\n".join(lines)
            
            try:
                hprinter = win32print.OpenPrinter(printer_name)
                try:
                    hjob = win32print.StartDocPrinter(hprinter, 1, ("Afrekening Koeriers", None, "RAW"))
                    win32print.StartPagePrinter(hprinter)
                    
                    # Print report text
                    for line in report_text.split('\n'):
                        try:
                            encoded = line.encode('cp858', errors='replace')
                            win32print.WritePrinter(hprinter, encoded)
                            win32print.WritePrinter(hprinter, b'\n')
                        except Exception as e:
                            logger.warning(f"Error encoding line: {e}")
                    
                    win32print.WritePrinter(hprinter, b'\n\n\n')
                    win32print.EndPagePrinter(hprinter)
                    win32print.EndDocPrinter(hprinter)
                    
                    logger.info(f"Courier totals printed successfully to {printer_name}")
                    messagebox.showinfo("Succes", "Totalen zijn afgedrukt.")
                finally:
                    win32print.ClosePrinter(hprinter)
            except Exception as e:
                logger.exception(f"Error printing to {printer_name}: {e}")
                messagebox.showerror("Fout", f"Kon niet afdrukken naar {printer_name}: {e}")
            
        except Exception as e:
            logger.exception("Error printing totals")
            messagebox.showerror("Fout", f"Kon totalen niet afdrukken: {e}")
    
    def show_route_for_selected(self) -> None:
        """Show route for selected order."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selectie", "Selecteer eerst een bestelling.")
            return
        
        # Get first selected order
        item_id = selected[0]
        values = self.tree.item(item_id, "values")
        
        # Build address from values (postcode column removed, indices shifted)
        straat = values[3] if len(values) > 3 else ""
        huis_nr = values[4] if len(values) > 4 else ""
        gemeente = values[5] if len(values) > 5 else ""
        
        address = f"{straat} {huis_nr}, {gemeente}".strip()
        
        if address:
            import webbrowser
            google_maps_url = f"https://www.google.com/maps/dir/?api=1&destination={address.replace(' ', '+')}"
            webbrowser.open(google_maps_url)
        else:
            messagebox.showwarning("Adres ontbreekt", "Geen adres beschikbaar voor deze bestelling.")
    
    def setup_filters(self) -> None:
        """Setup filter bar (not used in new layout)."""
        # Initialize filter vars for compatibility
        self.filter_vars = {
            "search": tk.StringVar(),
            "koerier": tk.StringVar(value="Alle"),
            "datum": tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        }
    
    def setup_table(self) -> None:
        """Setup orders table (old method - kept for compatibility)."""
        pass
    
    def setup_table_new(self, parent: tk.Widget) -> None:
        """Setup orders table with new columns matching example."""
        # Define columns - removed postcode, added koerier
        columns = ("soort", "nummer", "totaal", "straat", "huis_nr", "gemeente", "tijd", "vertrek", "betaalmethode", "koerier")
        headers = {
            "soort": "Soort",
            "nummer": "Nummer",
            "totaal": "Totaal",
            "straat": "Straat",
            "huis_nr": "Huis nr.",
            "gemeente": "Gemeente",
            "tijd": "Tijd",
            "vertrek": "Vertrek",
            "betaalmethode": "Betaalmethode",
            "koerier": "Koerier"
        }
        widths = {
            "soort": 80,
            "nummer": 60,
            "totaal": 80,
            "straat": 150,
            "huis_nr": 70,
            "gemeente": 150,
            "tijd": 70,
            "vertrek": 70,
            "betaalmethode": 120,
            "koerier": 120
        }
        
        # Create Treeview
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=headers[col])
            anchor = "e" if col in ("totaal", "nummer") else ("center" if col in ("tijd", "vertrek") else "w")
            self.tree.column(col, width=widths[col], anchor=anchor)
        
        # Store column indices for reference
        self.column_indices = {col: idx for idx, col in enumerate(columns)}
        
        # Scrollbar
        scroll_y = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure styles
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        self.tree.tag_configure("row_a", background="#F5F5F5")
        self.tree.tag_configure("row_b", background="white")
        self.tree.tag_configure("online", background="#E3F2FD")  # Light blue for online orders
        self.tree.tag_configure("selected", background="#B3E5FC", foreground="#0D47A1")
        
        # Configure courier-specific row colors
        for i, naam in enumerate(self.courier_names):
            tag = f"koerier_{naam.replace(' ', '_')}"
            bg_color = CARD_COLORS[i % len(CARD_COLORS)][0]
            self.tree.tag_configure(tag, background=bg_color)
    
    def setup_right_panel(self) -> None:
        """Setup right panel (not used in new layout)."""
        pass
    
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
        # Scrollable frame for settlement
        settlement_canvas = tk.Canvas(self.right_frame, bg="white", highlightthickness=0)
        settlement_scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=settlement_canvas.yview)
        settlement_inner = tk.Frame(settlement_canvas, bg="white")
        
        settlement_canvas_window = settlement_canvas.create_window((0, 0), window=settlement_inner, anchor="nw")
        settlement_canvas.configure(yscrollcommand=settlement_scrollbar.set)
        
        def _on_canvas_configure(event):
            canvas_width = event.width
            settlement_canvas.itemconfig(settlement_canvas_window, width=canvas_width)
        
        def _on_frame_configure(event):
            settlement_canvas.configure(scrollregion=settlement_canvas.bbox("all"))
        
        settlement_canvas.bind('<Configure>', _on_canvas_configure)
        settlement_inner.bind('<Configure>', _on_frame_configure)
        
        settlement_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        settlement_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.totals_frame = tk.LabelFrame(
            settlement_inner,
            text="Afrekening per koerier",
            padx=8,
            pady=8,
            bg="#F3F6FC"
        )
        self.totals_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
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
            
            # Subtotal label with formatting
            subtotal_label = tk.Label(
                self.totals_frame,
                text="0.00",
                anchor="e",
                bg=bg_light,
                fg=fg_dark,
                font=("Arial", 10)
            )
            subtotal_label.grid(row=i, column=1, sticky="e", padx=5)
            # Update label when variable changes
            def update_subtotal(*args, var=self.totals_var[naam], label=subtotal_label):
                val = var.get()
                label.config(text=f"{val:.2f}")
            self.totals_var[naam].trace_add("write", update_subtotal)
            update_subtotal()  # Initial update
            
            tk.Label(
                self.totals_frame,
                text=f"{STARTGELD:.2f}",
                anchor="e",
                bg=bg_light,
                fg=fg_dark,
                font=("Arial", 10)
            ).grid(row=i, column=2, sticky="e", padx=5)
            
            # Eindtotaal label with formatting
            eindtotaal_label = tk.Label(
                self.totals_frame,
                text="0.00",
                font=("Arial", 10, "bold"),
                anchor="e",
                bg=bg_light,
                fg=fg_dark
            )
            eindtotaal_label.grid(row=i, column=3, sticky="e", padx=5)
            # Update label when variable changes
            def update_eindtotaal(*args, var=self.eind_totals_var[naam], label=eindtotaal_label):
                val = var.get()
                label.config(text=f"{val:.2f}")
            self.eind_totals_var[naam].trace_add("write", update_eindtotaal)
            update_eindtotaal()  # Initial update
            
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
            
            # Afrekening label with formatting
            afrekening_label = tk.Label(
                self.totals_frame,
                text="0.00",
                font=("Arial", 11, "bold"),
                fg=fg_dark,
                bg=bg_light
            )
            afrekening_label.grid(row=i, column=7, padx=4, sticky="e")
            # Update label when variable changes
            def update_afrekening(*args, var=self.afrekening_var[naam], label=afrekening_label):
                val = var.get()
                label.config(text=f"{val:.2f}")
            self.afrekening_var[naam].trace_add("write", update_afrekening)
            update_afrekening()  # Initial update
            
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
        
        # Get orders (exclude afhaal orders, only delivery orders)
        try:
            # Check if filter for "only without courier" is active
            filter_var = getattr(self, 'filter_without_courier', None)
            if isinstance(filter_var, tk.BooleanVar):
                only_without_courier = filter_var.get()
            else:
                only_without_courier = False
            
            orders = self.service.get_orders_for_date(
                order_date, 
                exclude_afhaal=True,  # Only show delivery orders
                only_without_courier=only_without_courier
            )
        except DatabaseError as e:
            logger.exception("Error loading orders")
            messagebox.showerror("Fout", str(e))
            return
        
        # Get online orders from API
        online_orders = self.fetch_online_orders(order_date)
        if online_orders:
            # Convert online orders to same format as local orders
            for online_order in online_orders:
                # Parse address
                klant_adres = online_order.get('klant_adres', '')
                straat = ''
                huisnummer = ''
                plaats = ''
                if klant_adres:
                    # Format: "Straat Huisnummer, Postcode Gemeente"
                    parts = klant_adres.split(',')
                    if len(parts) >= 1:
                        address_part = parts[0].strip()
                        address_words = address_part.split()
                        if len(address_words) > 1:
                            straat = ' '.join(address_words[:-1])
                            huisnummer = address_words[-1]
                    if len(parts) >= 2:
                        plaats = parts[1].strip()
                
                # Convert to same format as local orders
                order_dict = {
                    'id': f"online_{online_order['id']}",  # Prefix to distinguish
                    'tijd': online_order.get('tijd', ''),
                    'straat': straat,
                    'huisnummer': huisnummer,
                    'plaats': plaats,
                    'telefoon': online_order.get('klant_telefoon', ''),
                    'totaal': online_order.get('totaal', 0),
                    'koerier_naam': self.get_courier_name_by_id(online_order.get('koerier_id')),
                    'online': True  # Mark as online order
                }
                orders.append(order_dict)
        
        # Cache online orders data for lookups
        online_orders_cache = {}
        for oo in self.fetch_online_orders(order_date):
            online_orders_cache[oo['id']] = oo
        
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
            
            # Mark online orders with special tag
            if order.get('online'):
                tags = tags + ("online",)
            
            # Determine order number and type
            if order.get('online'):
                soort = "Online"
                nummer = str(order['id']).replace("online_", "")
                # Get online order data from cache
                online_order_data = online_orders_cache.get(int(nummer))
            else:
                soort = "Kassa"
                nummer = str(order.get('id', ''))
                online_order_data = None
            
            # Get betaalmethode for online orders
            betaalmethode = "Cash"
            if online_order_data:
                betaalmethode_raw = online_order_data.get('betaalmethode', 'cash')
                if betaalmethode_raw == 'online':
                    betaalmethode = "Bancontact/M.."
                else:
                    betaalmethode = "Cash"
            
            # Parse plaats to get gemeente (only gemeente, no postcode)
            gemeente = ""
            plaats = order.get('plaats', '')
            if plaats:
                plaats_parts = plaats.split()
                if len(plaats_parts) > 1:
                    # Skip first part (postcode), take rest as gemeente
                    gemeente = ' '.join(plaats_parts[1:])
                else:
                    # If no postcode, use whole string as gemeente
                    gemeente = plaats
            
            # Get vertrek time (levertijd for online orders, or empty for local)
            vertrek = ""
            if online_order_data:
                vertrek = online_order_data.get('levertijd', '')
            
            # Format totaal
            totaal_str = f"€ {order['totaal']:,.2f}".replace(',', ' ').replace('.', ',')
            
            # Get koerier name (already extracted above)
            koerier_display = koerier_naam if koerier_naam else ""
            
            self.tree.insert(
                "",
                tk.END,
                iid=order['id'],
                values=(
                    soort,
                    nummer,
                    totaal_str,
                    order.get('straat', ''),
                    order.get('huisnummer', ''),
                    gemeente,
                    order.get('tijd', ''),
                    vertrek,
                    betaalmethode,
                    koerier_display
                ),
                tags=tags
            )
        
        # Recalculate totals (if settlement frame exists)
        if hasattr(self, 'totals_var') and self.totals_var:
            self.recalculate_courier_totals()
            self.recalculate_total_payment()
    
    def recalculate_courier_totals(self) -> None:
        """Recalculate totals for each courier."""
        if not hasattr(self, 'totals_var') or not self.totals_var:
            return
            
        # Reset totals
        for naam in self.courier_names:
            self.totals_var[naam].set(0.0)
        
        total_orders = 0.0
        
        # Get date for filtering
        datum_str = self.filter_vars.get("datum", tk.StringVar(value=date.today().strftime('%Y-%m-%d'))).get()
        try:
            order_date = datetime.strptime(datum_str, '%Y-%m-%d').date()
        except ValueError:
            order_date = date.today()
        
        # Get local orders from database (exclude afhaal orders)
        try:
            local_orders = self.service.get_orders_for_date(order_date, exclude_afhaal=True)
            # Group by courier
            courier_totals = {naam: 0.0 for naam in self.courier_names}
            
            for order in local_orders:
                koerier_naam = order.get('koerier_naam')
                if koerier_naam and koerier_naam in courier_totals:
                    courier_totals[koerier_naam] += float(order.get('totaal', 0))
                    total_orders += float(order.get('totaal', 0))
        except Exception as e:
            logger.warning(f"Error calculating local order totals: {e}")
        
        # Get online orders from API
        try:
            online_orders = self.fetch_online_orders(order_date)
            for online_order in online_orders:
                koerier_id = online_order.get('koerier_id')
                if koerier_id:
                    koerier_naam = self.get_courier_name_by_id(koerier_id)
                    if koerier_naam and koerier_naam in courier_totals:
                        courier_totals[koerier_naam] += float(online_order.get('totaal', 0))
                        total_orders += float(online_order.get('totaal', 0))
        except Exception as e:
            logger.warning(f"Error calculating online order totals: {e}")
        
        # Update totals variables
        for naam, totaal in courier_totals.items():
            if naam in self.totals_var:
                self.totals_var[naam].set(round(totaal, 2))
        
        if hasattr(self, 'subtotaal_totaal_var') and self.subtotaal_totaal_var:
            self.subtotaal_totaal_var.set(round(total_orders, 2))
        
        # Calculate final totals and payments
        for naam in self.courier_names:
            if naam in self.totals_var:
                subtotal = self.totals_var[naam].get()
                if hasattr(self, 'eind_totals_var') and naam in self.eind_totals_var:
                    self.eind_totals_var[naam].set(
                        self.service.calculate_final_total(subtotal)
                    )
                # Recalculate payment
                self.recalculate_payment(naam)
        
        # Recalculate total payment
        self.recalculate_total_payment()
    
    def recalculate_payment(self, naam: str) -> None:
        """Recalculate payment for a specific courier."""
        if not hasattr(self, 'totals_var') or naam not in self.totals_var:
            return
        try:
            subtotal = self.totals_var[naam].get()
            km = self.extra_km_var[naam].get() if hasattr(self, 'extra_km_var') and naam in self.extra_km_var else 0.0
            uur = self.extra_uur_var[naam].get() if hasattr(self, 'extra_uur_var') and naam in self.extra_uur_var else 0.0
            extra = self.extra_bedrag_var[naam].get() if hasattr(self, 'extra_bedrag_var') and naam in self.extra_bedrag_var else 0.0
            
            payment = self.service.calculate_payment(subtotal, km, uur, extra)
            if hasattr(self, 'afrekening_var') and naam in self.afrekening_var:
                self.afrekening_var[naam].set(payment)
        except Exception:
            if hasattr(self, 'afrekening_var') and naam in self.afrekening_var:
                self.afrekening_var[naam].set(0.0)
    
    def recalculate_total_payment(self) -> None:
        """Recalculate total payment to all couriers."""
        if not hasattr(self, 'afrekening_var'):
            return
        total = sum(self.afrekening_var[naam].get() for naam in self.courier_names if naam in self.afrekening_var)
        if hasattr(self, 'totaal_betaald_var') and self.totaal_betaald_var:
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
            # Recreate courier buttons
            self.setup_courier_buttons()
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
            # Recreate courier buttons
            self.setup_courier_buttons()
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
            # Separate online and local orders
            online_order_ids = []
            local_order_ids = []
            
            for item_id in selected:
                if isinstance(item_id, str) and item_id.startswith("online_"):
                    # Online order
                    order_id = int(item_id.replace("online_", ""))
                    online_order_ids.append(order_id)
                else:
                    # Local order
                    local_order_ids.append(int(item_id))
            
            # Assign local orders
            if local_order_ids:
                self.service.assign_courier_to_orders(local_order_ids, koerier_id)
            
            # Assign online orders via API
            if online_order_ids:
                self.assign_online_orders(online_order_ids, koerier_id)
            
            self.load_orders(force=True)
        except (ValueError, DatabaseError) as e:
            logger.exception("Error assigning courier")
            messagebox.showerror("Fout", f"Kon koerier niet toewijzen: {e}")
    
    def fetch_online_orders(self, order_date: date) -> List[Dict]:
        """Fetch online orders from API for a specific date."""
        try:
            # Authenticate if needed
            if not self.api_token:
                self.authenticate_api()
            
            if not self.api_token:
                return []
            
            # Fetch all pending online orders
            response = self.api_session.get(
                f"{self.api_base_url}/orders/online/pending"
            )
            
            if response.status_code == 200:
                orders = response.json()
                # Filter by date
                filtered_orders = []
                for order in orders:
                    order_datum = order.get('datum', '')
                    if order_datum == order_date.strftime('%Y-%m-%d'):
                        filtered_orders.append(order)
                return filtered_orders
            elif response.status_code == 401:
                # Re-authenticate
                if self.authenticate_api():
                    response = self.api_session.get(
                        f"{self.api_base_url}/orders/online/pending"
                    )
                    if response.status_code == 200:
                        orders = response.json()
                        filtered_orders = []
                        for order in orders:
                            order_datum = order.get('datum', '')
                            if order_datum == order_date.strftime('%Y-%m-%d'):
                                filtered_orders.append(order)
                        return filtered_orders
            return []
        except Exception as e:
            logger.error(f"Error fetching online orders: {e}")
            return []
    
    def authenticate_api(self) -> bool:
        """Authenticate with the API and get token."""
        try:
            response = self.api_session.post(
                f"{self.api_base_url}/auth/login",
                data={
                    "username": "admin",
                    "password": "admin123"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
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
            return False
        except Exception as e:
            logger.error(f"Error authenticating with API: {e}")
            return False
    
    def assign_online_orders(self, order_ids: List[int], koerier_id: int) -> None:
        """Assign online orders to a courier via API."""
        try:
            for order_id in order_ids:
                response = self.api_session.put(
                    f"{self.api_base_url}/orders/{order_id}/status",
                    json={
                        "new_status": "Onderweg",  # Set status to Onderweg when assigning courier
                        "koerier_id": koerier_id
                    }
                )
                if response.status_code != 200:
                    logger.warning(f"Failed to assign courier to online order {order_id}: {response.status_code}")
        except Exception as e:
            logger.error(f"Error assigning online orders: {e}")
            raise
    
    def get_courier_name_by_id(self, koerier_id: Optional[int]) -> Optional[str]:
        """Get courier name by ID."""
        if koerier_id is None:
            return None
        for naam, cid in self.courier_data.items():
            if cid == koerier_id:
                return naam
        return None
    
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
