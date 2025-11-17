import tkinter as tk
from tkinter import Toplevel, scrolledtext, messagebox, Frame, Button, Label
import os
import tempfile
import subprocess
import sys
import json
from PIL import Image, ImageTk
import urllib.parse  # <-- Correcte import!

# Optional QR code support
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    qrcode = None

# Importeer generate_bon_text van de bon_generator module
from bon_generator import generate_bon_text


def open_bon_viewer(root_window, klant_data, bestelregels, bonnummer, menu_data_global, extras_data_global,
                    app_settings_global, save_and_print_callback):
    """
    Opent een Toplevel venster om een bon weer te geven en aan te bieden voor afdrukken.
    Dit venster fungeert nu als een direct afdrukvoorbeeld.

    Args:
        root_window: Het hoofd Tkinter venster (root).
        klant_data (dict): De gegevens van de klant voor de bon.
        bestelregels (list): De bestelregels voor de bon.
        bonnummer (int): Het bonnummer.
        menu_data_global (dict): De globale menu_data.
        extras_data_global (dict): De globale EXTRAS data.
        app_settings_global (dict): De globale app_settings.
        save_and_print_callback: Een callback functie uit main.py om de bestelling op te slaan en af te drukken.
    """

    # De tekst voor de bon wordt één keer gegenereerd.
    parts = generate_bon_text(
        klant_data, bestelregels, bonnummer, menu_data_for_drinks=menu_data_global, extras_data=extras_data_global
    )
    header_str, info_str, address_str, details_str, tarief_str, totaal_label, totaal_waarde, te_betalen_str, footer_str, address_for_qr, bon_width_from_generator = parts

    # Construct the full text for printing
    full_bon_text_for_print = (
            header_str + "\n" +
            info_str.strip() + "\n" +
            address_str + "\n" +
            details_str.strip() + "\n" +
            tarief_str.strip() + "\n" +
            f"{totaal_label}: {totaal_waarde}\n" +
            f"{te_betalen_str}\n" +
            footer_str
    )

    bon_win = Toplevel(root_window)
    bon_win.title(f"Afdrukvoorbeeld Bon {bonnummer}")
    bon_win.geometry("350x700")
    bon_win.resizable(False, True)

    main_bon_frame = Frame(bon_win)
    main_bon_frame.pack(padx=5, pady=5, fill="both", expand=True)

    # Frame voor adres en QR-code naast elkaar
    qr_addr_frame = Frame(main_bon_frame)
    qr_addr_frame.pack(fill="x", pady=(2, 10))

    # Links: Adres tekst
    address_text_frame = Frame(qr_addr_frame)
    address_text_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
    
    address_label = Label(
        address_text_frame, 
        text=address_str, 
        font=("Courier", 8), 
        justify="left",
        anchor="w"
    )
    address_label.pack(anchor="w")

    # Rechts: QR-code
    qr_code_frame = Frame(qr_addr_frame)
    qr_code_frame.pack(side="right", padx=(5, 0))

    try:
        if not QRCODE_AVAILABLE:
            raise ImportError("qrcode module not installed")
        
        # Bouw smart navigation URL die automatisch de juiste app opent
        encoded_addr = urllib.parse.quote_plus(address_for_qr)
        
        # Smart navigation: gebruik een inline JavaScript redirect via data URL
        # Dit werkt zonder externe server en detecteert automatisch het platform
        # iOS → Apple Maps, Android → Waze (of Google Maps), Desktop → Google Maps
        
        # Build navigation URLs for different platforms
        google_url = f"https://www.google.com/maps/search/?api=1&query={encoded_addr}"
        waze_url = f"https://waze.com/ul?q={encoded_addr}"
        apple_url = f"http://maps.apple.com/?q={encoded_addr}"
        
        # Create smart redirect HTML with JavaScript
        # This will try to open the best app for the platform
        redirect_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Navigatie</title>
<script>
(function() {{
    var addr = decodeURIComponent('{encoded_addr}');
    var ua = navigator.userAgent;
    var isIOS = /iPad|iPhone|iPod/.test(ua) && !window.MSStream;
    var isAndroid = /android/i.test(ua);
    
    if (isIOS) {{
        // iOS: Try Apple Maps first
        window.location = 'maps://?q=' + encodeURIComponent(addr);
        setTimeout(function() {{
            window.location = 'http://maps.apple.com/?q=' + encodeURIComponent(addr);
        }}, 500);
    }} else if (isAndroid) {{
        // Android: Try Waze first, then Google Maps
        window.location = 'waze://?q=' + encodeURIComponent(addr);
        setTimeout(function() {{
            window.location = 'https://waze.com/ul?q=' + encodeURIComponent(addr);
        }}, 500);
        setTimeout(function() {{
            window.location = 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(addr);
        }}, 1000);
    }} else {{
        // Desktop: Use Google Maps
        window.location = 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(addr);
    }}
}})();
</script>
<body><p>Bezig met openen navigatie app...</p>
<p><a href="{google_url}">Google Maps</a> | 
<a href="{waze_url}">Waze</a> | 
<a href="{apple_url}">Apple Maps</a></p>
</body></html>"""
        
        # Convert to data URL (works without external server)
        import base64
        html_encoded = base64.b64encode(redirect_html.encode('utf-8')).decode('utf-8')
        maps_url = f"data:text/html;base64,{html_encoded}"

        # Genereer QR met de online URL
        qr = qrcode.QRCode(version=1, box_size=1, border=1)
        qr.add_data(maps_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white').resize((50, 50), Image.LANCZOS)
        bon_win.qr_photo = ImageTk.PhotoImage(qr_img)

        qr_lbl = Label(qr_code_frame, image=bon_win.qr_photo, anchor="center")
        qr_lbl.pack(anchor="center")
        Label(qr_code_frame, text="Scan voor navigatie", font=("Courier", 6), anchor="center").pack(
            anchor="center", pady=(0, 3))

    except ImportError:
        Label(qr_code_frame, text="[QR-code niet\nbeschikbaar]", 
              fg='orange', anchor="center", font=("Courier", 6), justify="center").pack(anchor="center")
    except Exception as e:
        Label(qr_code_frame, text=f"[QR-fout:\n{e}]", fg='red', anchor="center", font=("Courier", 6)).pack(anchor="center")

    # Knoppen voor Printen en Sluiten
    button_frame = Frame(main_bon_frame, pady=5)
    button_frame.pack(side="bottom", fill="x")

    # ScrolledText widget voor het afdrukvoorbeeld
    bon_display = scrolledtext.ScrolledText(
        main_bon_frame,
        wrap=tk.NONE,
        font=("Courier", 8),
        width=bon_width_from_generator,
        height=34
    )
    bon_display.pack(fill="both", expand=True)

    # Vul de bon_display met de volledige tekst
    bon_display.insert(tk.END, full_bon_text_for_print)
    bon_display.config(state='disabled')

    def print_bon_action():
        save_and_print_callback(full_bon_text_for_print, address_for_qr, klant_data)
        bon_win.destroy()

    # Knoppen toevoegen
    Button(button_frame, text="Afdrukken", command=print_bon_action, bg="#D1FFD1").pack(side="left", padx=(0, 5))
    Button(button_frame, text="Sluiten", command=bon_win.destroy, bg="#FFADAD").pack(side="right")

    # Keyboard shortcuts
    def handle_print_shortcut(event=None):
        print_bon_action()

    bon_win.bind("<Control-p>", handle_print_shortcut)
    bon_win.bind("<Command-p>", handle_print_shortcut)
