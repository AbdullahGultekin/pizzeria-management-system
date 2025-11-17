"""
Enhanced Product Options Dialog

Modern, visually improved interface for product customization with better UX.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Dict, List, Any, Optional, Callable, Set
from logging_config import get_logger

logger = get_logger("pizzeria.ui.product_options")


class ProductOptionsDialog:
    """Enhanced product options dialog with modern UI and better visual feedback."""
    
    COLORS = {
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F8F9FA',
        'bg_section': '#F1F3F5',
        'bg_selected': '#E3F2FD',
        'bg_hover': '#F5F5F5',
        'border': '#DEE2E6',
        'border_selected': '#0D6EFD',
        'text_primary': '#212529',
        'text_secondary': '#6C757D',
        'text_accent': '#0D6EFD',
        'accent': '#0D6EFD',
        'success': '#198754',
        'warning': '#FFC107',
        'danger': '#DC3545',
        'pizza_yellow': '#FFDD44',
    }
    
    def __init__(
        self,
        parent: tk.Tk,
        product: Dict[str, Any],
        category: str,
        extras_config: Dict[str, Any],
        initial_values: Dict[str, Any],
        on_add: Callable[[Dict[str, Any]], None],
        on_close: Optional[Callable[[], None]] = None
    ):
        """
        Initialize product options dialog.
        
        Args:
            parent: Parent window
            product: Product dictionary
            category: Category name
            extras_config: Extras configuration
            initial_values: Initial control values
            on_add: Callback when product is added
            on_close: Optional callback when dialog closes
        """
        self.parent = parent
        self.product = product
        self.category = category.lower()
        self.extras_config = extras_config
        self.initial_values = initial_values
        self.on_add = on_add
        self.on_close = on_close
        
        self.is_pizza = self.category in ("small pizza's", "medium pizza's", "large pizza's")
        self.is_half_half = self.is_pizza and ("half" in product['naam'].lower())
        self.is_medium_pizza = self.category == "medium pizza's"
        
        # Get product-specific extras
        self.product_extras = {}
        if product.get('naam') and isinstance(extras_config, dict) and product['naam'] in extras_config:
            self.product_extras = extras_config[product['naam']]
        elif isinstance(extras_config, dict) and 'default' in extras_config:
            self.product_extras = extras_config.get('default', {})
        
        # Control variables
        self.ctrl = {
            'aantal': tk.IntVar(value=initial_values.get('aantal', 1)),
            'vlees': tk.StringVar(value=initial_values.get('vlees', '')),
            'opmerking': tk.StringVar(value=initial_values.get('opmerking', '')),
            'bijgerecht_combos': [],
            'saus_combos': [],
            'garnering': [],
            '_sauzen_toeslag_cache': 0.0,
        }
        
        self.half1_var = tk.StringVar(value=initial_values.get('half1', '1'))
        self.half2_var = tk.StringVar(value=initial_values.get('half2', '2'))
        self.volle_kaart_var = tk.BooleanVar(value=initial_values.get('volle_kaart', False))
        
        # State
        self.bijgerecht_counts: Dict[str, int] = {}  # Changed from Set to Dict to allow duplicates
        self.saus_counts: Dict[str, int] = {}
        self.selected_garnering: Set[str] = set()
        
        self.window: Optional[tk.Toplevel] = None
        self.price_label: Optional[tk.Label] = None
        
        self._create_window()
        self._setup_ui()
        self._update_price()
    
    def _create_window(self) -> None:
        """Create the options window."""
        self.window = tk.Toplevel(self.parent, bg=self.COLORS['bg_primary'])
        self.window.title(f"⚙️ Opties — {self.product['naam']}")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        width, height = 720, 620
        sw, sh = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        x, y = (sw // 2) - (width // 2), max(40, (sh // 2) - (height // 2))
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.resizable(True, True)
        self.window.minsize(680, 550)
        
        # Bind close event
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _setup_ui(self) -> None:
        """Setup the UI components."""
        # Main container with scrollable canvas
        main_container = tk.Frame(self.window, bg=self.COLORS['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        
        # Header
        header = self._create_header(main_container)
        header.pack(fill=tk.X, pady=(0, 8))
        
        # Scrollable content
        canvas_frame = tk.Frame(main_container, bg=self.COLORS['bg_primary'])
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg=self.COLORS['bg_primary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['bg_primary'])
        
        def update_scrollregion(event=None):
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", update_scrollregion)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def configure_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', configure_canvas_width)
        
        # Mouse wheel scrolling (Windows/Mac)
        def on_mousewheel(event):
            if event.delta:
                # Windows
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                # macOS
                canvas.yview_scroll(int(-1 * event.delta), "units")
        
        # Bind mouse wheel to canvas and scrollable frame
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            widget.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            widget.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        bind_mousewheel(canvas)
        bind_mousewheel(scrollable_frame)
        
        # Content sections
        self._create_aantal_section(scrollable_frame)
        self._create_half_half_section(scrollable_frame)
        self._create_vlees_section(scrollable_frame)
        self._create_bijgerecht_section(scrollable_frame)
        self._create_sauzen_section(scrollable_frame)
        self._create_garnering_section(scrollable_frame)
        self._create_volle_kaart_section(scrollable_frame)
        self._create_opmerking_section(scrollable_frame)
        
        # Pack scrollable area
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Update scroll region after all widgets are created
        self.window.update_idletasks()
        update_scrollregion()
        
        # Footer with price and buttons
        footer = self._create_footer(main_container)
        footer.pack(fill=tk.X, pady=(8, 0))
    
    def _create_header(self, parent: tk.Frame) -> tk.Frame:
        """Create header section."""
        header = tk.Frame(parent, bg=self.COLORS['bg_secondary'], relief=tk.RAISED, bd=1, padx=10, pady=6)
        
        # Product name
        name_label = tk.Label(
            header,
            text=self.product['naam'],
            font=("Arial", 12, "bold"),
            bg=self.COLORS['bg_secondary'],
            fg=self.COLORS['text_primary']
        )
        name_label.pack(side=tk.LEFT)
        
        # Base price
        base_price_label = tk.Label(
            header,
            text=f"€{self.product['prijs']:.2f}",
            font=("Arial", 9),
            bg=self.COLORS['bg_secondary'],
            fg=self.COLORS['text_secondary']
        )
        base_price_label.pack(side=tk.RIGHT, padx=(8, 0))
        
        return header
    
    def _create_aantal_section(self, parent: tk.Frame) -> None:
        """Create aantal (quantity) section."""
        section = self._create_section_frame(parent, "📊 Aantal")
        
        aantal_frame = tk.Frame(section, bg=self.COLORS['bg_section'])
        aantal_frame.pack(fill=tk.X, padx=8, pady=4)
        
        tk.Label(
            aantal_frame,
            text="Aantal:",
            font=("Arial", 9, "bold"),
            bg=self.COLORS['bg_section'],
            fg=self.COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        spinbox = tk.Spinbox(
            aantal_frame,
            from_=1,
            to=30,
            width=6,
            textvariable=self.ctrl['aantal'],
            font=("Arial", 9),
            command=self._update_price
        )
        spinbox.pack(side=tk.LEFT)
        spinbox.bind('<KeyRelease>', lambda e: self._update_price())
    
    def _create_half_half_section(self, parent: tk.Frame) -> None:
        """Create half-half pizza section."""
        if not self.is_half_half:
            return
        
        section = self._create_section_frame(parent, "🍕 Half-Half Pizza")
        
        info_label = tk.Label(
            section,
            text="Kies 2 verschillende pizza nummers:",
            font=("Arial", 8, "italic"),
            bg=self.COLORS['bg_section'],
            fg=self.COLORS['text_secondary']
        )
        info_label.pack(pady=(2, 6))
        
        # Container for both pizza grids side by side
        half_container = tk.Frame(section, bg=self.COLORS['bg_section'])
        half_container.pack(fill=tk.X, padx=8, pady=4)
        
        # Pizza 1 grid
        pizza1_frame = tk.Frame(half_container, bg=self.COLORS['bg_section'])
        pizza1_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        
        pizza1_label = tk.Label(
            pizza1_frame,
            text="Pizza 1:",
            font=("Arial", 9, "bold"),
            bg=self.COLORS['bg_section'],
            fg=self.COLORS['text_primary']
        )
        pizza1_label.pack(anchor="w", pady=(0, 3))
        
        self._create_compact_pizza_grid(pizza1_frame, self.half1_var, 1)
        
        # Pizza 2 grid
        pizza2_frame = tk.Frame(half_container, bg=self.COLORS['bg_section'])
        pizza2_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))
        
        pizza2_label = tk.Label(
            pizza2_frame,
            text="Pizza 2:",
            font=("Arial", 9, "bold"),
            bg=self.COLORS['bg_section'],
            fg=self.COLORS['text_primary']
        )
        pizza2_label.pack(anchor="w", pady=(0, 3))
        
        self._create_compact_pizza_grid(pizza2_frame, self.half2_var, 2)
        
        self.half1_var.trace_add("write", lambda *_: self._update_price())
        self.half2_var.trace_add("write", lambda *_: self._update_price())
    
    def _create_compact_pizza_grid(self, parent: tk.Frame, var: tk.StringVar, default: int) -> None:
        """Create compact pizza number selection grid with scrollable area."""
        # Create scrollable canvas container
        canvas_container = tk.Frame(parent, bg=self.COLORS['bg_section'], relief=tk.SUNKEN, bd=1)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(canvas_container, bg=self.COLORS['bg_section'], highlightthickness=0, height=120)
        scrollbar = tk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=canvas.yview)
        grid_frame = tk.Frame(canvas, bg=self.COLORS['bg_section'])
        
        def update_scrollregion(event=None):
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        grid_frame.bind("<Configure>", update_scrollregion)
        
        canvas_window = canvas.create_window((0, 0), window=grid_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def configure_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', configure_canvas_width)
        
        # Use a more compact grid layout
        max_num, cols = 49, 7  # 7 columns for better fit
        
        # Create grid of buttons
        for i in range(1, max_num + 1):
            btn = tk.Radiobutton(
                grid_frame,
                text=str(i),
                value=str(i),
                variable=var,
                width=3,
                indicatoron=0,
                bg="#EDEBFE",
                selectcolor=self.COLORS['pizza_yellow'],
                activebackground="#D4D1F5",
                relief=tk.RAISED,
                bd=1,
                padx=2,
                pady=2,
                font=("Arial", 8, "bold"),
                command=self._update_price,
                cursor="hand2"
            )
            r, c = (i - 1) // cols, (i - 1) % cols
            btn.grid(row=r, column=c, padx=1, pady=1, sticky="nsew")
        
        # Configure grid weights for equal column distribution
        for c in range(cols):
            grid_frame.grid_columnconfigure(c, weight=1, uniform="pizza_col")
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mouse wheel scrolling for pizza grids
        def on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                canvas.yview_scroll(int(-1 * event.delta), "units")
        
        canvas.bind("<MouseWheel>", on_mousewheel)
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        var.set(str(default))
        update_scrollregion()
    
    def _create_vlees_section(self, parent: tk.Frame) -> None:
        """Create vlees (meat) selection section."""
        if self.is_pizza or not isinstance(self.extras_config, dict):
            return
        
        vlees_options = self.extras_config.get('vlees', [])
        if not vlees_options:
            return
        
        section = self._create_section_frame(parent, "🥩 Vlees")
        
        vlees_frame = tk.Frame(section, bg=self.COLORS['bg_section'])
        vlees_frame.pack(fill=tk.X, padx=8, pady=4)
        
        if not self.ctrl['vlees'].get() and vlees_options:
            self.ctrl['vlees'].set(vlees_options[0])
        
        vlees_buttons = {}
        
        def pick_vlees(naam: str) -> None:
            self.ctrl['vlees'].set(naam)
            for k, btn in vlees_buttons.items():
                self._style_toggle_button(btn, k == naam)
            self._update_price()
        
        for i, v in enumerate(vlees_options):
            r, c = divmod(i, 4)
            btn = self._create_toggle_button(
                vlees_frame,
                v,
                v == self.ctrl['vlees'].get(),
                width=12,
                command=lambda n=v: pick_vlees(n)
            )
            btn.grid(row=r, column=c, padx=3, pady=2, sticky="w")
            vlees_buttons[v] = btn
    
    def _create_bijgerecht_section(self, parent: tk.Frame) -> None:
        """Create bijgerecht (side dish) section."""
        bron_bijgerecht = (
            self.product_extras.get('bijgerecht', self.extras_config.get('bijgerecht', []))
            if isinstance(self.extras_config, dict) else []
        )
        
        if not bron_bijgerecht:
            return
        
        bijgerecht_aantal = self.product_extras.get('bijgerecht_aantal', 1) if isinstance(self.product_extras, dict) else 1
        
        section = self._create_section_frame(
            parent,
            f"🍟 Bijgerecht{'en' if bijgerecht_aantal > 1 else ''} ({bijgerecht_aantal})"
        )
        
        bg_frame = tk.Frame(section, bg=self.COLORS['bg_section'])
        bg_frame.pack(fill=tk.X, padx=8, pady=4)
        
        # Initialize counts from existing combos
        if self.ctrl['bijgerecht_combos']:
            vals = [v.get() for v in self.ctrl['bijgerecht_combos'] if v.get()]
            self.bijgerecht_counts = {naam: 0 for naam in bron_bijgerecht}
            for naam in vals:
                if naam in self.bijgerecht_counts:
                    self.bijgerecht_counts[naam] += 1
        else:
            self.bijgerecht_counts = {naam: 0 for naam in bron_bijgerecht}
        
        # Total label
        total_lbl = tk.Label(
            bg_frame,
            text="",
            font=("Arial", 8, "bold"),
            bg=self.COLORS['bg_section'],
            fg=self.COLORS['text_accent']
        )
        total_lbl.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 4))
        
        def refresh_bijgerecht():
            """Refresh bijgerecht display and update combos."""
            total = sum(self.bijgerecht_counts.values())
            total_lbl.config(text=f"Gekozen: {total} / {bijgerecht_aantal}")
            
            # Update button styles
            for naam, btn in bijgerecht_buttons.items():
                count = self.bijgerecht_counts.get(naam, 0)
                self._style_toggle_button(btn, count > 0)
                # Update button text to show count if > 0
                if count > 0:
                    btn.config(text=f"{naam} ({count})")
                else:
                    btn.config(text=naam)
            
            # Update combos
            self.ctrl['bijgerecht_combos'].clear()
            for naam, count in self.bijgerecht_counts.items():
                for _ in range(count):
                    self.ctrl['bijgerecht_combos'].append(tk.StringVar(value=naam))
            
            self._update_price()
        
        def dec_bij(naam: str) -> None:
            """Decrease bijgerecht count."""
            if self.bijgerecht_counts[naam] > 0:
                self.bijgerecht_counts[naam] -= 1
                refresh_bijgerecht()
        
        def inc_bij(naam: str) -> None:
            """Increase bijgerecht count."""
            total = sum(self.bijgerecht_counts.values())
            if total >= bijgerecht_aantal:
                # Visual feedback: flash red
                btn = bijgerecht_buttons[naam]
                old_bg = btn.cget("bg")
                btn.configure(bg="#FFE8E8")
                btn.after(200, lambda: btn.configure(bg=old_bg))
                return
            self.bijgerecht_counts[naam] += 1
            refresh_bijgerecht()
        
        bijgerecht_buttons = {}
        
        for i, naam in enumerate(bron_bijgerecht):
            r, c = divmod(i, 4)
            row_base = r + 1
            
            btn_minus = tk.Button(
                bg_frame,
                text="−",
                width=2,
                padx=1,
                pady=1,
                bg="#F3F4F6",
                activebackground="#E9ECEF",
                relief=tk.RAISED,
                bd=1,
                font=("Arial", 9, "bold"),
                command=lambda n=naam: dec_bij(n)
            )
            
            btn = self._create_toggle_button(
                bg_frame,
                naam,
                self.bijgerecht_counts.get(naam, 0) > 0,
                width=12,
                command=lambda n=naam: inc_bij(n)
            )
            bijgerecht_buttons[naam] = btn
            
            btn_minus.grid(row=row_base, column=c * 2, padx=1, pady=2, sticky="w")
            btn.grid(row=row_base, column=c * 2 + 1, padx=(3, 8), pady=2, sticky="w")
        
        refresh_bijgerecht()
    
    def _create_sauzen_section(self, parent: tk.Frame) -> None:
        """Create sauzen (sauces) section."""
        saus_key = None
        if isinstance(self.product_extras, dict) and 'sauzen' in self.product_extras:
            saus_key = 'sauzen'
        elif isinstance(self.product_extras, dict) and 'saus' in self.product_extras:
            saus_key = 'saus'
        elif isinstance(self.extras_config, dict) and 'sauzen' in self.extras_config:
            saus_key = 'sauzen'
        elif isinstance(self.extras_config, dict) and 'saus' in self.extras_config:
            saus_key = 'saus'
        
        if not saus_key:
            return
        
        bron_sauzen = (
            self.product_extras.get(saus_key, self.extras_config.get(saus_key, []))
            if isinstance(self.extras_config, dict) else []
        )
        
        if not bron_sauzen:
            return
        
        sauzen_aantal = (
            self.product_extras.get('sauzen_aantal', self.extras_config.get('sauzen_aantal', 1))
            if isinstance(self.extras_config, dict) else 1
        )
        
        section = self._create_section_frame(
            parent,
            f"🍯 Sauzen (eerste {sauzen_aantal} inbegrepen, extra +€1,50/st)"
        )
        
        s_frame = tk.Frame(section, bg=self.COLORS['bg_section'])
        s_frame.pack(fill=tk.X, padx=8, pady=4)
        
        # Initialize counts
        current_list = [v.get() for v in self.ctrl.get('saus_combos', []) if v.get()]
        self.saus_counts = {naam: 0 for naam in bron_sauzen}
        for naam in current_list:
            if naam in self.saus_counts:
                self.saus_counts[naam] += 1
        
        # Total label
        total_lbl = tk.Label(
            s_frame,
            text="",
            font=("Arial", 8, "bold"),
            bg=self.COLORS['bg_section'],
            fg=self.COLORS['text_accent']
        )
        total_lbl.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 4))
        
        # Toeslag label
        toeslag_lbl = tk.Label(
            s_frame,
            text="",
            font=("Arial", 8),
            bg=self.COLORS['bg_section'],
            fg=self.COLORS['danger']
        )
        toeslag_lbl.grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 3))
        
        EXTRA_SAUS_PRIJS = 1.50
        
        def refresh_sauzen():
            t = sum(self.saus_counts.values())
            extra_cnt = max(0, t - sauzen_aantal)
            toeslag = round(extra_cnt * EXTRA_SAUS_PRIJS, 2)
            
            total_lbl.config(text=f"Gekozen: {t} (inclusief {sauzen_aantal} gratis)")
            toeslag_lbl.config(
                text=(f"Extra sauzen: {extra_cnt} × €{EXTRA_SAUS_PRIJS:.2f} = €{toeslag:.2f}")
                if extra_cnt > 0 else ""
            )
            
            self.ctrl['saus_combos'].clear()
            dup_list = []
            for naam, cnt in self.saus_counts.items():
                dup_list.extend([naam] * max(0, cnt))
            for naam in dup_list:
                self.ctrl['saus_combos'].append(tk.StringVar(value=naam))
            
            self.ctrl['_sauzen_toeslag_cache'] = toeslag
            self._update_price()
        
        def dec(naam: str, amt_lbl: tk.Label) -> None:
            if self.saus_counts[naam] > 0:
                self.saus_counts[naam] -= 1
                amt_lbl.config(text=str(self.saus_counts[naam]))
                refresh_sauzen()
        
        def inc(naam: str, amt_lbl: tk.Label) -> None:
            self.saus_counts[naam] += 1
            amt_lbl.config(text=str(self.saus_counts[naam]))
            refresh_sauzen()
        
        for i, naam in enumerate(bron_sauzen):
            r, c = divmod(i, 2)
            row_base = r + 2
            col_base = c * 5
            
            btn_minus = tk.Button(
                s_frame,
                text="−",
                width=2,
                padx=1,
                pady=1,
                bg="#F3F4F6",
                activebackground="#E9ECEF",
                relief=tk.RAISED,
                bd=1,
                font=("Arial", 9, "bold"),
                command=lambda n=naam: None
            )
            
            name_lbl = tk.Label(
                s_frame,
                text=naam,
                bg=self.COLORS['bg_section'],
                fg=self.COLORS['text_primary'],
                font=("Arial", 8)
            )
            
            amt_lbl = tk.Label(
                s_frame,
                text=str(self.saus_counts[naam]),
                bg=self.COLORS['bg_section'],
                fg=self.COLORS['text_accent'],
                width=2,
                font=("Arial", 9, "bold")
            )
            
            btn_plus = tk.Button(
                s_frame,
                text="+",
                width=2,
                padx=1,
                pady=1,
                bg="#F3F4F6",
                activebackground="#E9ECEF",
                relief=tk.RAISED,
                bd=1,
                font=("Arial", 9, "bold"),
                command=lambda n=naam: None
            )
            
            btn_minus.configure(command=lambda n=naam, al=amt_lbl: dec(n, al))
            btn_plus.configure(command=lambda n=naam, al=amt_lbl: inc(n, al))
            
            btn_minus.grid(row=row_base, column=col_base + 0, padx=1, pady=2, sticky="w")
            name_lbl.grid(row=row_base, column=col_base + 1, padx=(3, 6), pady=2, sticky="w")
            amt_lbl.grid(row=row_base, column=col_base + 2, padx=1, pady=2, sticky="w")
            btn_plus.grid(row=row_base, column=col_base + 3, padx=(1, 8), pady=2, sticky="w")
        
        refresh_sauzen()
    
    def _create_garnering_section(self, parent: tk.Frame) -> None:
        """Create garnering (garnish) section."""
        bron_garnering = None
        if isinstance(self.product_extras, dict) and 'garnering' in self.product_extras:
            bron_garnering = self.product_extras['garnering']
        elif isinstance(self.extras_config, dict) and 'garnering' in self.extras_config:
            bron_garnering = self.extras_config['garnering']
        
        if not bron_garnering:
            return
        
        if isinstance(bron_garnering, list):
            items = [(naam, 0.0) for naam in bron_garnering]
        elif isinstance(bron_garnering, dict):
            items = list(bron_garnering.items())
        else:
            items = []
        
        if not items:
            return
        
        section = self._create_section_frame(parent, "🌿 Garnering")
        
        g_frame = tk.Frame(section, bg=self.COLORS['bg_section'])
        g_frame.pack(fill=tk.X, padx=8, pady=4)
        
        # Initialize selected
        self.selected_garnering = set([
            naam for (naam, var) in self.ctrl.get('garnering', []) if var.get()
        ])
        
        def toggle_g(naam: str, btn: tk.Button) -> None:
            if naam in self.selected_garnering:
                self.selected_garnering.remove(naam)
                self._style_toggle_button(btn, False)
            else:
                self.selected_garnering.add(naam)
                self._style_toggle_button(btn, True)
            
            self.ctrl['garnering'].clear()
            for nm, _pr in items:
                var = tk.BooleanVar(value=(nm in self.selected_garnering))
                self.ctrl['garnering'].append((nm, var))
            self._update_price()
        
        for i, (naam, prijs) in enumerate(items):
            r, c = divmod(i, 5)
            label = f"{naam}" + (f" (+€{prijs:.2f})" if prijs > 0 else "")
            btn = self._create_toggle_button(
                g_frame,
                label,
                naam in self.selected_garnering,
                width=14,
                command=lambda n=naam, b=None: toggle_g(n, b) if b else None
            )
            btn.configure(command=lambda n=naam, b=btn: toggle_g(n, b))
            btn.grid(row=r, column=c, padx=2, pady=2, sticky="w")
        
        if not self.ctrl['garnering']:
            for nm, _pr in items:
                var = tk.BooleanVar(value=(nm in self.selected_garnering))
                self.ctrl['garnering'].append((nm, var))
    
    def _create_volle_kaart_section(self, parent: tk.Frame) -> None:
        """Create volle kaart (loyalty card) section."""
        if not self.is_medium_pizza:
            return
        
        section = self._create_section_frame(parent, "🎫 Volle Kaart")
        
        vk_frame = tk.Frame(section, bg=self.COLORS['bg_section'])
        vk_frame.pack(fill=tk.X, padx=8, pady=4)
        
        check = tk.Checkbutton(
            vk_frame,
            text="Gratis pizza (€0.00) - Volle stempelkaart",
            variable=self.volle_kaart_var,
            font=("Arial", 9, "bold"),
            bg=self.COLORS['bg_section'],
            fg=self.COLORS['success'],
            activebackground=self.COLORS['bg_section'],
            activeforeground=self.COLORS['success'],
            selectcolor="#D1E7DD",
            command=self._update_price
        )
        check.pack(side=tk.LEFT)
    
    def _create_opmerking_section(self, parent: tk.Frame) -> None:
        """Create opmerking (note) section."""
        section = self._create_section_frame(parent, "📝 Opmerking")
        
        opm_frame = tk.Frame(section, bg=self.COLORS['bg_section'])
        opm_frame.pack(fill=tk.X, padx=8, pady=4)
        
        entry = tk.Entry(
            opm_frame,
            textvariable=self.ctrl['opmerking'],
            font=("Arial", 9),
            width=45,
            relief=tk.SOLID,
            bd=1
        )
        entry.pack(fill=tk.X, padx=4, pady=3)
    
    def _create_footer(self, parent: tk.Frame) -> tk.Frame:
        """Create footer with price and action buttons."""
        footer = tk.Frame(parent, bg=self.COLORS['bg_secondary'], relief=tk.RAISED, bd=1, padx=10, pady=8)
        
        # Price display
        price_frame = tk.Frame(footer, bg=self.COLORS['bg_secondary'])
        price_frame.pack(side=tk.LEFT)
        
        tk.Label(
            price_frame,
            text="Totaal:",
            font=("Arial", 10, "bold"),
            bg=self.COLORS['bg_secondary'],
            fg=self.COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(0, 6))
        
        self.price_label = tk.Label(
            price_frame,
            text="€0.00",
            font=("Arial", 12, "bold"),
            bg=self.COLORS['bg_secondary'],
            fg=self.COLORS['success']
        )
        self.price_label.pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = tk.Frame(footer, bg=self.COLORS['bg_secondary'])
        btn_frame.pack(side=tk.RIGHT)
        
        add_btn = tk.Button(
            btn_frame,
            text="➕ Toevoegen",
            font=("Arial", 10, "bold"),
            bg=self.COLORS['success'],
            fg="white",
            activebackground="#157347",
            activeforeground="white",
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            command=self._on_add
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 6))
        
        cancel_btn = tk.Button(
            btn_frame,
            text="❌ Sluiten",
            font=("Arial", 10),
            bg=self.COLORS['danger'],
            fg="white",
            activebackground="#BB2D3B",
            activeforeground="white",
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            command=self._on_close
        )
        cancel_btn.pack(side=tk.LEFT)
        
        return footer
    
    def _create_section_frame(self, parent: tk.Frame, title: str) -> tk.Frame:
        """Create a section frame with title."""
        section = tk.Frame(parent, bg=self.COLORS['bg_section'], relief=tk.RIDGE, bd=1, padx=8, pady=6)
        section.pack(fill=tk.X, pady=4)
        
        title_label = tk.Label(
            section,
            text=title,
            font=("Arial", 9, "bold"),
            bg=self.COLORS['bg_section'],
            fg=self.COLORS['text_primary']
        )
        title_label.pack(anchor="w", pady=(0, 4))
        
        return section
    
    def _create_toggle_button(
        self,
        parent: tk.Frame,
        text: str,
        is_on: bool,
        width: int = 10,
        command: Optional[Callable[[], None]] = None
    ) -> tk.Button:
        """Create a toggle button."""
        btn = tk.Button(
            parent,
            text=text,
            width=width,
            anchor="w",
            padx=6,
            pady=3,
            font=("Arial", 8),
            relief=tk.RAISED,
            bd=1,
            cursor="hand2",
            command=command
        )
        self._style_toggle_button(btn, is_on)
        return btn
    
    def _style_toggle_button(self, btn: tk.Button, is_on: bool) -> None:
        """Style a toggle button based on state."""
        if is_on:
            btn.configure(
                bg=self.COLORS['accent'],
                activebackground="#0B5ED7",
                fg="white",
                activeforeground="white",
                relief=tk.SOLID,
                bd=1,
                highlightthickness=0
            )
        else:
            btn.configure(
                bg="#F3F4F6",
                activebackground="#E9ECEF",
                fg=self.COLORS['text_primary'],
                activeforeground=self.COLORS['text_primary'],
                relief=tk.RAISED,
                bd=1,
                highlightthickness=0
            )
    
    def _update_price(self) -> None:
        """Update the price display."""
        if not self.price_label:
            return
        
        base_price = self.product['prijs']
        extras_price = 0.0
        
        # Add garnering prices
        if 'garnering' in self.ctrl and isinstance(self.extras_config, dict):
            bron_garnering = (
                self.product_extras.get('garnering', self.extras_config.get('garnering', {}))
                if isinstance(self.product_extras, dict) else {}
            )
            if isinstance(bron_garnering, dict):
                for naam in self.selected_garnering:
                    extras_price += float(bron_garnering.get(naam, 0.0))
        
        # Add sauzen toeslag
        extras_price += float(self.ctrl.get('_sauzen_toeslag_cache', 0.0) or 0.0)
        
        # Calculate total
        if self.volle_kaart_var.get():
            total = 0.0  # Gratis
        else:
            total = (base_price + extras_price) * self.ctrl['aantal'].get()
        
        self.price_label.config(text=f"€{total:.2f}")
    
    def _build_extra_keuze(self) -> Dict[str, Any]:
        """Build the extra choices dictionary."""
        extra = {}
        
        if self.is_half_half:
            extra['half_half'] = [self.half1_var.get(), self.half2_var.get()]
        
        if self.ctrl['vlees'].get():
            extra['vlees'] = self.ctrl['vlees'].get()
        
        if self.ctrl['bijgerecht_combos']:
            vals = [v.get() for v in self.ctrl['bijgerecht_combos'] if v.get()]
            if vals:
                extra['bijgerecht'] = vals if len(vals) > 1 else vals[0]
        
        if self.ctrl.get('saus_combos'):
            dup_sauzen = [v.get() for v in self.ctrl['saus_combos'] if v.get()]
            if dup_sauzen:
                extra['sauzen'] = dup_sauzen
            toeslag = float(self.ctrl.get('_sauzen_toeslag_cache', 0.0) or 0.0)
            if toeslag > 0:
                extra['sauzen_toeslag'] = round(toeslag, 2)
        
        if self.ctrl.get('garnering'):
            g_list = [naam for (naam, var) in self.ctrl['garnering'] if var.get()]
            if g_list:
                extra['garnering'] = g_list
        
        if self.volle_kaart_var.get():
            extra['volle_kaart'] = True
        
        return extra
    
    def _on_add(self) -> None:
        """Handle add button click."""
        # Validation
        if self.is_half_half:
            h1_val, h2_val = self.half1_var.get(), self.half2_var.get()
            valid_vals = {str(n) for n in range(1, 50)}
            if not (h1_val in valid_vals and h2_val in valid_vals):
                messagebox.showwarning("Waarschuwing", "Kies twee geldige pizza-nummers voor de Half-Half optie.")
                return
            if h1_val == h2_val:
                messagebox.showwarning("Waarschuwing", "Kies twee verschillende pizza-nummers voor de Half-Half optie.")
                return
        
        # Build result
        extra = self._build_extra_keuze()
        
        # Calculate price
        base_price = self.product['prijs']
        extras_price = 0.0
        
        if 'garnering' in extra and isinstance(self.extras_config, dict):
            bron_garnering = (
                self.product_extras.get('garnering', self.extras_config.get('garnering', {}))
                if isinstance(self.product_extras, dict) else {}
            )
            if isinstance(bron_garnering, dict):
                for naam in extra.get('garnering', []):
                    extras_price += float(bron_garnering.get(naam, 0.0))
        
        extras_price += float(extra.get('sauzen_toeslag', 0.0))
        
        if self.volle_kaart_var.get():
            final_price = 0.0
        else:
            final_price = base_price + extras_price
        
        result = {
            'categorie': self.category,
            'product': self.product['naam'],
            'aantal': self.ctrl['aantal'].get(),
            'prijs': final_price,
            'base_price': base_price,
            'extras': extra,
            'opmerking': self.ctrl['opmerking'].get()
        }
        
        self.on_add(result)
        self._on_close()
    
    def _on_close(self) -> None:
        """Handle close event."""
        if self.on_close:
            self.on_close()
        if self.window:
            self.window.destroy()

