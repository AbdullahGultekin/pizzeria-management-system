"""Tab management for notebook interface."""

import tkinter as tk
from typing import Dict, Any, Optional
from tkinter import ttk


class TabManager:
    """Manages tabs in the notebook interface."""
    
    def __init__(self, notebook: ttk.Notebook):
        """
        Initialize tab manager.
        
        Args:
            notebook: The ttk.Notebook widget to manage
        """
        self.notebook = notebook
        self.tabs_map: Dict[str, Dict[str, Any]] = {}
    
    def add_tab(self, title: str) -> tk.Frame:
        """
        Add a new tab to the notebook.
        
        Args:
            title: Tab title
            
        Returns:
            Frame widget for the tab
        """
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        self.tabs_map[title] = {"frame": frame, "loaded": False}
        return frame
    
    def load_tab_content(
        self,
        title: str,
        load_callbacks: Dict[str, callable]
    ) -> None:
        """
        Load content for a tab when it's first selected (OPTIMIZED - always async for fast tab switching).
        
        Args:
            title: Tab title
            load_callbacks: Dictionary mapping tab titles to callback functions
        """
        info = self.tabs_map.get(title)
        if not info or info["loaded"]:
            return
        
        parent = info["frame"]
        callback = load_callbacks.get(title)
        if callback:
            # Show loading indicator immediately for better UX
            self._show_loading_indicator(parent, title)
            
            # Always load asynchronously for fast tab switching (non-blocking)
            # Use after(1) instead of after_idle for faster response
            self.notebook.after(1, lambda: self._load_tab_async(title, parent, callback, info))
    
    def _show_loading_indicator(self, parent: tk.Frame, title: str) -> None:
        """Show a loading indicator while tab content is loading."""
        # Clear existing content
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Show simple loading message
        loading_label = tk.Label(
            parent,
            text=f"Laden {title}...",
            font=("Arial", 12),
            fg="#666"
        )
        loading_label.pack(expand=True)
    
    def _load_tab_async(self, title: str, parent: tk.Frame, callback: callable, info: Dict[str, Any]) -> None:
        """Load tab content asynchronously (non-blocking)."""
        try:
            # Clear loading indicator if still present
            for widget in parent.winfo_children():
                if isinstance(widget, tk.Label) and "Laden" in widget.cget("text"):
                    widget.destroy()
                    break
            
            # Load actual content
            callback(parent)
            info["loaded"] = True
        except Exception as e:
            from logging_config import get_logger
            logger = get_logger("pizzeria.ui.tab_manager")
            logger.exception(f"Error loading tab {title}: {e}")
            
            # Show error message
            for widget in parent.winfo_children():
                widget.destroy()
            error_label = tk.Label(
                parent,
                text=f"Fout bij laden {title}:\n{str(e)}",
                font=("Arial", 10),
                fg="#DC3545",
                justify=tk.LEFT
            )
            error_label.pack(expand=True, padx=20, pady=20)
            info["loaded"] = True
    
    def on_tab_changed(
        self,
        event: tk.Event,
        load_callbacks: Dict[str, callable]
    ) -> None:
        """
        Handle tab change event.
        
        Args:
            event: Tkinter event
            load_callbacks: Dictionary mapping tab titles to callback functions
        """
        current = event.widget.select()
        tab_id = event.widget.index(current)
        tab_text = event.widget.tab(tab_id, "text")
        self.load_tab_content(tab_text, load_callbacks)



