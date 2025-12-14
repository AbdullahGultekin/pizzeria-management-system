"""
Update checker UI module voor de Pizzeria Management System.
"""
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional
import webbrowser
import threading
import sys
import urllib.request
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
        """Download update file automatically."""
        import urllib.request
        import os
        from pathlib import Path
        
        download_url = update_info.get("download_url")
        release_url = update_info.get("release_url")
        latest_version = update_info.get("latest_version", "unknown")
        
        # If no download URL from API, try to construct it directly
        if not download_url and release_url:
            # Try common asset names
            tag_name = update_info.get("latest_version", "").lstrip("v")
            if not tag_name.startswith("v"):
                tag_name = f"v{tag_name}"
            
            # Try to construct download URL for common asset names
            repo_name = release_url.split("/releases/tag/")[0].split("/")[-1]
            owner_name = release_url.split("/releases/tag/")[0].split("/")[-2]
            
            # Try .exe first, then .zip
            possible_names = [
                "PizzeriaBestelformulier.exe",
                "PizzeriaBestelformulier.zip",
                f"pizzeria-management-system-{tag_name}.exe",
                f"pizzeria-management-system-{tag_name}.zip"
            ]
            
            # Test if any of these URLs exist
            for asset_name in possible_names:
                test_url = f"https://github.com/{owner_name}/{repo_name}/releases/download/{tag_name}/{asset_name}"
                try:
                    # Quick HEAD request to check if file exists
                    test_req = urllib.request.Request(test_url, method='HEAD')
                    with urllib.request.urlopen(test_req, timeout=2) as response:
                        if response.status == 200:
                            download_url = test_url
                            logger.info(f"Found asset via direct URL: {download_url}")
                            break
                except:
                    continue
        
        if download_url:
            # Automatisch downloaden
            try:
                # Bepaal download locatie (naast EXE of in Downloads)
                if hasattr(sys, 'frozen') and sys.frozen:
                    # Running from EXE
                    download_dir = Path(sys.executable).parent
                else:
                    # Running from script
                    download_dir = Path.home() / "Downloads"
                    download_dir.mkdir(exist_ok=True)
                
                # Bepaal bestandsnaam
                filename = download_url.split('/')[-1]
                if '?' in filename:
                    filename = filename.split('?')[0]
                download_path = download_dir / filename
                
                # Toon progress dialog
                progress_dialog = tk.Toplevel(dialog)
                progress_dialog.title("Downloaden...")
                progress_dialog.transient(dialog)
                progress_dialog.geometry("400x150")
                progress_dialog.grab_set()
                
                progress_label = tk.Label(
                    progress_dialog,
                    text=f"Downloaden van versie {latest_version}...",
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
                
                def download_worker():
                    """Download in background thread."""
                    try:
                        # Download file
                        urllib.request.urlretrieve(download_url, str(download_path))
                        
                        # Update UI from main thread
                        def on_complete():
                            progress_bar.stop()
                            progress_dialog.destroy()
                            dialog.destroy()
                            
                            messagebox.showinfo(
                                "Download Voltooid",
                                f"Update succesvol gedownload!\n\n"
                                f"Locatie: {download_path}\n\n"
                                f"Pak het bestand uit en vervang de oude EXE.",
                                parent=parent
                            )
                        
                        parent.after(0, on_complete)
                        
                    except Exception as e:
                        logger.exception(f"Error downloading update: {e}")
                        
                        def on_error():
                            progress_bar.stop()
                            progress_dialog.destroy()
                            messagebox.showerror(
                                "Download Gefaald",
                                f"Kon update niet downloaden:\n{str(e)}\n\n"
                                f"Probeer handmatig te downloaden van:\n{release_url}",
                                parent=dialog
                            )
                        
                        parent.after(0, on_error)
                
                # Start download in background
                import threading
                thread = threading.Thread(target=download_worker, daemon=True)
                thread.start()
                
            except Exception as e:
                logger.exception(f"Error setting up download: {e}")
                # Fallback: open in browser
                webbrowser.open(download_url)
                dialog.destroy()
        elif release_url:
            # Geen directe download URL - probeer direct download URL te construeren
            # GitHub releases download URL format: 
            # https://github.com/owner/repo/releases/download/tag/filename
            tag_name = latest_version
            if not tag_name.startswith("v"):
                tag_name = f"v{tag_name}"
            
            # Extract repo info from release_url
            try:
                # release_url format: https://github.com/owner/repo/releases/tag/v1.1.1
                parts = release_url.replace("https://github.com/", "").split("/releases/tag/")
                if len(parts) == 2:
                    repo_path = parts[0]  # owner/repo
                    
                    # Try common asset names
                    possible_assets = [
                        f"https://github.com/{repo_path}/releases/download/{tag_name}/PizzeriaBestelformulier.exe",
                        f"https://github.com/{repo_path}/releases/download/{tag_name}/PizzeriaBestelformulier.zip",
                    ]
                    
                    # Test which URL works
                    working_url = None
                    for test_url in possible_assets:
                        try:
                            test_req = urllib.request.Request(test_url, method='HEAD')
                            with urllib.request.urlopen(test_req, timeout=3) as response:
                                if response.status == 200:
                                    working_url = test_url
                                    logger.info(f"Found working download URL: {working_url}")
                                    break
                        except:
                            continue
                    
                    if working_url:
                        # Use the working URL for download
                        download_url = working_url
                        # Retry download with found URL
                        download_update()
                        return
            except Exception as e:
                logger.debug(f"Could not construct download URL: {e}")
            
            # Fallback: open releases pagina met duidelijke instructies
            webbrowser.open(release_url)
            messagebox.showinfo(
                "Download Update",
                f"Update versie {latest_version} beschikbaar!\n\n"
                "De GitHub releases pagina is geopend.\n\n"
                "Download instructies:\n"
                "1. Scroll naar 'Assets' sectie\n"
                "2. Klik op 'PizzeriaBestelformulier.zip' of '.exe'\n"
                "3. Het bestand wordt automatisch gedownload\n\n"
                "Tip: Wacht 2-5 minuten en probeer opnieuw voor automatische download.",
                parent=dialog
            )
            dialog.destroy()
        else:
            messagebox.showinfo(
                "Download",
                "Download URL niet beschikbaar.\n\n"
                "Bezoek de GitHub releases pagina om de update te downloaden.",
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
                # Update status label (thread-safe via after)
                parent.after(0, lambda: status_label.config(text="Backup maken van lokale gegevens..."))
                
                # Perform git update
                success, message = perform_git_update(backup_data=True)
                
                # Update UI from main thread (thread-safe)
                def on_complete():
                    progress_bar.stop()
                    progress_dialog.destroy()
                    dialog.destroy()
                    
                    if success:
                        # Show success message
                        result = messagebox.askyesno(
                            "Update Succesvol",
                            f"{message}\n\n"
                            "De applicatie moet opnieuw worden gestart om de updates te activeren.\n\n"
                            "Wil je de applicatie nu opnieuw starten?",
                            parent=parent
                        )
                        
                        if result:
                            # Restart application
                            import sys
                            import os
                            try:
                                # Close all windows first
                                parent.quit()
                                parent.destroy()
                                # Restart
                                os.execv(sys.executable, [sys.executable] + sys.argv)
                            except Exception as e:
                                logger.exception(f"Error restarting application: {e}")
                                messagebox.showinfo(
                                    "Herstart Vereist",
                                    "Update succesvol!\n\n"
                                    "Start de applicatie handmatig opnieuw om de updates te activeren.",
                                    parent=parent
                                )
                    else:
                        messagebox.showerror(
                            "Update Gefaald",
                            f"{message}\n\n"
                            "Je kunt handmatig updaten via:\n"
                            "scripts\\update\\update_safe.bat\n\n"
                            "Of gebruik: git pull origin main",
                            parent=parent
                        )
                
                parent.after(0, on_complete)
                
            except Exception as e:
                logger.exception(f"Error during auto update: {e}")
                
                def on_error():
                    progress_bar.stop()
                    progress_dialog.destroy()
                    messagebox.showerror(
                        "Fout",
                        f"Fout tijdens automatische update:\n{str(e)}\n\n"
                        "Probeer handmatig te updaten via:\n"
                        "git pull origin main",
                        parent=parent
                    )
                
                parent.after(0, on_error)
        
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

