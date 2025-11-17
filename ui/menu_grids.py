"""
Modern Menu Grids Component

Enhanced category and product grids with modern styling, hover effects,
and better visual hierarchy.
"""

import tkinter as tk
from typing import Dict, List, Any, Optional, Callable
from logging_config import get_logger

logger = get_logger("pizzeria.ui.menu_grids")


class ModernMenuGrids:
    """Modern menu grids with enhanced styling and UX."""
    
    # Modern color scheme
    COLORS = {
        'bg_primary': '#F8F9FA',
        'bg_secondary': '#FFFFFF',
        'bg_card': '#FFFFFF',
        'bg_card_hover': '#F0F4F8',
        'border': '#E1E8ED',
        'border_hover': '#0D6EFD',
        'text_primary': '#212529',
        'text_secondary': '#6C757D',
        'text_price': '#198754',
        'accent': '#0D6EFD',
        'accent_hover': '#0B5ED7',
        'shadow': '#E9ECEF',
        'success': '#198754',
        'warning': '#FFC107',
    }
    
    # Category colors - modern gradient-inspired palette
    CATEGORY_COLORS = [
        '#E3F2FD',  # Light Blue
        '#E8F5E9',  # Light Green
        '#FFF3E0',  # Light Orange
        '#FCE4EC',  # Light Pink
        '#E1BEE7',  # Light Purple
        '#F3E5F5',  # Light Lavender
        '#E0F2F1',  # Light Teal
        '#FFF9C4',  # Light Yellow
        '#FFE0B2',  # Light Peach
        '#BBDEFB',  # Sky Blue
    ]
    
    def __init__(
        self,
        parent: tk.Frame,
        on_category_select: Callable[[str], None],
        on_product_select: Callable[[Dict[str, Any]], None]
    ):
        """
        Initialize modern menu grids.
        
        Args:
            parent: Parent frame
            on_category_select: Callback for category selection
            on_product_select: Callback for product selection
        """
        self.parent = parent
        self.on_category_select = on_category_select
        self.on_product_select = on_product_select
        
        # Current selection
        self.selected_category: Optional[str] = None
        self.category_buttons: Dict[str, tk.Button] = {}
        
        # Widget references
        self.category_frame: Optional[tk.Frame] = None
        self.product_frame: Optional[tk.Frame] = None
        self.product_title: Optional[tk.Label] = None
    
    def create_category_grid(
        self,
        categories: List[str],
        columns: int = 5,
        parent_frame: Optional[tk.Frame] = None
    ) -> tk.Frame:
        """
        Create modern category button grid.
        
        Args:
            categories: List of category names
            columns: Number of columns
            parent_frame: Optional parent frame (creates new if None)
            
        Returns:
            Frame containing category buttons
        """
        if parent_frame is None:
            self.category_frame = tk.Frame(self.parent, bg=self.COLORS['bg_primary'], padx=4, pady=4)
        else:
            self.category_frame = tk.Frame(parent_frame, bg=self.COLORS['bg_primary'], padx=4, pady=4)
        
        # Clear existing buttons
        for widget in self.category_frame.winfo_children():
            widget.destroy()
        self.category_buttons.clear()
        
        # Auto-calculate columns based on available width if parent exists
        if parent_frame:
            try:
                parent_frame.update_idletasks()
                available_width = parent_frame.winfo_width()
                if available_width > 100:  # Only if we have a valid width
                    # Calculate optimal columns: each button needs ~120px + padding
                    optimal_cols = max(1, min(columns, available_width // 130))
                    columns = optimal_cols
            except:
                pass  # Use provided columns if calculation fails
        
        # Configure grid
        for c in range(columns):
            self.category_frame.grid_columnconfigure(c, weight=1, uniform="cat_col")
        
        # Create category buttons with compact sizing
        for i, cat_name in enumerate(categories):
            row, col = divmod(i, columns)
            color = self.CATEGORY_COLORS[i % len(self.CATEGORY_COLORS)]
            
            # Create button with compact styling
            btn = tk.Button(
                self.category_frame,
                text=cat_name.upper(),
                font=("Arial", 9, "bold"),
                bg=color,
                fg=self.COLORS['text_primary'],
                activebackground=self._darken_color(color, 0.1),
                activeforeground=self.COLORS['text_primary'],
                relief="flat",
                borderwidth=1,
                highlightbackground=color,
                highlightthickness=1,
                padx=8,
                pady=6,
                cursor="hand2",
                command=lambda cn=cat_name: self._on_category_click(cn)
            )
            
            # Store original color for later use
            btn.original_color = color
            
            # Add hover effects
            self._add_button_hover(btn, color)
            
            # Grid placement
            btn.grid(
                row=row,
                column=col,
                sticky="nsew",
                padx=2,
                pady=2
            )
            
            self.category_buttons[cat_name] = btn
        
        return self.category_frame
    
    def create_product_grid(
        self,
        products: List[Dict[str, Any]],
        is_pizza_category: bool = False,
        parent_frame: Optional[tk.Frame] = None
    ) -> tk.Frame:
        """
        Create modern product card grid with responsive sizing.
        
        Args:
            products: List of product dictionaries
            is_pizza_category: Whether this is a pizza category
            parent_frame: Optional parent frame (creates new if None)
            
        Returns:
            Frame containing product cards
        """
        if parent_frame is None:
            self.product_frame = tk.Frame(self.parent, bg=self.COLORS['bg_primary'], padx=4, pady=4)
        else:
            self.product_frame = tk.Frame(parent_frame, bg=self.COLORS['bg_primary'], padx=4, pady=4)
        
        # Clear existing products
        for widget in self.product_frame.winfo_children():
            widget.destroy()
        
        if not products:
            no_products_label = tk.Label(
                self.product_frame,
                text="Geen producten beschikbaar",
                font=("Arial", 11),
                fg=self.COLORS['text_secondary'],
                bg=self.COLORS['bg_primary']
            )
            no_products_label.pack(pady=20)
            return self.product_frame
        
        # Auto-calculate columns based on available width
        # More columns for compact cards
        columns = 8 if is_pizza_category else 6
        if parent_frame:
            try:
                parent_frame.update_idletasks()
                available_width = parent_frame.winfo_width()
                if available_width > 100:  # Only if we have a valid width
                    # Calculate optimal columns: compact cards need ~60-80px + padding
                    card_width = 60 if is_pizza_category else 80
                    optimal_cols = max(3, min(columns, available_width // (card_width + 10)))
                    columns = optimal_cols
            except:
                pass  # Use default columns if calculation fails
        
        # Configure grid
        for c in range(columns):
            self.product_frame.grid_columnconfigure(c, weight=1, uniform="prod_col")
        
        # Create product cards
        for i, product in enumerate(products):
            row, col = divmod(i, columns)
            
            card = self._create_product_card(product, is_pizza_category)
            card.grid(
                row=row,
                column=col,
                sticky="nsew",
                padx=2,
                pady=2
            )
        
        return self.product_frame
    
    def _create_product_card(
        self,
        product: Dict[str, Any],
        is_pizza: bool = False
    ) -> tk.Frame:
        """
        Create a compact product card.
        
        Args:
            product: Product dictionary
            is_pizza: Whether this is a pizza product
            
        Returns:
            Product card frame
        """
        # Main card frame - very compact
        card = tk.Frame(
            self.product_frame,
            bg=self.COLORS['bg_card'],
            relief="flat",
            borderwidth=1,
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        
        # Card content frame - minimal padding
        content = tk.Frame(card, bg=self.COLORS['bg_card'], padx=4, pady=4)
        content.pack(fill=tk.BOTH, expand=True)
        
        # For pizzas: show only number (1-50)
        if is_pizza:
            pizza_num = product.get('pizza_num', '')
            if not pizza_num:
                # Try to extract from name
                name_text = product.get('naam', '')
                if '.' in name_text:
                    pizza_num = name_text.split('.')[0].strip()
                elif name_text.startswith('#'):
                    pizza_num = name_text.split(' ', 1)[0].lstrip('#')
                elif name_text and name_text[0].isdigit():
                    # Extract first number from name
                    import re
                    match = re.match(r'^(\d+)', name_text)
                    if match:
                        pizza_num = match.group(1)
            
            # Display only the number
            if pizza_num:
                try:
                    num = int(pizza_num)
                    if 1 <= num <= 50:
                        display_text = str(num)
                    else:
                        display_text = pizza_num
                except:
                    display_text = pizza_num
            else:
                display_text = "?"
            
            # Compact number display
            name_label = tk.Label(
                content,
                text=display_text,
                font=("Arial", 14, "bold"),
                bg=self.COLORS['bg_card'],
                fg=self.COLORS['text_primary'],
                justify="center"
            )
            name_label.pack(fill=tk.BOTH, expand=True, pady=2)
        else:
            # For non-pizza products: show name only (no price)
            name_text = product.get('naam', 'Onbekend')
            
            # Truncate long names
            if len(name_text) > 15:
                name_text = name_text[:12] + "..."
            
            name_label = tk.Label(
                content,
                text=name_text,
                font=("Arial", 8, "bold"),
                bg=self.COLORS['bg_card'],
                fg=self.COLORS['text_primary'],
                wraplength=80,
                justify="center"
            )
            name_label.pack(pady=(2, 0))
        
        # Add button - very compact, fills the card
        add_btn = tk.Button(
            content,
            text="➕",
            font=("Arial", 12, "bold"),
            bg=self.COLORS['accent'],
            fg="white",
            activebackground=self.COLORS['accent_hover'],
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            padx=2,
            pady=2,
            cursor="hand2",
            command=lambda p=product: self._on_product_click(p)
        )
        if is_pizza:
            # For pizzas, button is smaller
            add_btn.pack(fill=tk.X, pady=(2, 0))
        else:
            add_btn.pack(fill=tk.X, pady=(4, 0))
        
        # Add hover effect to entire card
        self._add_card_hover(card, content, name_label, None, add_btn)
        
        return card
    
    def _add_button_hover(self, button: tk.Button, base_color: str) -> None:
        """Add hover effects to category button."""
        def on_enter(e):
            button.config(
                bg=self._darken_color(base_color, 0.15),
                relief="raised",
                borderwidth=1
            )
        
        def on_leave(e):
            button.config(
                bg=base_color,
                relief="flat",
                borderwidth=0
            )
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def _add_card_hover(
        self,
        card: tk.Frame,
        content: tk.Frame,
        name_label: tk.Label,
        price_label: Optional[tk.Label],
        add_btn: tk.Button
    ) -> None:
        """Add hover effects to product card."""
        def on_enter(e):
            card.config(
                bg=self.COLORS['bg_card_hover'],
                highlightbackground=self.COLORS['border_hover'],
                highlightthickness=2
            )
            content.config(bg=self.COLORS['bg_card_hover'])
            if name_label:
                name_label.config(bg=self.COLORS['bg_card_hover'])
            if price_label:
                price_label.config(bg=self.COLORS['bg_card_hover'])
            # Update other labels if they exist
            for widget in content.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(bg=self.COLORS['bg_card_hover'])
        
        def on_leave(e):
            card.config(
                bg=self.COLORS['bg_card'],
                highlightbackground=self.COLORS['border'],
                highlightthickness=1
            )
            content.config(bg=self.COLORS['bg_card'])
            if name_label:
                name_label.config(bg=self.COLORS['bg_card'])
            if price_label:
                price_label.config(bg=self.COLORS['bg_card'])
            # Update other labels if they exist
            for widget in content.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(bg=self.COLORS['bg_card'])
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        content.bind("<Enter>", on_enter)
        content.bind("<Leave>", on_leave)
    
    def _on_category_click(self, category_name: str) -> None:
        """Handle category button click."""
        # Update visual selection
        self._update_category_selection(category_name)
        
        # Call callback
        if self.on_category_select:
            self.on_category_select(category_name)
    
    def _on_product_click(self, product: Dict[str, Any]) -> None:
        """Handle product card click."""
        if self.on_product_select:
            self.on_product_select(product)
    
    def _update_category_selection(self, category_name: str) -> None:
        """Update visual selection state of category buttons."""
        self.selected_category = category_name
        
        for name, button in self.category_buttons.items():
            if name == category_name:
                # Highlight selected - use darker background and accent border
                original_color = getattr(button, 'original_color', button.cget('bg'))
                button.config(
                    relief="raised",
                    borderwidth=2,
                    highlightbackground=self.COLORS['accent'],
                    highlightthickness=2,
                    bg=self._darken_color(original_color, 0.15)
                )
            else:
                # Reset others - restore original color
                original_color = getattr(button, 'original_color', button.cget('bg'))
                button.config(
                    relief="flat",
                    borderwidth=1,
                    highlightbackground=original_color,
                    highlightthickness=1,
                    bg=original_color
                )
    
    def _darken_color(self, hex_color: str, factor: float) -> str:
        """
        Darken a hex color by a factor.
        
        Args:
            hex_color: Hex color string (e.g., "#FF0000")
            factor: Darkening factor (0.0 to 1.0)
            
        Returns:
            Darkened hex color string
        """
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Darken
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color
    
    def set_category_selection(self, category_name: str) -> None:
        """Set the selected category programmatically."""
        self._update_category_selection(category_name)

