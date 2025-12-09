"""
Update checker UI module voor de Pizzeria Management System.
"""
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional
import webbrowser
from utils.updater import UpdateChecker, check_for_updates_async
from logging_config import get_logger

logger = get_logger("pizzeria.update_checker")


def show_update_dialog(parent: tk.Tk, update_info: dict):
    """
    Show update available dialog.
    
    Args:
        parent: Parent window
        update_info: Dictionary with update information
    """
    dialog = tk.Toplevel(parent)
    dialog.title("Update Beschikbaar")
    dialog.transient(parent)
    dialog.grab_set()
    dialog.geometry("600x400")
    
    # Header
    header_frame = tk.Frame(dialog, bg="#4CAF50", pady=10)
    header_frame.pack(fill=tk.X)
    
    tk.Label(
        header_frame,
        text="🔄 Update Beschikbaar!",
        font=("Arial", 16, "bold"),
        bg="#4CAF50",
        fg="white"
    ).pack()
    
    # Content
    content_frame = tk.Frame(dialog, padx=20, pady=20)
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # Version info
    version_frame = tk.Frame(content_frame)
    version_frame.pack(fill=tk.X, pady=(0, 10))
    
    tk.Label(
        version_frame,
        text=f"Huidige versie: {update_info.get('current_version', 'Onbekend')}",
        font=("Arial", 11)
    ).pack(anchor="w")
    
    tk.Label(
        version_frame,
        text=f"Nieuwe versie: {update_info.get('latest_version', 'Onbekend')}",
        font=("Arial", 11, "bold"),
        fg="#4CAF50"
    ).pack(anchor="w")
    
    # Release notes
    tk.Label(
        content_frame,
        text="Release Notes:",
        font=("Arial", 11, "bold")
    ).pack(anchor="w", pady=(10, 5))
    
    notes_text = tk.Text(
        content_frame,
        wrap=tk.WORD,
        height=10,
        width=60,
        font=("Arial", 9)
    )
    notes_text.pack(fill=tk.BOTH, expand=True)
    notes_text.insert("1.0", update_info.get("release_notes", "Geen release notes beschikbaar."))
    notes_text.config(state=tk.DISABLED)
    
    # Buttons
    button_frame = tk.Frame(dialog, pady=10)
    button_frame.pack(fill=tk.X)
    
    def download_update():
        """Open download URL in browser."""
        download_url = update_info.get("download_url")
        release_url = update_info.get("release_url")
        
        if download_url:
            webbrowser.open(download_url)
        elif release_url:
            webbrowser.open(release_url)
        else:
            messagebox.showinfo(
                "Download",
                "Download URL niet beschikbaar. Bezoek de GitHub releases pagina.",
                parent=dialog
            )
        
        dialog.destroy()
    
    def later():
        """Close dialog."""
        dialog.destroy()
    
    tk.Button(
        button_frame,
        text="Download Nu",
        command=download_update,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 11, "bold"),
        padx=20,
        pady=5
    ).pack(side=tk.LEFT, padx=10)
    
    tk.Button(
        button_frame,
        text="Later",
        command=later,
        font=("Arial", 11),
        padx=20,
        pady=5
    ).pack(side=tk.LEFT, padx=10)


def check_updates_on_startup(parent: tk.Tk, current_version: str):
    """
    Check for updates on application startup (in background).
    
    Args:
        parent: Parent window
        current_version: Current application version
    """
    def on_update_available(update_info: dict):
        """Callback when update is available."""
        parent.after(0, lambda: show_update_dialog(parent, update_info))
    
    # Check for updates in background (non-blocking)
    check_for_updates_async(current_version, callback=on_update_available)


def manual_update_check(parent: tk.Tk, current_version: str):
    """
    Manually check for updates.
    
    Args:
        parent: Parent window
        current_version: Current application version
    """
    # Show checking dialog
    checking_dialog = tk.Toplevel(parent)
    checking_dialog.title("Controleren op Updates...")
    checking_dialog.transient(parent)
    checking_dialog.geometry("300x100")
    
    tk.Label(
        checking_dialog,
        text="Controleren op updates...",
        font=("Arial", 11)
    ).pack(expand=True)
    
    def check_complete():
        """Complete update check."""
        checking_dialog.destroy()
        
        checker = UpdateChecker(current_version)
        has_update = checker.check_for_updates()
        
        if has_update:
            update_info = checker.get_update_info()
            show_update_dialog(parent, update_info)
        else:
            messagebox.showinfo(
                "Updates",
                f"Je gebruikt de nieuwste versie ({current_version}).",
                parent=parent
            )
    
    # Check in background
    def worker():
        checker = UpdateChecker(current_version)
        has_update = checker.check_for_updates()
        
        parent.after(0, lambda: checking_dialog.destroy())
        
        if has_update:
            update_info = checker.get_update_info()
            parent.after(0, lambda: show_update_dialog(parent, update_info))
        else:
            parent.after(0, lambda: messagebox.showinfo(
                "Updates",
                f"Je gebruikt de nieuwste versie ({current_version}).",
                parent=parent
            ))
    
    import threading
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    
    # Auto-close after 10 seconds if still checking
    parent.after(10000, lambda: checking_dialog.destroy() if checking_dialog.winfo_exists() else None)

