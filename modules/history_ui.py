"""
History UI Components

This module contains modern UI components for the order history interface.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional
from datetime import date, datetime, timedelta
from logging_config import get_logger

logger = get_logger("pizzeria.history_ui")


class HistoryUI:
    """Modern UI components for order history."""
    
    # Modern color scheme
    COLORS = {
        'bg_primary': '#F8F9FA',
        'bg_secondary': '#FFFFFF',
        'bg_header': '#E9ECEF',
        'bg_accent': '#0D6EFD',
        'bg_success': '#198754',
        'bg_danger': '#DC3545',
        'bg_warning': '#FFC107',
        'bg_info': '#0DCAF0',
        'text_primary': '#212529',
        'text_secondary': '#6C757D',
        'border': '#DEE2E6',
        'row_even': '#FFFFFF',
        'row_odd': '#F8F9FA',
        'row_hover': '#E7F1FF',
        'row_selected': '#CFE2FF'
    }
    
    @staticmethod
    def create_filter_bar(
        parent: tk.Widget,
        on_search_change: Callable,
        on_date_change: Callable,
        on_refresh: Callable
    ) -> Dict[str, tk.Variable]:
        """
        Create modern filter bar.
        
        Returns:
            Dictionary with filter variables
        """
        # Main filter frame with modern styling
        filter_frame = tk.Frame(parent, bg=HistoryUI.COLORS['bg_primary'], padx=15, pady=12)
        filter_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Title
        title_label = tk.Label(
            filter_frame,
            text="🔍 Zoeken en Filteren",
            font=("Arial", 12, "bold"),
            bg=HistoryUI.COLORS['bg_primary'],
            fg=HistoryUI.COLORS['text_primary']
        )
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Search frame
        search_frame = tk.Frame(filter_frame, bg=HistoryUI.COLORS['bg_primary'])
        search_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(
            search_frame,
            text="Zoek:",
            font=("Arial", 10, "bold"),
            bg=HistoryUI.COLORS['bg_primary'],
            fg=HistoryUI.COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=search_var,
            width=35,
            font=("Arial", 10),
            relief="solid",
            borderwidth=1,
            bg=HistoryUI.COLORS['bg_secondary']
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 15))
        search_entry.insert(0, "Naam, telefoon of adres...")
        search_entry.config(fg=HistoryUI.COLORS['text_secondary'])
        
        def on_search_focus_in(e):
            if search_entry.get() == "Naam, telefoon of adres...":
                search_entry.delete(0, tk.END)
                search_entry.config(fg=HistoryUI.COLORS['text_primary'])
        
        def on_search_focus_out(e):
            if not search_entry.get():
                search_entry.insert(0, "Naam, telefoon of adres...")
                search_entry.config(fg=HistoryUI.COLORS['text_secondary'])
        
        search_entry.bind("<FocusIn>", on_search_focus_in)
        search_entry.bind("<FocusOut>", on_search_focus_out)
        search_var.trace_add("write", lambda *_: on_search_change())
        
        # Date frame
        date_frame = tk.Frame(filter_frame, bg=HistoryUI.COLORS['bg_primary'])
        date_frame.pack(fill=tk.X)
        
        tk.Label(
            date_frame,
            text="Datum:",
            font=("Arial", 10, "bold"),
            bg=HistoryUI.COLORS['bg_primary'],
            fg=HistoryUI.COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        date_entry = tk.Entry(
            date_frame,
            textvariable=date_var,
            width=15,
            font=("Arial", 10),
            relief="solid",
            borderwidth=1,
            bg=HistoryUI.COLORS['bg_secondary']
        )
        date_entry.pack(side=tk.LEFT, padx=(0, 15))
        date_var.trace_add("write", lambda *_: on_date_change())
        
        # Quick date buttons
        quick_dates_frame = tk.Frame(date_frame, bg=HistoryUI.COLORS['bg_primary'])
        quick_dates_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        def set_today():
            date_var.set(date.today().strftime('%Y-%m-%d'))
        
        def set_yesterday():
            yesterday = date.today() - timedelta(days=1)
            date_var.set(yesterday.strftime('%Y-%m-%d'))
        
        def clear_date():
            date_var.set("")
        
        tk.Button(
            quick_dates_frame,
            text="Vandaag",
            command=set_today,
            bg=HistoryUI.COLORS['bg_info'],
            fg="white",
            font=("Arial", 9),
            relief="flat",
            padx=8,
            pady=2
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            quick_dates_frame,
            text="Gisteren",
            command=set_yesterday,
            bg=HistoryUI.COLORS['bg_info'],
            fg="white",
            font=("Arial", 9),
            relief="flat",
            padx=8,
            pady=2
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            quick_dates_frame,
            text="Alles",
            command=clear_date,
            bg=HistoryUI.COLORS['bg_secondary'],
            fg=HistoryUI.COLORS['text_primary'],
            font=("Arial", 9),
            relief="flat",
            padx=8,
            pady=2
        ).pack(side=tk.LEFT, padx=2)
        
        # Refresh button
        refresh_btn = tk.Button(
            filter_frame,
            text="🔄 Vernieuwen",
            command=on_refresh,
            bg=HistoryUI.COLORS['bg_accent'],
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=15,
            pady=6,
            cursor="hand2"
        )
        refresh_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        return {
            "search": search_var,
            "date": date_var
        }
    
    @staticmethod
    def create_statistics_panel(parent: tk.Widget, stats: Dict[str, float]) -> tk.Frame:
        """
        Create statistics panel showing order counts and totals.
        
        Args:
            parent: Parent widget
            stats: Statistics dictionary with count, total, average
            
        Returns:
            Statistics frame
        """
        stats_frame = tk.Frame(parent, bg=HistoryUI.COLORS['bg_primary'], padx=15, pady=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(
            stats_frame,
            text="📊 Statistieken",
            font=("Arial", 11, "bold"),
            bg=HistoryUI.COLORS['bg_primary'],
            fg=HistoryUI.COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 8))
        
        stats_grid = tk.Frame(stats_frame, bg=HistoryUI.COLORS['bg_primary'])
        stats_grid.pack(fill=tk.X)
        
        # Count card
        count_card = tk.Frame(
            stats_grid,
            bg=HistoryUI.COLORS['bg_info'],
            relief="flat",
            padx=15,
            pady=10
        )
        count_card.pack(side=tk.LEFT, padx=(0, 10), fill=tk.BOTH, expand=True)
        
        tk.Label(
            count_card,
            text="Aantal Bestellingen",
            font=("Arial", 9),
            bg=HistoryUI.COLORS['bg_info'],
            fg="white"
        ).pack(anchor="w")
        count_var = tk.StringVar(value=str(int(stats.get('count', 0))))
        tk.Label(
            count_card,
            textvariable=count_var,
            font=("Arial", 18, "bold"),
            bg=HistoryUI.COLORS['bg_info'],
            fg="white"
        ).pack(anchor="w")
        
        # Total card
        total_card = tk.Frame(
            stats_grid,
            bg=HistoryUI.COLORS['bg_success'],
            relief="flat",
            padx=15,
            pady=10
        )
        total_card.pack(side=tk.LEFT, padx=(0, 10), fill=tk.BOTH, expand=True)
        
        tk.Label(
            total_card,
            text="Totaal Bedrag",
            font=("Arial", 9),
            bg=HistoryUI.COLORS['bg_success'],
            fg="white"
        ).pack(anchor="w")
        total_var = tk.StringVar(value=f"€{stats.get('total', 0):.2f}")
        tk.Label(
            total_card,
            textvariable=total_var,
            font=("Arial", 18, "bold"),
            bg=HistoryUI.COLORS['bg_success'],
            fg="white"
        ).pack(anchor="w")
        
        # Average card
        avg_card = tk.Frame(
            stats_grid,
            bg=HistoryUI.COLORS['bg_warning'],
            relief="flat",
            padx=15,
            pady=10
        )
        avg_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            avg_card,
            text="Gemiddeld per Bestelling",
            font=("Arial", 9),
            bg=HistoryUI.COLORS['bg_warning'],
            fg="white"
        ).pack(anchor="w")
        avg_var = tk.StringVar(value=f"€{stats.get('average', 0):.2f}")
        tk.Label(
            avg_card,
            textvariable=avg_var,
            font=("Arial", 18, "bold"),
            bg=HistoryUI.COLORS['bg_warning'],
            fg="white"
        ).pack(anchor="w")
        
        return stats_frame, {'count': count_var, 'total': total_var, 'average': avg_var}
    
    @staticmethod
    def create_orders_table(parent: tk.Widget) -> ttk.Treeview:
        """
        Create modern styled orders table.
        
        Returns:
            Configured Treeview widget
        """
        # Table frame - don't expand to allow buttons to be visible
        table_frame = tk.Frame(parent, bg=HistoryUI.COLORS['bg_primary'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        
        # Title
        tk.Label(
            table_frame,
            text="📋 Bestellingen",
            font=("Arial", 11, "bold"),
            bg=HistoryUI.COLORS['bg_primary'],
            fg=HistoryUI.COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 8))
        
        # Treeview container
        tree_container = tk.Frame(table_frame, bg=HistoryUI.COLORS['bg_secondary'], relief="solid", borderwidth=1)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ('datum', 'tijd', 'bon', 'naam', 'telefoon', 'adres', 'levertijd', 'totaal')
        tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=20)
        
        # Configure columns
        column_config = {
            'datum': ('Datum', 100, 'center'),
            'tijd': ('Tijd', 80, 'center'),
            'bon': ('Bonnummer', 100, 'center'),
            'naam': ('Naam', 150, 'w'),
            'telefoon': ('Telefoon', 120, 'w'),
            'adres': ('Adres', 200, 'w'),
            'levertijd': ('Levertijd', 90, 'center'),
            'totaal': ('Totaal (€)', 100, 'e')
        }
        
        for col in columns:
            text, width, anchor = column_config[col]
            tree.heading(col, text=text)
            tree.column(col, width=width, anchor=anchor)
        
        # Scrollbar
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.pack(side='left', fill='both', expand=True, padx=2, pady=2)
        vsb.pack(side='right', fill='y', pady=2)
        
        # Modern styling
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure treeview style
        style.configure(
            "Treeview",
            background=HistoryUI.COLORS['bg_secondary'],
            foreground=HistoryUI.COLORS['text_primary'],
            fieldbackground=HistoryUI.COLORS['bg_secondary'],
            rowheight=28,
            font=("Arial", 10)
        )
        
        style.configure(
            "Treeview.Heading",
            background=HistoryUI.COLORS['bg_header'],
            foreground=HistoryUI.COLORS['text_primary'],
            font=("Arial", 10, "bold"),
            relief="flat"
        )
        
        # Zebra striping
        tree.tag_configure("even", background=HistoryUI.COLORS['row_even'])
        tree.tag_configure("odd", background=HistoryUI.COLORS['row_odd'])
        
        # Selection styling
        style.map(
            "Treeview",
            background=[('selected', HistoryUI.COLORS['row_selected'])],
            foreground=[('selected', HistoryUI.COLORS['text_primary'])]
        )
        
        return tree
    
    @staticmethod
    def create_action_buttons(
        parent: tk.Widget,
        on_edit: Callable,
        on_delete: Callable,
        on_delete_all: Callable
    ) -> None:
        """
        Create modern action buttons.
        
        Args:
            parent: Parent widget
            on_edit: Callback for edit action
            on_delete: Callback for delete action
            on_delete_all: Callback for delete all action
        """
        button_frame = tk.Frame(parent, bg=HistoryUI.COLORS['bg_primary'], padx=15, pady=12)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Left side - primary actions
        left_buttons = tk.Frame(button_frame, bg=HistoryUI.COLORS['bg_primary'])
        left_buttons.pack(side=tk.LEFT)
        
        edit_btn = tk.Button(
            left_buttons,
            text="✏️ Bewerk & Herdruk",
            command=on_edit,
            bg=HistoryUI.COLORS['bg_success'],
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Right side - danger actions
        right_buttons = tk.Frame(button_frame, bg=HistoryUI.COLORS['bg_primary'])
        right_buttons.pack(side=tk.RIGHT)
        
        delete_btn = tk.Button(
            right_buttons,
            text="🗑️ Verwijder Bestelling",
            command=on_delete,
            bg=HistoryUI.COLORS['bg_danger'],
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_all_btn = tk.Button(
            right_buttons,
            text="⚠️ Verwijder Alles",
            command=on_delete_all,
            bg="#8B0000",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            pady=8,
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
        add_hover_effect(delete_btn, HistoryUI.COLORS['bg_danger'])
        add_hover_effect(delete_all_btn, "#8B0000")
    
    @staticmethod
    def _lighten_color(hex_color: str) -> str:
        """Lighten a hex color for hover effect."""
        # Simple lightening by increasing RGB values
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        lightened = tuple(min(255, c + 20) for c in rgb)
        return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"

