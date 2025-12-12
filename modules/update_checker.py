"""
Update checker UI module voor de Pizzeria Management System.
"""
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional
import webbrowser
import threading
from utils.updater import UpdateChecker, check_for_updates_async, is_git_repository, perform_git_update
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
    
    # Check if git update is available
    can_git_update = is_git_repository()
    
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
    
    def auto_update():
        """Perform automatic git update."""
        # Confirm dialog
        confirm = messagebox.askyesno(
            "Automatische Update",
            "Wil je nu automatisch updaten via git pull?\n\n"
            "Dit zal:\n"
            "• Je lokale gegevens backuppen\n"
            "• De laatste wijzigingen van GitHub ophalen\n"
            "• De applicatie opnieuw starten\n\n"
            "Je database en instellingen blijven behouden.",
            parent=dialog
        )
        
        if not confirm:
            return
        
        # Show progress dialog
        progress_dialog = tk.Toplevel(dialog)
        progress_dialog.title("Updaten...")
        progress_dialog.transient(dialog)
        progress_dialog.geometry("400x150")
        progress_dialog.grab_set()
        
        progress_label = tk.Label(
            progress_dialog,
            text="Updaten van GitHub...",
            font=("Arial", 11)
        )
        progress_label.pack(pady=20)
        
        progress_bar = ttk.Progressbar(
            progress_dialog,
            mode='indeterminate',
            length=300
        )
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        status_label = tk.Label(
            progress_dialog,
            text="",
            font=("Arial", 9),
            fg="gray"
        )
        status_label.pack(pady=5)
        
        def update_worker():
            """Perform update in background thread."""
            try:
                status_label.config(text="Backup maken van lokale gegevens...")
                success, message = perform_git_update(backup_data=True)
                
                progress_bar.stop()
                progress_dialog.destroy()
                dialog.destroy()
                
                if success:
                    messagebox.showinfo(
                        "Update Succesvol",
                        f"{message}\n\n"
                        "De applicatie zal nu opnieuw starten.\n"
                        "Sluit dit venster om de update te voltooien.",
                        parent=parent
                    )
                    # Restart application
                    import sys
                    import os
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                else:
                    messagebox.showerror(
                        "Update Gefaald",
                        f"{message}\n\n"
                        "Je kunt handmatig updaten via:\n"
                        "scripts\\update\\update_safe.bat",
                        parent=parent
                    )
            except Exception as e:
                progress_bar.stop()
                progress_dialog.destroy()
                logger.exception(f"Error during auto update: {e}")
                messagebox.showerror(
                    "Fout",
                    f"Fout tijdens automatische update:\n{str(e)}",
                    parent=parent
                )
        
        # Start update in background
        thread = threading.Thread(target=update_worker, daemon=True)
        thread.start()
    
    def later():
        """Close dialog."""
        dialog.destroy()
    
    # Primary button: Auto-update if available, otherwise download
    if can_git_update:
        tk.Button(
            button_frame,
            text="🔄 Automatisch Updaten",
            command=auto_update,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="📥 Download Exe",
            command=download_update,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=10)
    else:
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
    
    # Show info about git update if available
    if can_git_update:
        info_label = tk.Label(
            content_frame,
            text="💡 Tip: Automatische update werkt direct zonder exe te downloaden!",
            font=("Arial", 9),
            fg="#4CAF50",
            bg="#E8F5E9"
        )
        info_label.pack(pady=(10, 0))


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

