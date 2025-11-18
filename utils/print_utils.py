"""Print and receipt utility functions."""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Dict, Any
import platform
import sys

# Optional QR code support
try:
    import qrcode
    from PIL import Image
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    qrcode = None
    Image = None

# Windows print support
WIN32PRINT_AVAILABLE = False
if platform.system() == "Windows":
    try:
        import win32print
        WIN32PRINT_AVAILABLE = True
    except ImportError:
        pass

from modules.bon_viewer import open_bon_viewer
from logging_config import get_logger

logger = get_logger("pizzeria.utils.print")


def print_bon_with_qr(full_bon_text_for_print: str, qr_data_string: str) -> None:
    """
    Print receipt with QR code (ESC/POS printer).
    Note: This function uses python-escpos which is not currently in use.
    """
    if not QRCODE_AVAILABLE:
        messagebox.showerror("Print Error", "QR code support niet beschikbaar. Installeer qrcode met: pip install qrcode[pil]")
        return
    
    VENDOR_ID = 0x04b8  # Epson (controleer eventueel)
    PRODUCT_ID = 0x0e15  # TM-T20II (controleer met pyusb of boekje)
    try:
        qr_img = qrcode.make(qr_data_string)
        qr_img = qr_img.resize((180, 180), Image.LANCZOS)
        # Note: Usb from escpos is not imported - this function may not be in use
        # p = Usb(VENDOR_ID, PRODUCT_ID, timeout=0)
        # p.set(align='left')
        # p.text(full_bon_text_for_print + "\n")
        # p.image(qr_img)
        # p.cut()
        logger.warning("print_bon_with_qr called but ESC/POS support not configured")
    except Exception as e:
        logger.exception("Error in print_bon_with_qr")
        messagebox.showerror("Print Error", f"QR/ESC/POS print niet gelukt: {e}")


def show_print_preview(
    event: Optional[tk.Event],
    root: tk.Tk,
    get_current_order_data_func,
    menu_data: Dict[str, Any],
    EXTRAS: Dict[str, Any],
    app_settings: Dict[str, Any],
    save_and_print_callback
) -> None:
    """Show print preview dialog."""
    klant_data, order_items, temp_bonnummer = get_current_order_data_func()
    if klant_data is None:  # Geen geldige data om te previewen
        return

    # Toon het afdrukvoorbeeld
    open_bon_viewer(
        root,
        klant_data,
        order_items,
        temp_bonnummer,
        menu_data,
        EXTRAS,
        app_settings,
        save_and_print_callback  # Geef de callback mee
    )


def _save_and_print_from_preview(
    full_bon_text_for_print: str,
    address_for_qr: Optional[str],
    klant_data: Optional[Dict[str, Any]],
    bestelling_opslaan_func,
    app_settings: Dict[str, Any]
) -> None:
    """Save order and print from preview."""
    import re
    if not WIN32PRINT_AVAILABLE:
        messagebox.showerror("Platform Error", "Windows printer support niet beschikbaar.")
        return

    success, bonnummer = bestelling_opslaan_func(show_confirmation=False)
    if not success:
        return

    printer_name = app_settings.get("thermal_printer_name", "Default")
    try:
        hprinter = win32print.OpenPrinter(printer_name)
        try:
            win32print.StartDocPrinter(hprinter, 1, ("Bon", None, "RAW"))
            win32print.StartPagePrinter(hprinter)
            
            # Split text into lines and print
            lines = full_bon_text_for_print.split('\n')
            for line in lines:
                win32print.WritePrinter(hprinter, (line + '\n').encode('utf-8'))
            
            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)
            
            messagebox.showinfo("Voltooid", f"Bon {bonnummer} opgeslagen en naar printer gestuurd!")
        finally:
            win32print.ClosePrinter(hprinter)
    except Exception as e:
        error_msg = str(e)
        if "Ongeldige printernaam" in error_msg or "Invalid printer name" in error_msg or "1801" in error_msg:
            messagebox.showerror(
                "Fout bij afdrukken",
                f"De printer '{printer_name}' kon niet worden gevonden.\n\n"
                f"Controleer:\n"
                f"1. Of de printer is aangesloten en ingeschakeld\n"
                f"2. Of de printer naam correct is in Instellingen > Printer Instellingen\n"
                f"3. Of de printer beschikbaar is in Windows Printer Instellingen\n\n"
                f"Foutdetails: {error_msg}"
            )
        else:
            messagebox.showerror("Fout bij afdrukken", f"Kon de bon niet afdrukken.\n\nFoutdetails: {error_msg}")


def find_printer_usb_ids() -> None:
    """
    Helperfunctie om USB ID's van aangesloten printers te vinden.
    Roep aan via een debug-knop of via de Python console.
    """
    try:
        import usb.core
        devices = usb.core.find(find_all=True)

        printer_info = []
        for device in devices:
            try:
                vendor = f"0x{device.idVendor:04x}"
                product = f"0x{device.idProduct:04x}"
                try:
                    manufacturer = usb.util.get_string(device, device.iManufacturer)
                    prod_name = usb.util.get_string(device, device.iProduct)
                    info = f"Vendor: {vendor}, Product: {product}\n  {manufacturer} - {prod_name}"
                except Exception:
                    info = f"Vendor: {vendor}, Product: {product}"
                printer_info.append(info)
            except Exception:
                pass

        if printer_info:
            messagebox.showinfo("USB Apparaten", "\n\n".join(printer_info))
        else:
            messagebox.showinfo("USB Apparaten", "Geen USB-apparaten gevonden.")

    except ImportError:
        messagebox.showerror("Fout", "PyUSB niet geïnstalleerd. Installeer met: pip install pyusb")


def open_printer_settings(root: tk.Tk, app_settings: Dict[str, Any], settings_file: str = "settings.json") -> None:
    """Open printer settings dialog.
    
    Args:
        root: Root Tkinter window
        app_settings: Application settings dictionary
        settings_file: Path to settings JSON file
    """
    from config import save_json_file
    
    settings_win = tk.Toplevel(root)
    settings_win.title("Printer Instellingen")
    settings_win.geometry("400x150")
    settings_win.transient(root)
    settings_win.grab_set()

    tk.Label(settings_win, text="Naam thermische printer (of 'Default'):", font=("Arial", 11, "bold")).pack(pady=10)

    printer_name_var = tk.StringVar(value=app_settings.get("thermal_printer_name", "Default"), master=settings_win)
    printer_entry = tk.Entry(settings_win, textvariable=printer_name_var, width=40, font=("Arial", 11))
    printer_entry.pack(pady=5)

    def save_settings():
        app_settings["thermal_printer_name"] = printer_name_var.get().strip()
        if save_json_file(settings_file, app_settings):
            messagebox.showinfo("Opgeslagen", "Printerinstellingen succesvol opgeslagen!")
            settings_win.destroy()

    tk.Button(settings_win, text="Opslaan", command=save_settings, bg="#D1FFD1", font=("Arial", 10)).pack(pady=10)

