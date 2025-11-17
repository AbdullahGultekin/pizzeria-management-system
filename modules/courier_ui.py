"""
Courier UI Components

This module contains UI components for the courier management interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Callable, Optional
from datetime import date, datetime
from modules.courier_config import (
    CARD_COLORS, ROW_COLOR_A, ROW_COLOR_B, UNASSIGNED_COLOR,
    TABLE_COLUMNS, TABLE_HEADERS, TABLE_WIDTHS
)
from logging_config import get_logger

logger = get_logger("pizzeria.courier_ui")


class CourierUI:
    """UI components for courier management."""
    
    def __init__(self, parent: tk.Widget, courier_names: List[str]):
        """
        Initialize courier UI.
        
        Args:
            parent: Parent widget
            courier_names: List of courier names
        """
        self.parent = parent
        self.courier_names = courier_names
        self.koerier_row_colors = self._init_courier_colors()
    
    def _init_courier_colors(self) -> Dict[str, str]:
        """Initialize color mapping for couriers."""
        return {
            naam: CARD_COLORS[i % len(CARD_COLORS)][0]
            for i, naam in enumerate(self.courier_names)
        }
    
    @staticmethod
    def get_initials(name: str) -> str:
        """
        Get initials from a name.
        
        Args:
            name: Full name
            
        Returns:
            Initials (e.g., "John Doe" -> "JD")
        """
        parts = [p for p in name.split() if p.strip()]
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()
    
    def create_filter_bar(
        self,
        parent: tk.Widget,
        on_search_change: Callable,
        on_koerier_change: Callable,
        on_date_change: Callable,
        on_reload: Callable
    ) -> Dict[str, tk.Variable]:
        """
        Create filter bar with search, courier filter, and date filter.
        
        Returns:
            Dictionary with filter variables
        """
        filter_frame = tk.Frame(parent)
        filter_frame.pack(fill=tk.X, pady=(0, 6))
        
        # Search
        tk.Label(filter_frame, text="Zoek:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        search_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=search_var, width=12)
        search_entry.pack(side=tk.LEFT, padx=(6, 12))
        search_var.trace_add("write", lambda *_: on_search_change())
        
        # Courier filter
        tk.Label(filter_frame, text="Koerier:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        filter_koerier_var = tk.StringVar(value="Alle")
        koerier_opt = ttk.Combobox(
            filter_frame,
            state="readonly",
            values=["Alle"] + self.courier_names,
            textvariable=filter_koerier_var,
            width=12
        )
        koerier_opt.pack(side=tk.LEFT, padx=(6, 12))
        filter_koerier_var.trace_add("write", lambda *_: on_koerier_change())
        
        # Date filter
        tk.Label(filter_frame, text="Datum:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        datum_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        datum_entry = tk.Entry(filter_frame, textvariable=datum_var, width=12)
        datum_entry.pack(side=tk.LEFT, padx=(6, 12))
        datum_var.trace_add("write", lambda *_: on_date_change())
        
        # Reload button
        tk.Button(
            filter_frame,
            text="Herlaad",
            command=on_reload,
            bg="#E1E1FF"
        ).pack(side=tk.LEFT)
        
        return {
            "search": search_var,
            "koerier": filter_koerier_var,
            "datum": datum_var
        }
    
    def create_orders_table(self, parent: tk.Widget) -> ttk.Treeview:
        """
        Create orders table (Treeview).
        
        Returns:
            Configured Treeview widget
        """
        tree = ttk.Treeview(parent, columns=TABLE_COLUMNS, show="headings", height=18)
        
        # Configure columns
        for col in TABLE_COLUMNS:
            tree.heading(col, text=TABLE_HEADERS[col].upper())
            anchor = "w" if col not in ("totaal", "tijd") else ("center" if col == "tijd" else "e")
            tree.column(col, width=TABLE_WIDTHS[col], anchor=anchor)
        
        # Configure scrollbar
        scroll_y = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scroll_y.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.LEFT, fill=tk.Y)
        
        # Configure styles
        style = ttk.Style(tree)
        style.map("Treeview")
        tree.tag_configure("row_a", background=ROW_COLOR_A)
        tree.tag_configure("row_b", background=ROW_COLOR_B)
        tree.tag_configure("unassigned", background=UNASSIGNED_COLOR)
        
        # Configure courier-specific row colors
        for naam in self.courier_names:
            tag = f"koerier_{naam.replace(' ', '_')}"
            if not style.lookup(tag, "background"):
                tree.tag_configure(
                    tag,
                    background=self.koerier_row_colors.get(naam, "#FFFFFF"),
                    foreground="#000000"
                )
        
        # Selection highlight
        style.configure("Treeview", rowheight=24)
        style.map(
            "Treeview",
            background=[('selected', '#B3E5FC')],
            foreground=[('selected', '#0D47A1')]
        )
        
        return tree
    
    def create_courier_cards(
        self,
        parent: tk.Widget,
        on_assign: Callable[[str], None]
    ) -> tk.Frame:
        """
        Create courier cards display.
        
        Args:
            parent: Parent widget
            on_assign: Callback when assign button is clicked (receives courier name)
            
        Returns:
            Frame containing courier cards
        """
        cards_frame = tk.Frame(parent)
        cards_frame.pack(fill=tk.X)
        
        for i, naam in enumerate(self.courier_names):
            bg, fg = CARD_COLORS[i % len(CARD_COLORS)]
            card = tk.Frame(
                cards_frame,
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
            avatar.create_text(17, 17, text=self.get_initials(naam), fill=bg, font=("Arial", 10, "bold"))
            
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
            
            # Assign button
            btn = tk.Button(
                card,
                text="Wijs selectie toe",
                command=lambda n=naam: on_assign(n),
                bg="#FFFFFF",
                fg=fg,
                font=("Arial", 10, "bold"),
                relief="raised",
                bd=1,
                activebackground="#FFF"
            )
            btn.grid(row=0, column=2, rowspan=2, padx=(8, 0))
            
            # Hover effects
            def on_enter(e, b=btn):
                b.configure(bg="#F5F5F5")
            
            def on_leave(e, b=btn):
                b.configure(bg="#FFFFFF")
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        return cards_frame
    
    def update_courier_cards(
        self,
        cards_frame: tk.Frame,
        totals: Dict[str, float],
        on_assign: Callable
    ) -> None:
        """
        Update courier cards with totals.
        
        Args:
            cards_frame: Frame containing cards
            totals: Dictionary mapping courier names to totals
            on_assign: Callback for assign button
        """
        # Clear existing cards
        for w in cards_frame.winfo_children():
            w.destroy()
        
        # Recreate cards with updated totals
        for i, naam in enumerate(self.courier_names):
            bg, fg = CARD_COLORS[i % len(CARD_COLORS)]
            card = tk.Frame(
                cards_frame,
                bd=1,
                relief="groove",
                padx=10,
                pady=8,
                bg=bg,
                highlightthickness=0
            )
            card.grid(row=i // 2, column=i % 2, padx=6, pady=6, sticky="ew")
            card.grid_columnconfigure(1, weight=1)
            
            # Avatar
            avatar = tk.Canvas(card, width=34, height=34, bg=bg, highlightthickness=0)
            avatar.grid(row=0, column=0, rowspan=2, padx=(0, 8))
            avatar.create_oval(2, 2, 32, 32, fill=fg, outline=fg)
            avatar.create_text(17, 17, text=self.get_initials(naam), fill=bg, font=("Arial", 10, "bold"))
            
            # Name
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
            
            # Total
            total = totals.get(naam, 0.0)
            tk.Label(
                card,
                text=f"€{total:.2f}",
                font=("Arial", 10, "bold"),
                fg=fg,
                bg=bg
            ).grid(row=1, column=1, sticky="w")
            
            # Assign button
            btn = tk.Button(
                card,
                text="Wijs selectie toe",
                command=lambda n=naam: on_assign(n),
                bg="#FFFFFF",
                fg=fg,
                font=("Arial", 10, "bold"),
                relief="raised",
                bd=1,
                activebackground="#FFF"
            )
            btn.grid(row=0, column=2, rowspan=2, padx=(8, 0))
            
            # Hover effects
            def on_enter(e, b=btn):
                b.configure(bg="#F5F5F5")
            
            def on_leave(e, b=btn):
                b.configure(bg="#FFFFFF")
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
    
    @staticmethod
    def apply_filters(
        order: Dict,
        search_text: str,
        filter_koerier: str
    ) -> bool:
        """
        Check if order matches current filters.
        
        Args:
            order: Order dictionary
            search_text: Search text to match
            filter_koerier: Selected courier filter ("Alle" or courier name)
            
        Returns:
            True if order matches filters, False otherwise
        """
        # Search filter
        if search_text:
            search_lower = search_text.lower().strip()
            if not any(
                search_lower in str(v).lower()
                for v in (order.get('tijd', ''), order.get('straat', ''), order.get('plaats', ''), order.get('telefoon', ''))
            ):
                return False
        
        # Courier filter
        if filter_koerier and filter_koerier != "Alle":
            if (order.get('koerier_naam') or "") != filter_koerier:
                return False
        
        return True



