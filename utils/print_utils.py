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
    """Save order and print from preview with detailed formatting."""
    import re
    if not WIN32PRINT_AVAILABLE:
        messagebox.showerror("Platform Error", "Windows printer support niet beschikbaar.")
        return

    success, bonnummer = bestelling_opslaan_func(show_confirmation=False)
    if not success:
        messagebox.showerror("Fout", "Bestelling kon niet worden opgeslagen.")
        return

    printer_name = app_settings.get("thermal_printer_name", "Default")
    
    # Check if printer name is valid
    if not printer_name or printer_name == "Default":
        messagebox.showwarning(
            "Printer niet geconfigureerd",
            "Er is geen printer geconfigureerd.\n\n"
            "Ga naar Instellingen > Printer Instellingen om een printer te selecteren."
        )
        return
    
    # Try to get available printers to suggest alternatives
    available_printers = get_available_printers()
    
    try:
        hprinter = win32print.OpenPrinter(printer_name)
        try:
            hjob = win32print.StartDocPrinter(hprinter, 1, ("Bon", None, "RAW"))
            win32print.StartPagePrinter(hprinter)
            
            ESC = b'\x1b'
            GS = b'\x1d'
            
            # Header
            win32print.WritePrinter(hprinter, ESC + b'a' + b'\x01')
            win32print.WritePrinter(hprinter, GS + b'!' + b'\x11')
            win32print.WritePrinter(hprinter, b'PITA PIZZA NAPOLI\n')
            win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')
            win32print.WritePrinter(hprinter, b'\n')
            
            header_info = """Brugstraat 12 - 9120 Vrasene
TEL: 03 / 775 72 28
FAX: 03 / 755 52 22
BTW: BE 0479.048.950
Bestel online
www.pitapizzanapoli.be
info@pitapizzanapoli.be

"""
            win32print.WritePrinter(hprinter, header_info.encode('cp437', errors='replace'))
            
            bon_lines = full_bon_text_for_print.split('\n')
            bonnummer_idx = bezorgtijd_idx = address_idx = dhr_mvr_idx = details_idx = 0
            is_afhaal = False
            
            for i, line in enumerate(bon_lines):
                if 'Bonnummer' in line: bonnummer_idx = i
                if 'Bezorgtijd' in line or 'Afhaaltijd' in line or 'Levertijd' in line: bezorgtijd_idx = i
                if 'Leveringsadres:' in line: address_idx = i
                if 'Afhaal:' in line: 
                    address_idx = i
                    is_afhaal = True
                if ('Dhr.' in line or 'Mvr.' in line): dhr_mvr_idx = i
                if 'Details bestelling' in line: details_idx = i; break
            
            # Bestelinfo printen, tot bezorgtijd/afhaaltijd
            win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')
            win32print.WritePrinter(hprinter, '\n'.join(bon_lines[bonnummer_idx:bezorgtijd_idx]).encode('cp437', errors='replace'))
            
            # Bezorgtijd/Afhaaltijd vet drukken
            win32print.WritePrinter(hprinter, ESC + b'E' + b'\x01')
            win32print.WritePrinter(hprinter, bon_lines[bezorgtijd_idx].encode('cp437', errors='replace'))
            win32print.WritePrinter(hprinter, b'\n')
            win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')
            win32print.WritePrinter(hprinter, b'\n')
            
            # Klantnaam ophalen uit klant_data of bontekst
            klantnaam = ""
            if klant_data:
                klantnaam = klant_data.get("naam", "").strip()
            
            if not klantnaam:
                # Val terug op bontekst: zoek regel na "Dhr. / Mvr."
                if dhr_mvr_idx and dhr_mvr_idx + 1 < len(bon_lines):
                    possible_name = bon_lines[dhr_mvr_idx + 1].strip()
                    if possible_name and ("Details bestelling" not in possible_name):
                        klantnaam = possible_name
            
            # Bepaal of het afhaal of levering is
            if is_afhaal:
                win32print.WritePrinter(hprinter, 'Afhaal:\n'.encode('cp858'))
            else:
                win32print.WritePrinter(hprinter, 'Leveringsadres:\n'.encode('cp858'))
            
            # Maak naam en adres vet en groter
            win32print.WritePrinter(hprinter, ESC + b'E' + b'\x01')  # Bold aan
            win32print.WritePrinter(hprinter, GS + b'!' + b'\x01')  # hoogte+breedte
            
            # Klantnaam expliciet printen indien beschikbaar
            if klantnaam:
                win32print.WritePrinter(hprinter, (klantnaam + '\n').encode('cp858', errors='replace'))
            
            ## Daarna het adres
            adres_end = dhr_mvr_idx if (dhr_mvr_idx > 0 and dhr_mvr_idx > address_idx) else details_idx
            address_content = bon_lines[address_idx + 1:adres_end] if address_idx > 0 and adres_end > 0 else []
            for addr_line in address_content:
                win32print.WritePrinter(hprinter, addr_line.encode('cp858', errors='replace'))
                win32print.WritePrinter(hprinter, b'\n')
            
            # Reset stijl
            win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')  # Normale grootte
            win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
            
            # Bestel-details
            win32print.WritePrinter(hprinter, b'\x1B\x74\x13')  # CP858 #euroteken
            
            if details_idx > 0:
                # bereken einde van details sectie
                details_end_idx = len(bon_lines)
                for i in range(details_idx, len(bon_lines)):
                    if 'Tarief' in bon_lines[i] or ('Totaal' in bon_lines[i] and i > details_idx + 2):
                        details_end_idx = i
                        break
                
                # "Details bestelling" vet maar NORMALE grootte
                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x01')  # Bold aan
                win32print.WritePrinter(hprinter, 'Details bestelling\n'.encode('cp858'))
                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                win32print.WritePrinter(hprinter, b'\n')
                
                # Items GROTER maken (zoals adres) - dubbele hoogte + breedte
                win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')  # Links uitlijnen
                win32print.WritePrinter(hprinter, GS + b'!' + b'\x01')  # Dubbele hoogte
                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                
                current_item_lines = []
                first_item = True
                
                for line in bon_lines[details_idx + 1:details_end_idx]:
                    stripped_line = line.strip()
                    if stripped_line and (stripped_line[0].isdigit() and 'x' in line[:5]):
                        if current_item_lines:
                            # Print vorige item
                            win32print.WritePrinter(hprinter, '\n'.join(current_item_lines).encode('cp858'))
                            win32print.WritePrinter(hprinter, b'\n')
                            # Reset tijdelijk voor scheidingslijn
                            win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')  # Normale grootte
                            win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                            win32print.WritePrinter(hprinter, ('-' * 42 + '\n').encode('cp858'))
                            # Weer groot maken voor volgende item
                            win32print.WritePrinter(hprinter, GS + b'!' + b'\x01')  # Groot
                            win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                            current_item_lines = []
                        elif first_item:
                            first_item = False
                        current_item_lines.append(line.replace('?', '€'))
                    else:
                        if "TE BETALEN" in line:
                            continue
                        if stripped_line:
                            current_item_lines.append(f"> {stripped_line}")
                
                if current_item_lines:
                    win32print.WritePrinter(hprinter, '\n'.join(current_item_lines).encode('cp858'))
                    win32print.WritePrinter(hprinter, b'\n')
                
                # Reset stijl na details (terug naar normaal)
                win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')  # Normale grootte
                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Bold uit
                win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')  # Links
                
                # ==== Tarief-sectie printen ====
                tarief_start = -1
                for i in range(details_end_idx, len(bon_lines)):
                    line = bon_lines[i]
                    if ("Tarief" in line and "Basis" in line and "BTW" in line and "Totaal" in line):
                        tarief_start = i
                        break
                
                if tarief_start >= 0:
                    tarief_end = len(bon_lines)
                    for j in range(tarief_start + 1, len(bon_lines)):
                        if bon_lines[j].strip() == "" or bon_lines[j].startswith("Totaal"):
                            tarief_end = j
                            break
                    tarief_block = "\n".join(bon_lines[tarief_start:tarief_end]).encode('cp858', errors='replace')
                    win32print.WritePrinter(hprinter, tarief_block)
                    win32print.WritePrinter(hprinter, b'\n')
            
            # Totaal
            totaal_line = ""
            for i in range(len(bon_lines) - 1, -1, -1):
                if 'Totaal' in bon_lines[i] and ('€' in bon_lines[i] or '?' in bon_lines[i]):
                    totaal_line = bon_lines[i]
                    break
            
            if totaal_line:
                totaal_line = totaal_line.replace('\u20ac', '€').replace('\xe2\x82\xac', '€').replace('?', '€')
                win32print.WritePrinter(hprinter, b'\n')
                win32print.WritePrinter(hprinter, ESC + b'a' + b'\x01')
                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x01')
                win32print.WritePrinter(hprinter, GS + b'!' + b'\x11')
                win32print.WritePrinter(hprinter, totaal_line.encode('cp858', errors='replace'))
                win32print.WritePrinter(hprinter, b'\n')
                win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')
                win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')
                win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')
            
            # Algemene opmerking printen (indien aanwezig)
            if klant_data:
                klant_opm = (klant_data.get("opmerking") or "").strip()
                if klant_opm:
                    win32print.WritePrinter(hprinter, b'\n')
                    win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')  # Links
                    win32print.WritePrinter(hprinter, ESC + b'E' + b'\x01')  # Vet aan
                    win32print.WritePrinter(hprinter, GS + b'!' + b'\x01')  # Dubbele hoogte aan
                    opmerking_text = f"Opmerking:\n{klant_opm}"
                    win32print.WritePrinter(hprinter, opmerking_text.encode('cp858', errors='replace'))
                    win32print.WritePrinter(hprinter, b'\n')
                    win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')  # Reset grootte
                    win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')  # Vet uit
                    win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')  # Links uitlijnen
            
            # Footer
            footer = """

"""
            win32print.WritePrinter(hprinter, ESC + b'a' + b'\x01')
            win32print.WritePrinter(hprinter, footer.encode('cp437', errors='replace'))
            
            # TE BETALEN! (groot/vet) + exact 1 lege lijn erna
            win32print.WritePrinter(hprinter, ESC + b'a' + b'\x01')
            win32print.WritePrinter(hprinter, ESC + b'E' + b'\x01')
            win32print.WritePrinter(hprinter, GS + b'!' + b'\x01')
            win32print.WritePrinter(hprinter, b'TE BETALEN!\n')
            # Reset grootte/vet, blijven gecentreerd
            win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')
            win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')
            # Precies één lege lijn na "TE BETALEN!"
            win32print.WritePrinter(hprinter, b'\n')
            # Centraal "Eet smakelijk"
            win32print.WritePrinter(hprinter, ESC + b'E' + b'\x01')
            win32print.WritePrinter(hprinter, b'Eet smakelijk\n')
            win32print.WritePrinter(hprinter, ESC + b'E' + b'\x00')
            # Openingsuren
            win32print.WritePrinter(hprinter, b'Van Dins- tot Zon\n vanaf 17 u Tot 20u30\n')
            # Reset uitlijning
            win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')
            
            # QR code
            if address_for_qr:
                win32print.WritePrinter(hprinter, b'\n')
                win32print.WritePrinter(hprinter, ESC + b'a' + b'\x01')
                win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x04\x00' + b'1A2\x00')
                win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x03\x00' + b'1C\x06')
                win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x03\x00' + b'1E0')
                qr_data = address_for_qr.encode('utf-8')
                qr_len = len(qr_data) + 3
                win32print.WritePrinter(hprinter, GS + b'(' + b'k' + qr_len.to_bytes(2, 'little') + b'1P0' + qr_data)
                win32print.WritePrinter(hprinter, GS + b'(' + b'k' + b'\x03\x00' + b'1Q0')
                win32print.WritePrinter(hprinter, b'\n')
                win32print.WritePrinter(hprinter, ESC + b'a' + b'\x00')
            
            win32print.WritePrinter(hprinter, b'\n\n\n')
            win32print.WritePrinter(hprinter, GS + b'V' + b'\x00')
            
            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)
            
            messagebox.showinfo("Voltooid", f"Bon {bonnummer} opgeslagen en naar printer gestuurd!")
        finally:
            win32print.ClosePrinter(hprinter)
    except Exception as e:
        error_msg = str(e)
        if "Ongeldige printernaam" in error_msg or "Invalid printer name" in error_msg or "1801" in error_msg:
            # Build error message with available printers
            error_text = (
                f"De printer '{printer_name}' kon niet worden gevonden.\n\n"
                f"Controleer:\n"
                f"1. Of de printer is aangesloten en ingeschakeld\n"
                f"2. Of de printer naam exact overeenkomt met Windows\n"
                f"3. Open Instellingen > Printer Instellingen om de juiste naam te selecteren\n\n"
            )
            
            if available_printers:
                error_text += f"Beschikbare printers ({len(available_printers)}):\n"
                for i, printer in enumerate(available_printers[:5], 1):  # Show first 5
                    error_text += f"  {i}. {printer}\n"
                if len(available_printers) > 5:
                    error_text += f"  ... en {len(available_printers) - 5} meer\n"
                error_text += "\n"
            
            error_text += f"Foutdetails: {error_msg}"
            
            messagebox.showerror("Fout bij afdrukken", error_text)
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


def get_available_printers() -> list:
    """Get list of available Windows printers.
    
    Returns:
        List of printer names
    """
    if not WIN32PRINT_AVAILABLE:
        return []
    
    try:
        printers = []
        printer_info = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        for printer in printer_info:
            printers.append(printer[2])  # printer[2] contains the printer name
        return sorted(printers)
    except Exception as e:
        logger.exception(f"Error getting printer list: {e}")
        return []


def open_printer_settings(root: tk.Tk, app_settings: Dict[str, Any], settings_file: str = "settings.json") -> None:
    """Open printer settings dialog.
    
    Args:
        root: Root Tkinter window
        app_settings: Application settings dictionary
        settings_file: Path to settings JSON file
    """
    from config import save_json_file
    from tkinter import ttk
    
    settings_win = tk.Toplevel(root)
    settings_win.title("Printer Instellingen")
    settings_win.geometry("500x250")
    settings_win.transient(root)
    settings_win.grab_set()

    tk.Label(settings_win, text="Selecteer thermische printer:", font=("Arial", 11, "bold")).pack(pady=10)

    # Get available printers
    available_printers = get_available_printers()
    current_printer = app_settings.get("thermal_printer_name", "Default")
    
    # Frame for printer selection
    printer_frame = tk.Frame(settings_win)
    printer_frame.pack(pady=5, padx=20, fill=tk.X)
    
    printer_name_var = tk.StringVar(value=current_printer, master=settings_win)
    
    if available_printers:
        # Use Combobox if printers are available
        printer_combo = ttk.Combobox(
            printer_frame,
            textvariable=printer_name_var,
            values=available_printers,
            width=45,
            font=("Arial", 10),
            state="readonly"
        )
        printer_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Set current selection if it exists in the list
        if current_printer in available_printers:
            printer_combo.current(available_printers.index(current_printer))
        elif available_printers:
            printer_combo.current(0)  # Select first printer if current not found
        
        # Manual entry option
        tk.Label(settings_win, text="Of voer handmatig in:", font=("Arial", 9)).pack(pady=(5, 0))
        manual_entry = tk.Entry(settings_win, width=45, font=("Arial", 10))
        manual_entry.pack(pady=5)
        manual_entry.insert(0, current_printer if current_printer not in available_printers else "")
        
        def on_combo_change(event=None):
            manual_entry.delete(0, tk.END)
            manual_entry.insert(0, printer_name_var.get())
        
        def on_manual_change(event=None):
            printer_name_var.set(manual_entry.get())
        
        printer_combo.bind("<<ComboboxSelected>>", on_combo_change)
        manual_entry.bind("<KeyRelease>", on_manual_change)
        
        tk.Label(
            settings_win,
            text=f"Gevonden printers: {len(available_printers)}",
            font=("Arial", 8),
            fg="gray"
        ).pack(pady=(0, 5))
    else:
        # Fallback to entry if no printers found
        printer_entry = tk.Entry(printer_frame, textvariable=printer_name_var, width=45, font=("Arial", 10))
        printer_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            settings_win,
            text="Geen printers gevonden. Voer de exacte printer naam in zoals deze in Windows staat.",
            font=("Arial", 8),
            fg="orange",
            wraplength=450
        ).pack(pady=(5, 10))

    def save_settings():
        printer_name = printer_name_var.get().strip()
        if not printer_name:
            messagebox.showwarning("Waarschuwing", "Voer een printer naam in.")
            return
        
        app_settings["thermal_printer_name"] = printer_name
        if save_json_file(settings_file, app_settings):
            messagebox.showinfo("Opgeslagen", f"Printerinstellingen opgeslagen!\n\nPrinter: {printer_name}")
            settings_win.destroy()

    button_frame = tk.Frame(settings_win)
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="Opslaan", command=save_settings, bg="#D1FFD1", font=("Arial", 10), padx=20).pack(side=tk.LEFT, padx=5)
    
    def test_printer():
        """Test if selected printer is available."""
        printer_name = printer_name_var.get().strip()
        if not printer_name:
            messagebox.showwarning("Waarschuwing", "Selecteer eerst een printer.")
            return
        
        try:
            hprinter = win32print.OpenPrinter(printer_name)
            win32print.ClosePrinter(hprinter)
            messagebox.showinfo("Succes", f"Printer '{printer_name}' is beschikbaar en werkt!")
        except Exception as e:
            error_msg = str(e)
            if "1801" in error_msg or "Ongeldige printernaam" in error_msg:
                messagebox.showerror(
                    "Fout",
                    f"Printer '{printer_name}' niet gevonden.\n\n"
                    f"Controleer:\n"
                    f"1. Of de printer is aangesloten en ingeschakeld\n"
                    f"2. Of de naam exact overeenkomt met Windows\n"
                    f"3. Open Windows Instellingen > Printers om de exacte naam te zien\n\n"
                    f"Fout: {error_msg}"
                )
            else:
                messagebox.showerror("Fout", f"Kan printer niet testen: {error_msg}")
    
    tk.Button(button_frame, text="Test Printer", command=test_printer, bg="#D1E7FF", font=("Arial", 10), padx=20).pack(side=tk.LEFT, padx=5)


def open_footer_settings(root: tk.Tk, app_settings: Dict[str, Any], settings_file: str = "settings.json") -> None:
    """Open footer settings dialog.
    
    Args:
        root: Root Tkinter window
        app_settings: Application settings dictionary
        settings_file: Path to settings JSON file
    """
    from config import save_json_file
    
    settings_win = tk.Toplevel(root)
    settings_win.title("Bon Footer Instellingen")
    settings_win.geometry("600x400")
    settings_win.transient(root)
    settings_win.grab_set()

    tk.Label(
        settings_win,
        text="Aangepaste tekst onder openingsuren:",
        font=("Arial", 11, "bold")
    ).pack(pady=10)

    tk.Label(
        settings_win,
        text="Deze tekst wordt onder de openingsuren op de bon geprint.\nLaat leeg om geen extra tekst te tonen.",
        font=("Arial", 9),
        fg="gray"
    ).pack(pady=(0, 10))

    # Text widget for multi-line input
    text_frame = tk.Frame(settings_win)
    text_frame.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)
    
    from tkinter import scrolledtext
    footer_text_widget = scrolledtext.ScrolledText(
        text_frame,
        wrap=tk.WORD,
        width=60,
        height=12,
        font=("Arial", 10)
    )
    footer_text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Load current value
    current_text = app_settings.get("bon_footer_custom_text", "")
    footer_text_widget.insert("1.0", current_text)

    def save_settings():
        custom_text = footer_text_widget.get("1.0", tk.END).strip()
        app_settings["bon_footer_custom_text"] = custom_text
        if save_json_file(settings_file, app_settings):
            messagebox.showinfo("Opgeslagen", "Footer instellingen opgeslagen!")
            settings_win.destroy()

    button_frame = tk.Frame(settings_win)
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="Opslaan", command=save_settings, bg="#D1FFD1", font=("Arial", 10), padx=20).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Annuleren", command=settings_win.destroy, bg="#FFADAD", font=("Arial", 10), padx=20).pack(side=tk.LEFT, padx=5)

