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
        
        # Main content area - Split into table and settlement (50/50 split)
        content_paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashpad=2)
        content_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Table (50% of width)
        left_panel = tk.Frame(content_paned, bg="white")
        # Use same minsize and width for 50/50 split
        content_paned.add(left_panel, minsize=700, width=700)
        
        # Right panel - Settlement frame (50% of width)
        right_panel = tk.Frame(content_paned, bg="white")
        # Use same minsize and width for 50/50 split
        content_paned.add(right_panel, minsize=700, width=700)
        
        # Initialize UI helper
        self.ui = CourierUI(self.parent, self.courier_names)
        
        # Setup table with new columns
        self.setup_table_new(left_panel)
        
        # Setup right panel structure
        self.right_frame = right_panel
        
        # Setup management frame first (for adding/removing couriers) - at the top
        self.setup_management_frame()
        
        # Then setup settlement frame below management frame
        self.setup_settlement_frame()
        
        # Courier cards section - right panel, below settlement table
        self.setup_courier_cards()
        
        # Load initial data
        self.load_orders()
    
    def setup_courier_cards(self) -> None:
        """Setup courier cards with totals in right panel (below settlement table)."""
        # Container for courier cards
        cards_container = tk.LabelFrame(self.right_frame, text="Koeriers", font=("Arial", 11, "bold"), padx=8, pady=8)
        cards_container.pack(fill=tk.BOTH, expand=False, pady=(10, 0))
        
        # Frame for cards grid
        self.courier_cards_frame = tk.Frame(cards_container, bg="white")
        self.courier_cards_frame.pack(fill=tk.BOTH, expand=True)
        
        # Render cards
        self.render_courier_cards()
    
    def initials(self, name: str) -> str:
        """Get initials from name."""
        parts = [p for p in name.split() if p.strip()]
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()
    
    def render_courier_cards(self) -> None:
        """Render courier cards with totals."""
        # Clear existing cards
        for widget in self.courier_cards_frame.winfo_children():
            widget.destroy()
        
        # Configure grid columns
        self.courier_cards_frame.grid_columnconfigure(0, weight=1)
        self.courier_cards_frame.grid_columnconfigure(1, weight=1)
        
        # Create cards for each courier
        for i, naam in enumerate(self.courier_names):
            bg, fg = CARD_COLORS[i % len(CARD_COLORS)]
            
            # Card frame
            card = tk.Frame(
                self.courier_cards_frame,
                bd=1,
                relief="groove",
                padx=10,
                pady=8,
                bg=bg,
                highlightthickness=0
            )
            card.grid(row=i // 2, column=i % 2, padx=6, pady=6, sticky="ew")
            card.grid_columnconfigure(1, weight=1)
            
            # Avatar with initials
            avatar = tk.Canvas(card, width=34, height=34, bg=bg, highlightthickness=0)
            avatar.grid(row=0, column=0, rowspan=2, padx=(0, 8))
            avatar.create_oval(2, 2, 32, 32, fill=fg, outline=fg)
            avatar.create_text(17, 17, text=self.initials(naam), fill=bg, font=("Arial", 10, "bold"))
            
            # Name label
            name_lbl = tk.Label(
                card,
                text=naam,
                font=("Arial", 11, "bold"),
                bg=bg,
                fg=fg,
                anchor="w",
                wraplength=180
            )
            name_lbl.grid(row=0, column=1, sticky="w")
            
            # Total label (shows subtotal from totals_var with formatting)
            if naam in self.totals_var:
                total_lbl = tk.Label(
                    card,
                    text="€0.00",
                    font=("Arial", 10, "bold"),
                    fg=fg,
                    bg=bg
                )
                # Update label when variable changes
                def update_total(*args, var=self.totals_var[naam], label=total_lbl):
                    try:
                        if label.winfo_exists():
                            val = var.get()
                            label.config(text=f"€{val:.2f}")
                    except tk.TclError:
                        pass  # Widget destroyed, ignore
                self.totals_var[naam].trace_add("write", update_total)
                update_total()  # Initial update
            else:
                # Fallback if variable doesn't exist yet
                total_lbl = tk.Label(
                    card,
                    text="€0.00",
                    font=("Arial", 10, "bold"),
                    fg=fg,
                    bg=bg
                )
            total_lbl.grid(row=1, column=1, sticky="w")
            
            # Assign button
            btn = tk.Button(
                card,
                text="Wijs selectie toe",
                command=lambda n=naam: self.assign_courier(n),
                bg="#FFFFFF",
                fg=fg,
                font=("Arial", 10, "bold"),
                relief="raised",
                bd=1,
                activebackground="#F5F5F5"
            )
            btn.grid(row=0, column=2, rowspan=2, padx=(8, 0))
            
            # Hover effects
            def on_enter(e, b=btn):
                b.configure(bg="#F5F5F5")
            
            def on_leave(e, b=btn):
                b.configure(bg="#FFFFFF")
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
    
    def _refresh_courier_ui(self) -> None:
        """Refresh only necessary UI parts after courier changes (faster than full rebuild)."""
        # Update courier cards
        self.render_courier_cards()
        
        # Rebuild settlement frame with new courier variables
        if hasattr(self, 'right_frame') and self.right_frame:
            # Find and clear settlement frame (but keep management frame)
            for widget in self.right_frame.winfo_children():
                if isinstance(widget, tk.Frame) and widget != getattr(self, '_management_frame', None):
                    # Check if it's the settlement container
                    try:
                        if widget.winfo_exists():
                            widget.destroy()
                    except tk.TclError:
                        pass
            
            # Rebuild settlement frame
            self.setup_settlement_frame()
        
        # Reload orders to refresh display
        self.load_orders(force=True)
    
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
        """Setup orders table with optimized columns for courier assignment."""
        # Define columns - removed postcode and betaalmethode, added telefoon and koerier
        columns = ("soort", "nummer", "totaal", "straat", "huis_nr", "gemeente", "telefoon", "tijd", "vertrek", "koerier")
        headers = {
            "soort": "Soort",
            "nummer": "Nummer",
            "totaal": "Totaal",
            "straat": "Straat",
            "huis_nr": "Huis nr.",
            "gemeente": "Gemeente",
            "telefoon": "Telefoon",
            "tijd": "Tijd",
            "vertrek": "Vertrek",
            "koerier": "Koerier"
        }
        widths = {
            "soort": 40,      # Verkleind voor compactheid
            "nummer": 40,     # Iets groter voor volledige nummers
            "totaal": 40,      # Iets kleiner
            "straat": 150,     # Groter voor volledige straatnamen
            "huis_nr": 30,     # Iets kleiner
            "gemeente": 100,   # Iets kleiner maar nog leesbaar
            "telefoon": 100,   # Telefoonnummer kolom
            "tijd": 35,        # Iets kleiner
            "vertrek": 35,     # Iets kleiner
            "koerier": 80     # Groter zodat volledige koeriernaam zichtbaar is
        }
        
        # Create Treeview with optimized height for better visibility
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=20)
        
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
        
        # Configure courier-specific row colors - full row coloring across all columns
        for i, naam in enumerate(self.courier_names):
            tag = f"koerier_{naam.replace(' ', '_')}"
            bg_color = CARD_COLORS[i % len(CARD_COLORS)][0]
            # Get foreground color for better contrast
            fg_color = CARD_COLORS[i % len(CARD_COLORS)][1] if len(CARD_COLORS[i % len(CARD_COLORS)]) > 1 else "#000000"
            
            # Configure tag to apply background color to entire row (all columns)
            # In Tkinter Treeview, tag_configure automatically applies to the entire row
            self.tree.tag_configure(
                tag,
                background=bg_color,
                foreground=fg_color
            )
    
    def setup_right_panel(self) -> None:
        """Setup right panel (not used in new layout)."""
        pass
    
    def setup_management_frame(self) -> None:
        """Setup courier management frame."""
        manage_frame = tk.LabelFrame(self.right_frame, text="Koeriers beheren", padx=8, pady=8)
        manage_frame.pack(fill=tk.X, pady=(8, 8))
        self._management_frame = manage_frame  # Store reference for refresh
        
        # Entry for new courier name
        self.new_koerier_entry = tk.Entry(manage_frame, font=("Arial", 10))
        self.new_koerier_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        
        # Button to add courier
        tk.Button(
            manage_frame,
            text="Toevoegen",
            command=self.add_courier,
            bg="#D1FFD1",
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=3)
        
        # Combobox for selecting courier to delete
        self.del_name_var = tk.StringVar(value=self.courier_names[0] if self.courier_names else "")
        self.del_combo = ttk.Combobox(
            manage_frame,
            values=self.courier_names,
            textvariable=self.del_name_var,
            width=15,
            state="readonly",
            font=("Arial", 9)
        )
        self.del_combo.pack(side=tk.LEFT, padx=6)
        
        # Button to delete courier
        tk.Button(
            manage_frame,
            text="Verwijderen",
            command=lambda: self.delete_courier(self.del_name_var.get()),
            bg="#FFD1D1",
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=3)
    
    def setup_settlement_frame(self) -> None:
        """Setup settlement frame."""
        # Container frame for settlement (below management frame)
        settlement_container = tk.Frame(self.right_frame, bg="white")
        settlement_container.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        # Scrollable frame for settlement
        settlement_canvas = tk.Canvas(settlement_container, bg="white", highlightthickness=0)
        settlement_scrollbar = ttk.Scrollbar(settlement_container, orient="vertical", command=settlement_canvas.yview)
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
        # Configure column widths for better visibility
        column_configs = [
            ("Koerier", 90),           # Koerier naam
            ("Subtotaal (€)", 100),    # Subtotaal
            (f"+ Startgeld (€{STARTGELD:.2f})", 120),  # Startgeld
            ("Eindtotaal (€)", 100),   # Eindtotaal
            ("Km", 60),                # Kilometers
            ("Uur", 50),               # Uren
            ("Extra €", 70),           # Extra bedrag
            ("Definitief (€)", 100)    # Definitief totaal
        ]
        
        for col, (header_text, min_width) in enumerate(column_configs):
            label = tk.Label(
                self.totals_frame,
                text=header_text,
                font=("Arial", 9, "bold"),  # Iets kleiner font voor compactheid
                anchor="w",
                bg="#D2F2FF"
            )
            label.grid(row=0, column=col, sticky="we", padx=3, pady=2)
            # Set minimum width for column
            self.totals_frame.grid_columnconfigure(col, minsize=min_width, weight=1)
        
        # Rows for each courier
        for i, naam in enumerate(self.courier_names, start=1):
            bg_light, fg_dark = CARD_COLORS[(i - 1) % len(CARD_COLORS)]
            
            tk.Label(
                self.totals_frame,
                text=naam,
                anchor="w",
                bg=bg_light,
                fg=fg_dark,
                font=("Arial", 9, "bold")  # Iets kleiner voor compactheid
            ).grid(row=i, column=0, sticky="we", padx=3)
            
            # Subtotal label with formatting
            subtotal_label = tk.Label(
                self.totals_frame,
                text="0.00",
                anchor="e",
                bg=bg_light,
                fg=fg_dark,
                font=("Arial", 9)  # Iets kleiner
            )
            subtotal_label.grid(row=i, column=1, sticky="e", padx=3)
            # Update label when variable changes
            def update_subtotal(*args, var=self.totals_var[naam], label=subtotal_label):
                try:
                    if label.winfo_exists():
                        val = var.get()
                        label.config(text=f"{val:.2f}")
                except tk.TclError:
                    pass  # Widget destroyed, ignore
            self.totals_var[naam].trace_add("write", update_subtotal)
            update_subtotal()  # Initial update
            
            tk.Label(
                self.totals_frame,
                text=f"{STARTGELD:.2f}",
                anchor="e",
                bg=bg_light,
                fg=fg_dark,
                font=("Arial", 9)  # Iets kleiner
            ).grid(row=i, column=2, sticky="e", padx=3)
            
            # Eindtotaal label with formatting
            eindtotaal_label = tk.Label(
                self.totals_frame,
                text="0.00",
                font=("Arial", 9, "bold"),  # Iets kleiner
                anchor="e",
                bg=bg_light,
                fg=fg_dark
            )
            eindtotaal_label.grid(row=i, column=3, sticky="e", padx=3)
            # Update label when variable changes
            def update_eindtotaal(*args, var=self.eind_totals_var[naam], label=eindtotaal_label):
                try:
                    if label.winfo_exists():
                        val = var.get()
                        label.config(text=f"{val:.2f}")
                except tk.TclError:
                    pass  # Widget destroyed, ignore
            self.eind_totals_var[naam].trace_add("write", update_eindtotaal)
            update_eindtotaal()  # Initial update
            
            # Use same background color as row for Entry widgets to maintain full row coloring
            # Use a slightly lighter/darker shade for visual distinction while keeping same color family
            entry_bg = bg_light  # Same color as row for seamless appearance
            tk.Entry(
                self.totals_frame,
                textvariable=self.extra_km_var[naam],
                font=("Arial", 9, "bold"),  # Iets kleiner
                width=6,  # Iets smaller
                justify="right",
                bg=entry_bg,
                fg=fg_dark,  # Same foreground color
                relief="groove",
                borderwidth=2,
                insertbackground=fg_dark  # Cursor color matches text
            ).grid(row=i, column=4, padx=2)
            
            tk.Entry(
                self.totals_frame,
                textvariable=self.extra_uur_var[naam],
                font=("Arial", 9, "bold"),  # Iets kleiner
                width=5,
                justify="right",
                bg=entry_bg,
                fg=fg_dark,  # Same foreground color
                relief="groove",
                borderwidth=2,
                insertbackground=fg_dark  # Cursor color matches text
            ).grid(row=i, column=5, padx=2)
            
            tk.Entry(
                self.totals_frame,
                textvariable=self.extra_bedrag_var[naam],
                font=("Arial", 9, "bold"),  # Iets kleiner
                width=6,
                justify="right",
                bg=entry_bg,
                fg=fg_dark,  # Same foreground color
                relief="groove",
                borderwidth=2,
                insertbackground=fg_dark  # Cursor color matches text
            ).grid(row=i, column=6, padx=2)
            
            # Afrekening label with formatting
            afrekening_label = tk.Label(
                self.totals_frame,
                text="0.00",
                font=("Arial", 10, "bold"),  # Iets kleiner maar nog duidelijk
                fg=fg_dark,
                bg=bg_light
            )
            afrekening_label.grid(row=i, column=7, padx=3, sticky="e")
            # Update label when variable changes
            def update_afrekening(*args, var=self.afrekening_var[naam], label=afrekening_label):
                try:
                    if label.winfo_exists():
                        val = var.get()
                        label.config(text=f"{val:.2f}")
                except tk.TclError:
                    pass  # Widget destroyed, ignore
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
        
        # Column weights already configured above, but ensure all columns are properly sized
        for colindex in range(8):
            if colindex not in [4, 5, 6]:  # Km, Uur, Extra € don't need to expand
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
        
        # Get online orders from API (exclude afhaal/pickup orders) - SINGLE CALL
        online_orders = self.fetch_online_orders(order_date)
        online_orders_cache = {}
        
        if online_orders:
            # Convert online orders to same format as local orders
            for online_order in online_orders:
                # Skip afhaal/pickup orders - they should only appear in Afhaal tab
                if online_order.get('afhaal') or online_order.get('betaalmethode') == 'pickup':
                    continue
                
                # Cache for later lookups
                online_orders_cache[online_order['id']] = online_order
                
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
        
        # Get filter values
        search_text = self.filter_vars.get("search", tk.StringVar()).get()
        filter_koerier = self.filter_vars.get("koerier", tk.StringVar(value="Alle")).get()
        
        # Add orders to tree
        for idx, order in enumerate(orders):
            if not force and not self.ui.apply_filters(order, search_text, filter_koerier):
                continue
            
            koerier_naam = order.get('koerier_naam') or ""
            base_tag = "row_a" if idx % 2 == 0 else "row_b"
            
            # Priority: koerier tag overrides base tags for full row coloring
            if koerier_naam:
                tag = f"koerier_{koerier_naam.replace(' ', '_')}"
                # Only use koerier tag (no base_tag) to ensure full row coloring
                tags = (tag,)
            else:
                tags = (base_tag, "unassigned")
            
            # Mark online orders with special tag (but don't override koerier color)
            if order.get('online') and not koerier_naam:
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
            
            # Get telefoon number
            telefoon = order.get('telefoon', '')
            
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
                    telefoon,
                    order.get('tijd', ''),
                    vertrek,
                    koerier_display
                ),
                tags=tags
            )
        
        # Recalculate totals asynchronously (non-blocking) to prevent UI freeze
        if hasattr(self, 'totals_var') and self.totals_var:
            root = self.parent.winfo_toplevel()
            root.after_idle(lambda: self._recalculate_totals_async())
    
    def _recalculate_totals_async(self) -> None:
        """Recalculate totals asynchronously (non-blocking)."""
        try:
            self.recalculate_courier_totals()
            self.recalculate_total_payment()
        except Exception as e:
            logger.exception("Error in async totals recalculation")
    
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
        
        # Get online orders from API (exclude afhaal/pickup orders) - with timeout to prevent blocking
        try:
            online_orders = self.fetch_online_orders(order_date)
            for online_order in online_orders:
                # Skip afhaal/pickup orders - they should only appear in Afhaal tab
                if online_order.get('afhaal') or online_order.get('betaalmethode') == 'pickup':
                    continue
                
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
    
    def _update_payment_async(self, naam: str) -> None:
        """Update payment asynchronously for a specific courier."""
        try:
            self.recalculate_payment(naam)
            self.recalculate_total_payment()
        except Exception as e:
            logger.exception(f"Error updating payment for {naam}: {e}")
    
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
            # Reload couriers and update UI
            self.load_couriers()
            # Update delete combobox values
            if self.del_combo:
                self.del_combo['values'] = self.courier_names
                if self.courier_names:
                    self.del_name_var.set(self.courier_names[0])
            # Update only necessary parts instead of full rebuild
            self._refresh_courier_ui()
        except DatabaseError as e:
            messagebox.showerror("Fout", str(e))
        except ValueError as e:
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
            # Reload couriers and update UI
            self.load_couriers()
            # Update delete combobox values
            if self.del_combo:
                self.del_combo['values'] = self.courier_names
                if self.courier_names:
                    self.del_name_var.set(self.courier_names[0])
                else:
                    self.del_name_var.set("")
            # Update only necessary parts instead of full rebuild
            self._refresh_courier_ui()
        except DatabaseError as e:
            messagebox.showerror("Fout", str(e))
    
    def assign_courier(self, naam: str) -> None:
        """Assign selected orders to a courier - OPTIMIZED VERSION."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selectie", "Selecteer eerst één of meer rijen.")
            return
        
        koerier_id = self.courier_data.get(naam)
        if koerier_id is None:
            return
        
        try:
            # Separate online and local orders and collect totals from tree (FAST - no DB query)
            online_order_ids = []
            local_order_ids = []
            total_to_add = 0.0
            
            for item_id in selected:
                if isinstance(item_id, str) and item_id.startswith("online_"):
                    # Online order
                    order_id = int(item_id.replace("online_", ""))
                    online_order_ids.append(order_id)
                else:
                    # Local order - get total from tree directly (no DB query needed)
                    local_order_ids.append(int(item_id))
                    if self.tree.exists(item_id):
                        values = self.tree.item(item_id, "values")
                        if values and len(values) >= 3:
                            # Total is in column 2 (index 2)
                            try:
                                total_str = values[2].replace('€', '').replace(' ', '').replace(',', '.')
                                total_to_add += float(total_str)
                            except (ValueError, IndexError):
                                pass  # Skip if can't parse
            
            # Assign local orders - FAST: single batch update
            if local_order_ids:
                # Batch database update (single query)
                self.service.assign_courier_to_orders(local_order_ids, koerier_id)
                
                # Update UI directly from tree (no DB query, no full reload)
                for order_id in local_order_ids:
                    item_id = str(order_id)
                    if self.tree.exists(item_id):
                        values = list(self.tree.item(item_id, "values"))
                        # Check correct number of columns (10 columns: soort, nummer, totaal, straat, huis_nr, gemeente, telefoon, tijd, vertrek, koerier)
                        if len(values) >= 10:
                            # Update koerier column (last column, index 9)
                            values[9] = naam
                            # Update tags - ensure only koerier tag for full row coloring
                            tags = [f"koerier_{naam.replace(' ', '_')}"]  # Only koerier tag, no other tags to avoid conflicts
                            self.tree.item(item_id, values=tuple(values), tags=tuple(tags))
                            logger.debug(f"Updated UI for local order {order_id} with courier {naam}")
                        else:
                            logger.warning(f"Order {order_id} has {len(values)} columns, expected 10. Values: {values}")
                    else:
                        logger.warning(f"Order item {item_id} not found in tree")
                
                # Incremental totals update (FAST - no recalculation)
                if hasattr(self, 'totals_var') and self.totals_var and naam in self.totals_var:
                    current_total = self.totals_var[naam].get()
                    self.totals_var[naam].set(round(current_total + total_to_add, 2))
                    # Update payment asynchronously to prevent blocking
                    root = self.parent.winfo_toplevel()
                    root.after_idle(lambda: self._update_payment_async(naam))
            
            # Assign online orders via API (async to not block)
            if online_order_ids:
                # Run API calls in background
                root = self.parent.winfo_toplevel()
                root.after_idle(lambda: self._assign_online_orders_async(online_order_ids, koerier_id, naam))
                
        except (ValueError, DatabaseError) as e:
            logger.exception("Error assigning courier")
            messagebox.showerror("Fout", f"Kon koerier niet toewijzen: {e}")
    
    def _assign_online_orders_async(self, online_order_ids: List[int], koerier_id: int, naam: str) -> None:
        """Assign online orders asynchronously (non-blocking)."""
        try:
            # Try to assign orders
            self.assign_online_orders(online_order_ids, koerier_id)
            
            # Only update UI if assignment was successful (no exceptions raised)
            # Update UI for online orders
            for order_id in online_order_ids:
                item_id = f"online_{order_id}"
                if self.tree.exists(item_id):
                    values = list(self.tree.item(item_id, "values"))
                    # Check correct number of columns (10 columns: soort, nummer, totaal, straat, huis_nr, gemeente, telefoon, tijd, vertrek, koerier)
                    if len(values) >= 10:
                        # Update koerier column (last column, index 9)
                        values[9] = naam
                        # Update tags - ensure only koerier tag for full row coloring
                        tags = [f"koerier_{naam.replace(' ', '_')}"]  # Only koerier tag, no other tags to avoid conflicts
                        self.tree.item(item_id, values=tuple(values), tags=tuple(tags))
                        logger.debug(f"Updated UI for online order {order_id} with courier {naam}")
                    else:
                        logger.warning(f"Order {order_id} has {len(values)} columns, expected 10. Values: {values}")
                else:
                    logger.warning(f"Order item {item_id} not found in tree")
            
            # Update totals for online orders
            if online_order_ids:
                # Recalculate totals after successful assignment
                self.recalculate_courier_totals()
        except Exception as e:
            logger.exception(f"Error assigning online orders: {e}")
            # Error message already shown in assign_online_orders
    
    # REMOVED: _get_order_totals, _update_totals_async, _update_order_rows_courier, _update_online_order_rows_courier
    # These are no longer needed - we update directly in assign_courier for maximum speed
    
    def fetch_online_orders(self, order_date: date) -> List[Dict]:
        """Fetch online orders from API for a specific date."""
        try:
            # Authenticate if needed
            if not self.api_token:
                if not self.authenticate_api():
                    return []  # Silent fail if backend not available
            
            if not self.api_token:
                return []
            
            # Fetch all pending online orders
            response = self.api_session.get(
                f"{self.api_base_url}/orders/online/pending",
                timeout=2  # Short timeout to avoid hanging
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
                        f"{self.api_base_url}/orders/online/pending",
                        timeout=2
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
        except requests.exceptions.ConnectionError:
            # Backend not available - only log once per session
            if not hasattr(self, '_api_connection_logged'):
                logger.debug("Backend API not available (connection refused)")
                self._api_connection_logged = True
            return []
        except requests.exceptions.Timeout:
            return []  # Silent timeout
        except Exception as e:
            logger.debug(f"Error fetching online orders: {e}")
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
                    logger.debug("API authentication successful")
                    return True
            return False
        except requests.exceptions.ConnectionError:
            # Backend not available - silent fail
            return False
        except requests.exceptions.Timeout:
            return False
        except Exception as e:
            logger.debug(f"Error authenticating with API: {e}")
            return False
    
    def assign_online_orders(self, order_ids: List[int], koerier_id: int) -> None:
        """Assign online orders to a courier via API."""
        try:
            # Ensure we're authenticated
            if not self.api_token:
                if not self.authenticate_api():
                    logger.error("Cannot assign online orders: API authentication failed")
                    messagebox.showerror("Fout", "Kon niet authenticeren met de backend API. Controleer of de backend draait.")
                    return
            
            for order_id in order_ids:
                try:
                    response = self.api_session.put(
                        f"{self.api_base_url}/orders/{order_id}/status",
                        json={
                            "new_status": "Onderweg",  # Set status to Onderweg when assigning courier
                            "koerier_id": koerier_id
                        },
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"Successfully assigned courier {koerier_id} to online order {order_id}")
                    elif response.status_code == 401:
                        # Re-authenticate and retry once
                        logger.warning(f"Authentication expired, re-authenticating...")
                        if self.authenticate_api():
                            response = self.api_session.put(
                                f"{self.api_base_url}/orders/{order_id}/status",
                                json={
                                    "new_status": "Onderweg",
                                    "koerier_id": koerier_id
                                },
                                timeout=5
                            )
                            if response.status_code == 200:
                                logger.info(f"Successfully assigned courier {koerier_id} to online order {order_id} after re-auth")
                            else:
                                logger.error(f"Failed to assign courier to online order {order_id} after re-auth: {response.status_code} - {response.text}")
                                messagebox.showerror("Fout", f"Kon koerier niet toewijzen aan bestelling {order_id}: {response.text}")
                        else:
                            logger.error(f"Re-authentication failed for order {order_id}")
                            messagebox.showerror("Fout", "Kon niet authenticeren met de backend API.")
                    else:
                        error_msg = response.text if hasattr(response, 'text') else f"Status {response.status_code}"
                        logger.error(f"Failed to assign courier to online order {order_id}: {response.status_code} - {error_msg}")
                        messagebox.showerror("Fout", f"Kon koerier niet toewijzen aan bestelling {order_id}: {error_msg}")
                except requests.exceptions.Timeout:
                    logger.error(f"Timeout assigning courier to online order {order_id}")
                    messagebox.showerror("Fout", f"Timeout bij toewijzen koerier aan bestelling {order_id}. Controleer de backend verbinding.")
                except requests.exceptions.ConnectionError:
                    logger.error(f"Connection error assigning courier to online order {order_id}")
                    messagebox.showerror("Fout", "Kon niet verbinden met de backend API. Controleer of de backend draait.")
                    break  # Don't try more if connection failed
                except Exception as e:
                    logger.exception(f"Error assigning courier to online order {order_id}: {e}")
                    messagebox.showerror("Fout", f"Fout bij toewijzen koerier aan bestelling {order_id}: {e}")
        except Exception as e:
            logger.exception(f"Error assigning online orders: {e}")
            messagebox.showerror("Fout", f"Fout bij toewijzen koeriers: {e}")
    
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
    # Check if manager already exists (reuse to prevent rebuilding UI on tab switch)
    if hasattr(root, '_courier_manager'):
        manager = root._courier_manager
        # Just refresh orders if UI already exists
        if manager.tree:
            manager.load_orders(force=True)
        return
    
    # Create new manager and store reference
    manager = CourierManager(root)
    root._courier_manager = manager  # Store for reuse
    manager.load_couriers()
    manager.setup_ui()
