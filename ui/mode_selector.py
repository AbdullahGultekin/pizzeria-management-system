"""
Application Mode Selector

Dialog to choose between Front (Kassa) and Back (Admin) mode at startup.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Literal, Optional
from logging_config import get_logger

logger = get_logger("pizzeria.ui.mode_selector")


class ModeSelector:
    """Dialog to select application mode (Front/Back)."""
    
    COLORS = {
        'bg_primary': '#F5F7FA',
        'bg_front': '#E8F4FD',
        'bg_back': '#F5E8F5',
        'bg_button_front': '#2196F3',
        'bg_button_back': '#9C27B0',
        'bg_button_front_hover': '#1976D2',
        'bg_button_back_hover': '#7B1FA2',
        'text_primary': '#1A1A1A',
        'text_secondary': '#6C757D',
        'border': '#E0E0E0',
        'shadow': '#00000020',
    }
    
    def __init__(self, parent: tk.Tk) -> None:
        """
        Initialize mode selector dialog.
        
        Args:
            parent: Parent window (root)
        """
        self.parent = parent
        self.selected_mode: Optional[Literal["front", "back"]] = None
        self.dialog: Optional[tk.Toplevel] = None
    
    def show(self) -> Optional[Literal["front", "back"]]:
        """
        Show mode selector dialog and return selected mode.
        
        Returns:
            "front" or "back" or None if cancelled
        """
        # Use parent as dialog if it's a Tk root, otherwise create Toplevel
        if isinstance(self.parent, tk.Tk):
            # Use parent directly as the dialog window
            self.dialog = self.parent
            self.dialog.title("🔐 Selecteer Applicatie Modus")
        else:
            # Create Toplevel dialog
            self.parent.update_idletasks()
            self.dialog = tk.Toplevel(self.parent)
            self.dialog.title("🔐 Selecteer Applicatie Modus")
            self.dialog.transient(self.parent)
            self.dialog.grab_set()
        
        self.dialog.resizable(False, False)
        
        # Center dialog on screen - make it wider and taller for professional look
        width, height = 900, 550
        sw, sh = self.dialog.winfo_screenwidth(), self.dialog.winfo_screenheight()
        x, y = (sw // 2) - (width // 2), (sh // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Set window background
        self.dialog.configure(bg=self.COLORS['bg_primary'])
        
        # Prevent closing without selection
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Create UI
        self._create_ui()
        
        # Ensure dialog is visible and on top
        self.dialog.update_idletasks()
        self.dialog.lift()
        self.dialog.focus_force()
        
        # Make sure buttons are clickable - update after UI creation
        self.dialog.update()
        
        # Wait for user selection
        if isinstance(self.parent, tk.Tk):
            # If using parent as dialog, run mainloop
            self.dialog.mainloop()
        else:
            # If using Toplevel, wait for window
            self.dialog.wait_window()
        
        return self.selected_mode
    
    def _create_ui(self) -> None:
        """Create the UI components."""
        # Main container with gradient-like background
        main_frame = tk.Frame(self.dialog, bg=self.COLORS['bg_primary'], padx=40, pady=40)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header section with better styling
        header_frame = tk.Frame(main_frame, bg=self.COLORS['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 40))
        
        # Title with better typography
        title_label = tk.Label(
            header_frame,
            text="Selecteer Applicatie Modus",
            font=("Arial", 24, "bold"),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary']
        )
        title_label.pack(pady=(0, 8))
        
        # Subtitle with better styling
        subtitle_label = tk.Label(
            header_frame,
            text="Kies de modus waarin u wilt werken",
            font=("Arial", 12),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_secondary']
        )
        subtitle_label.pack()
        
        # Mode selection cards container - side by side
        cards_frame = tk.Frame(main_frame, bg=self.COLORS['bg_primary'])
        cards_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Front mode card - left side (professional card design)
        front_frame = tk.Frame(
            cards_frame, 
            bg=self.COLORS['bg_front'], 
            relief=tk.FLAT,
            bd=0,
            padx=30,
            pady=35
        )
        front_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Add visual border effect
        front_border = tk.Frame(front_frame, bg="#2196F3", height=4)
        front_border.pack(fill=tk.X, side=tk.TOP)
        
        # Icon with better styling
        icon_frame = tk.Frame(front_frame, bg=self.COLORS['bg_front'])
        icon_frame.pack(pady=(20, 20))
        
        front_icon = tk.Label(
            icon_frame,
            text="🛒",
            font=("Arial", 64),
            bg=self.COLORS['bg_front']
        )
        front_icon.pack()
        
        # Title with better styling
        front_title = tk.Label(
            front_frame,
            text="Kassa Modus",
            font=("Arial", 20, "bold"),
            bg=self.COLORS['bg_front'],
            fg=self.COLORS['text_primary']
        )
        front_title.pack(pady=(0, 12))
        
        # Description with better formatting
        desc_frame = tk.Frame(front_frame, bg=self.COLORS['bg_front'])
        desc_frame.pack(pady=(0, 25))
        
        front_desc = tk.Label(
            desc_frame,
            text="Bestellen\nKoeriers\nGeschiedenis",
            font=("Arial", 11),
            bg=self.COLORS['bg_front'],
            fg=self.COLORS['text_secondary'],
            justify=tk.CENTER
        )
        front_desc.pack()
        
        def select_front(event=None):
            """Callback for front mode button."""
            logger.info("Front button clicked")
            self._select_mode("front")
        
        def on_front_enter(e):
            """Hover effect for front card."""
            front_frame.config(bg="#D6EBFC")
            for widget in [icon_frame, front_title, desc_frame, front_desc]:
                widget.config(bg="#D6EBFC")
            front_icon.config(bg="#D6EBFC")
            front_btn.config(bg=self.COLORS['bg_button_front_hover'])
        
        def on_front_leave(e):
            """Leave hover effect for front card."""
            front_frame.config(bg=self.COLORS['bg_front'])
            for widget in [icon_frame, front_title, desc_frame, front_desc]:
                widget.config(bg=self.COLORS['bg_front'])
            front_icon.config(bg=self.COLORS['bg_front'])
            front_btn.config(bg=self.COLORS['bg_button_front'])
        
        front_btn = tk.Button(
            front_frame,
            text="Kassa Modus Starten",
            font=("Arial", 12, "bold"),
            bg=self.COLORS['bg_button_front'],
            fg="white",
            activebackground=self.COLORS['bg_button_front_hover'],
            activeforeground="white",
            relief=tk.FLAT,
            bd=0,
            padx=30,
            pady=14,
            cursor="hand2",
            command=select_front,
            state=tk.NORMAL
        )
        front_btn.pack()
        
        # Bind hover effects
        front_frame.bind("<Enter>", on_front_enter)
        front_frame.bind("<Leave>", on_front_leave)
        
        # Also bind click to the frame for easier clicking
        front_frame.bind("<Button-1>", select_front)
        front_icon.bind("<Button-1>", select_front)
        front_title.bind("<Button-1>", select_front)
        front_desc.bind("<Button-1>", select_front)
        icon_frame.bind("<Button-1>", select_front)
        desc_frame.bind("<Button-1>", select_front)
        
        # Make frame elements show hand cursor
        for widget in [front_frame, front_icon, front_title, front_desc, icon_frame, desc_frame]:
            widget.bind("<Enter>", lambda e, w=widget: (on_front_enter(e), w.config(cursor="hand2")))
            widget.bind("<Leave>", lambda e, w=widget: (on_front_leave(e), w.config(cursor="")))
        
        # Back mode card - right side (professional card design)
        back_frame = tk.Frame(
            cards_frame, 
            bg=self.COLORS['bg_back'], 
            relief=tk.FLAT,
            bd=0,
            padx=30,
            pady=35
        )
        back_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0))
        
        # Add visual border effect
        back_border = tk.Frame(back_frame, bg="#9C27B0", height=4)
        back_border.pack(fill=tk.X, side=tk.TOP)
        
        # Icon with better styling
        back_icon_frame = tk.Frame(back_frame, bg=self.COLORS['bg_back'])
        back_icon_frame.pack(pady=(20, 20))
        
        back_icon = tk.Label(
            back_icon_frame,
            text="⚙️",
            font=("Arial", 64),
            bg=self.COLORS['bg_back']
        )
        back_icon.pack()
        
        # Title with better styling
        back_title = tk.Label(
            back_frame,
            text="Admin Modus",
            font=("Arial", 20, "bold"),
            bg=self.COLORS['bg_back'],
            fg=self.COLORS['text_primary']
        )
        back_title.pack(pady=(0, 12))
        
        # Description with better formatting
        back_desc_frame = tk.Frame(back_frame, bg=self.COLORS['bg_back'])
        back_desc_frame.pack(pady=(0, 25))
        
        back_desc = tk.Label(
            back_desc_frame,
            text="Menu Management\nKlant Management\nExtras Management\nVoorraad\nRapportage\nBackup",
            font=("Arial", 11),
            bg=self.COLORS['bg_back'],
            fg=self.COLORS['text_secondary'],
            justify=tk.CENTER
        )
        back_desc.pack()
        
        def select_back(event=None):
            """Callback for back mode button."""
            logger.info("Back button clicked")
            self._select_mode("back")
        
        def on_back_enter(e):
            """Hover effect for back card."""
            back_frame.config(bg="#F0D6F0")
            for widget in [back_icon_frame, back_title, back_desc_frame, back_desc]:
                widget.config(bg="#F0D6F0")
            back_icon.config(bg="#F0D6F0")
            back_btn.config(bg=self.COLORS['bg_button_back_hover'])
        
        def on_back_leave(e):
            """Leave hover effect for back card."""
            back_frame.config(bg=self.COLORS['bg_back'])
            for widget in [back_icon_frame, back_title, back_desc_frame, back_desc]:
                widget.config(bg=self.COLORS['bg_back'])
            back_icon.config(bg=self.COLORS['bg_back'])
            back_btn.config(bg=self.COLORS['bg_button_back'])
        
        back_btn = tk.Button(
            back_frame,
            text="Admin Modus Starten",
            font=("Arial", 12, "bold"),
            bg=self.COLORS['bg_button_back'],
            fg="white",
            activebackground=self.COLORS['bg_button_back_hover'],
            activeforeground="white",
            relief=tk.FLAT,
            bd=0,
            padx=30,
            pady=14,
            cursor="hand2",
            command=select_back,
            state=tk.NORMAL
        )
        back_btn.pack()
        
        # Bind hover effects
        back_frame.bind("<Enter>", on_back_enter)
        back_frame.bind("<Leave>", on_back_leave)
        
        # Also bind click to the frame for easier clicking
        back_frame.bind("<Button-1>", select_back)
        back_icon.bind("<Button-1>", select_back)
        back_title.bind("<Button-1>", select_back)
        back_desc.bind("<Button-1>", select_back)
        back_icon_frame.bind("<Button-1>", select_back)
        back_desc_frame.bind("<Button-1>", select_back)
        
        # Make frame elements show hand cursor
        for widget in [back_frame, back_icon, back_title, back_desc, back_icon_frame, back_desc_frame]:
            widget.bind("<Enter>", lambda e, w=widget: (on_back_enter(e), w.config(cursor="hand2")))
            widget.bind("<Leave>", lambda e, w=widget: (on_back_leave(e), w.config(cursor="")))
    
    def _select_mode(self, mode: Literal["front", "back"]) -> None:
        """
        Select mode and close dialog.
        
        Args:
            mode: Selected mode ("front" or "back")
        """
        logger.info(f"Mode selected: {mode}")
        self.selected_mode = mode
        
        if self.dialog:
            # If using parent as dialog (Tk root), quit mainloop
            if isinstance(self.dialog, tk.Tk):
                logger.info("Quitting mainloop for Tk root")
                self.dialog.quit()
            else:
                # If using Toplevel, destroy it
                logger.info("Destroying Toplevel dialog")
                self.dialog.destroy()

