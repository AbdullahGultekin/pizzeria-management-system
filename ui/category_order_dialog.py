"""
Enhanced Category Order Dialog

Modern, visual interface for reordering categories with drag & drop support.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Callable, Optional
from logging_config import get_logger

logger = get_logger("pizzeria.ui.category_order")


class CategoryOrderDialog:
    """Enhanced category order dialog with visual feedback."""
    
    COLORS = {
        'bg_primary': '#F8F9FA',
        'bg_item': '#FFFFFF',
        'bg_selected': '#E3F2FD',
        'bg_hover': '#F5F5F5',
        'border': '#DEE2E6',
        'border_selected': '#0D6EFD',
        'text_primary': '#212529',
        'text_secondary': '#6C757D',
        'accent': '#0D6EFD',
        'success': '#198754',
    }
    
    def __init__(
        self,
        parent: tk.Tk,
        categories: List[str],
        on_save: Callable[[List[str]], None]
    ):
        """
        Initialize category order dialog.
        
        Args:
            parent: Parent window
            categories: List of category names
            on_save: Callback function called with new order when saved
        """
        self.parent = parent
        self.original_categories = categories.copy()
        self.categories = categories.copy()
        self.on_save = on_save
        self.selected_index: Optional[int] = None
        self.drag_start_index: Optional[int] = None
        
        self.top = tk.Toplevel(parent)
        self.top.title("📋 Categorie Volgorde Aanpassen")
        self.top.transient(parent)
        self.top.grab_set()
        self.top.geometry("500x600")
        self.top.configure(bg=self.COLORS['bg_primary'])
        
        self._create_ui()
        self._load_categories()
    
    def _create_ui(self) -> None:
        """Create the UI components."""
        # Header
        header = tk.Frame(self.top, bg=self.COLORS['bg_primary'], pady=15)
        header.pack(fill=tk.X, padx=20)
        
        title = tk.Label(
            header,
            text="📋 Categorie Volgorde",
            font=("Arial", 16, "bold"),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary']
        )
        title.pack()
        
        subtitle = tk.Label(
            header,
            text="Sleep items om de volgorde te wijzigen of gebruik de knoppen",
            font=("Arial", 9),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_secondary']
        )
        subtitle.pack(pady=(5, 0))
        
        # Main content frame
        content_frame = tk.Frame(self.top, bg=self.COLORS['bg_primary'], padx=20, pady=10)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        list_frame = tk.Frame(content_frame, bg=self.COLORS['bg_primary'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(
            list_frame,
            font=("Arial", 11),
            selectbackground=self.COLORS['bg_selected'],
            selectforeground=self.COLORS['text_primary'],
            activestyle="none",
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            yscrollcommand=scrollbar.set,
            height=18
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Bind events
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        self.listbox.bind("<Button-1>", self._on_click)
        self.listbox.bind("<B1-Motion>", self._on_drag)
        self.listbox.bind("<ButtonRelease-1>", self._on_release)
        self.listbox.bind("<Double-Button-1>", lambda e: None)  # Disable double-click
        
        # Control buttons frame
        controls_frame = tk.Frame(content_frame, bg=self.COLORS['bg_primary'], pady=15)
        controls_frame.pack(fill=tk.X)
        
        # Button container
        btn_container = tk.Frame(controls_frame, bg=self.COLORS['bg_primary'])
        btn_container.pack()
        
        # Move buttons
        move_frame = tk.Frame(btn_container, bg=self.COLORS['bg_primary'])
        move_frame.pack(side=tk.LEFT, padx=5)
        
        up_btn = tk.Button(
            move_frame,
            text="⬆️ Omhoog",
            font=("Arial", 10, "bold"),
            bg=self.COLORS['accent'],
            fg="white",
            activebackground="#0B5ED7",
            activeforeground="white",
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=self._move_up
        )
        up_btn.pack(side=tk.LEFT, padx=2)
        
        down_btn = tk.Button(
            move_frame,
            text="⬇️ Omlaag",
            font=("Arial", 10, "bold"),
            bg=self.COLORS['accent'],
            fg="white",
            activebackground="#0B5ED7",
            activeforeground="white",
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=self._move_down
        )
        down_btn.pack(side=tk.LEFT, padx=2)
        
        # Reset button
        reset_btn = tk.Button(
            btn_container,
            text="🔄 Reset",
            font=("Arial", 10),
            bg="#FFC107",
            fg="#212529",
            activebackground="#FFB300",
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=self._reset_order
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = tk.Frame(self.top, bg=self.COLORS['bg_primary'], pady=15)
        action_frame.pack(fill=tk.X, padx=20)
        
        save_btn = tk.Button(
            action_frame,
            text="💾 Opslaan",
            font=("Arial", 11, "bold"),
            bg=self.COLORS['success'],
            fg="white",
            activebackground="#157347",
            activeforeground="white",
            relief="flat",
            padx=25,
            pady=10,
            cursor="hand2",
            command=self._save
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            action_frame,
            text="❌ Annuleren",
            font=("Arial", 11),
            bg="#DC3545",
            fg="white",
            activebackground="#BB2D3B",
            activeforeground="white",
            relief="flat",
            padx=25,
            pady=10,
            cursor="hand2",
            command=self.top.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(
            action_frame,
            text="",
            font=("Arial", 9),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_secondary']
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
    
    def _load_categories(self) -> None:
        """Load categories into listbox."""
        self.listbox.delete(0, tk.END)
        for i, cat in enumerate(self.categories):
            # Display with number for visual clarity
            self.listbox.insert(tk.END, f"{i+1}. {cat}")
    
    def _on_select(self, event: tk.Event) -> None:
        """Handle listbox selection."""
        selection = self.listbox.curselection()
        if selection:
            self.selected_index = selection[0]
            self._update_status()
    
    def _on_click(self, event: tk.Event) -> None:
        """Handle mouse click for drag start."""
        index = self.listbox.nearest(event.y)
        if index >= 0:
            self.drag_start_index = index
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)
            self.selected_index = index
    
    def _on_drag(self, event: tk.Event) -> None:
        """Handle mouse drag."""
        if self.drag_start_index is None:
            return
        
        index = self.listbox.nearest(event.y)
        if index >= 0 and index != self.drag_start_index:
            # Visual feedback during drag
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)
    
    def _on_release(self, event: tk.Event) -> None:
        """Handle mouse release - perform move."""
        if self.drag_start_index is None:
            return
        
        index = self.listbox.nearest(event.y)
        if index >= 0 and index != self.drag_start_index:
            # Move item in categories list
            item = self.categories.pop(self.drag_start_index)
            self.categories.insert(index, item)
            self._load_categories()
            self.listbox.selection_set(index)
            self.selected_index = index
            self._update_status()
        
        self.drag_start_index = None
    
    def _move_up(self) -> None:
        """Move selected item up."""
        if self.selected_index is None or self.selected_index == 0:
            return
        
        # Swap items
        self.categories[self.selected_index], self.categories[self.selected_index - 1] = \
            self.categories[self.selected_index - 1], self.categories[self.selected_index]
        
        self._load_categories()
        self.listbox.selection_set(self.selected_index - 1)
        self.selected_index -= 1
        self._update_status()
    
    def _move_down(self) -> None:
        """Move selected item down."""
        if self.selected_index is None or self.selected_index >= len(self.categories) - 1:
            return
        
        # Swap items
        self.categories[self.selected_index], self.categories[self.selected_index + 1] = \
            self.categories[self.selected_index + 1], self.categories[self.selected_index]
        
        self._load_categories()
        self.listbox.selection_set(self.selected_index + 1)
        self.selected_index += 1
        self._update_status()
    
    def _reset_order(self) -> None:
        """Reset to original order."""
        if messagebox.askyesno(
            "Reset Bevestigen",
            "Weet u zeker dat u de volgorde wilt resetten naar de originele volgorde?"
        ):
            self.categories = self.original_categories.copy()
            self._load_categories()
            self.selected_index = None
            self.listbox.selection_clear(0, tk.END)
            self._update_status()
    
    def _update_status(self) -> None:
        """Update status label."""
        if self.selected_index is not None:
            cat_name = self.categories[self.selected_index]
            self.status_label.config(
                text=f"Geselecteerd: {cat_name} (positie {self.selected_index + 1})",
                fg=self.COLORS['accent']
            )
        else:
            self.status_label.config(text="Selecteer een categorie om te verplaatsen", fg=self.COLORS['text_secondary'])
    
    def _save(self) -> None:
        """Save the new order."""
        if self.categories != self.original_categories:
            self.on_save(self.categories)
            messagebox.showinfo("Succes", "Categorie volgorde opgeslagen!")
        self.top.destroy()

