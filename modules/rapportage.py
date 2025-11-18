import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import database
import json
from collections import defaultdict


def open_rapportage(root):
    # root is tab-frame
    win = root

    for w in win.winfo_children():
        w.destroy()

    paned = tk.PanedWindow(win, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashpad=4)
    paned.pack(fill=tk.BOTH, expand=True)

    # --- Linkerzijde: filters ---
    left = tk.Frame(paned, padx=10, pady=10)
    paned.add(left, minsize=260)

    tk.Label(left, text="Filters", font=("Arial", 13, "bold")).pack(anchor="w")

    periode_frame = tk.LabelFrame(left, text="Periode", padx=8, pady=8)
    periode_frame.pack(fill=tk.X, pady=(6, 10))

    periode_var = tk.StringVar(value="vandaag")
    opties = [("Vandaag", "vandaag"), ("Deze week", "week"), ("Deze maand", "maand"), ("Custom", "custom")]
    for text, val in opties:
        ttk.Radiobutton(periode_frame, text=text, value=val, variable=periode_var).pack(anchor="w")

    custom_frame = tk.Frame(periode_frame)
    custom_frame.pack(fill=tk.X, pady=(6, 0))
    tk.Label(custom_frame, text="Van (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
    from_var = tk.StringVar()
    tk.Entry(custom_frame, textvariable=from_var, width=12).grid(row=0, column=1, padx=(6, 0))
    tk.Label(custom_frame, text="Tot (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=(4, 0))
    to_var = tk.StringVar()
    tk.Entry(custom_frame, textvariable=to_var, width=12).grid(row=1, column=1, padx=(6, 0), pady=(4, 0))

    def get_date_range():
        today = datetime.date.today()
        if periode_var.get() == "vandaag":
            d1 = d2 = today
        elif periode_var.get() == "week":
            d1 = today - datetime.timedelta(days=today.weekday())
            d2 = today
        elif periode_var.get() == "maand":
            d1 = today.replace(day=1)
            d2 = today
        else:
            try:
                d1 = datetime.datetime.strptime(from_var.get(), "%Y-%m-%d").date()
                d2 = datetime.datetime.strptime(to_var.get(), "%Y-%m-%d").date()
            except Exception:
                messagebox.showwarning("Periode", "Voer geldige datums in (YYYY-MM-DD).")
                return None, None
        return d1, d2

    def refresh_all():
        d1, d2 = get_date_range()
        if not d1 or not d2:
            return
        load_omzet(d1, d2)
        load_populair(d1, d2)
        load_koeriers(d1, d2)

    ttk.Button(left, text="Toepassen", command=refresh_all).pack(anchor="w", pady=(4, 10))

    export_frame = tk.LabelFrame(left, text="Export", padx=8, pady=8)
    export_frame.pack(fill=tk.X)

    def export_excel(rows, headers, filename):
        try:
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.append(headers)
            for r in rows:
                ws.append(list(r))
            wb.save(filename)
            messagebox.showinfo("Export", f"Excel geëxporteerd naar {filename}")
        except ImportError:
            messagebox.showwarning("Export", "openpyxl niet gevonden. Valt terug op CSV.")
            export_csv(rows, headers, filename.replace(".xlsx", ".csv"))
        except Exception as e:
            messagebox.showerror("Export", f"Mislukt: {e}")

    export_data = {
        "omzet": ([], []),
        "populair": ([], []),
        "koeriers": ([], [])
    }

    ttk.Button(export_frame, text="Excel Omzet (.xlsx)",
               command=lambda: export_excel(*export_data["omzet"], "omzet.xlsx")).pack(fill=tk.X, pady=2)
    ttk.Button(export_frame, text="Excel Populair (.xlsx)",
               command=lambda: export_excel(*export_data["populair"], "populaire_producten.xlsx")).pack(fill=tk.X,
                                                                                                        pady=2)
    ttk.Button(export_frame, text="Excel Koeriers (.xlsx)",
               command=lambda: export_excel(*export_data["koeriers"], "koeriers.xlsx")).pack(fill=tk.X, pady=2)
    
    # Z-Rapport sectie
    zrapport_frame = tk.LabelFrame(left, text="Z-Rapport (Dagafsluiting)", padx=8, pady=8)
    zrapport_frame.pack(fill=tk.X, pady=(10, 0))
    
    def generate_z_rapport():
        """Genereer en toon Z-rapport voor vandaag."""
        today = datetime.date.today()
        today_str = today.strftime("%Y-%m-%d")
        
        conn = database.get_db_connection()
        cur = conn.cursor()
        
        # Haal alle bestellingen van vandaag op
        cur.execute("""
            SELECT 
                COUNT(*) AS totaal_bonnen,
                COALESCE(SUM(totaal), 0) AS totaal_omzet,
                MIN(tijd) AS eerste_bon,
                MAX(tijd) AS laatste_bon
            FROM bestellingen
            WHERE datum = ?
        """, (today_str,))
        
        summary = cur.fetchone()
        
        # Haal overzicht per uur op
        cur.execute("""
            SELECT 
                strftime('%H:00', tijd) AS uur,
                COUNT(*) AS aantal,
                COALESCE(SUM(totaal), 0) AS omzet
            FROM bestellingen
            WHERE datum = ?
            GROUP BY uur
            ORDER BY uur
        """, (today_str,))
        
        per_uur = cur.fetchall()
        
        # Haal overzicht per koerier op
        cur.execute("""
            SELECT 
                COALESCE(ko.naam, 'Niet toegewezen') AS koerier,
                COUNT(*) AS aantal,
                COALESCE(SUM(b.totaal), 0) AS omzet
            FROM bestellingen b
            LEFT JOIN koeriers ko ON ko.id = b.koerier_id
            WHERE b.datum = ?
            GROUP BY koerier
            ORDER BY omzet DESC
        """, (today_str,))
        
        per_koerier = cur.fetchall()
        
        conn.close()
        
        # Maak Z-rapport venster
        z_win = tk.Toplevel(win)
        z_win.title(f"Z-Rapport - {today.strftime('%d/%m/%Y')}")
        z_win.geometry("700x800")
        z_win.transient(win)
        
        # Scrollable text widget
        from tkinter import scrolledtext
        report_text = scrolledtext.ScrolledText(z_win, wrap=tk.WORD, font=("Courier", 10))
        report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Genereer rapport tekst
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append(" " * 15 + "Z-RAPPORT")
        report_lines.append(" " * 10 + "DAGAFSLUITING")
        report_lines.append("=" * 60)
        report_lines.append("")
        report_lines.append(f"Datum: {today.strftime('%d/%m/%Y')}")
        report_lines.append(f"Tijd: {datetime.datetime.now().strftime('%H:%M:%S')}")
        report_lines.append("")
        report_lines.append("-" * 60)
        report_lines.append("SAMENVATTING")
        report_lines.append("-" * 60)
        report_lines.append(f"Totaal aantal bonnen: {summary['totaal_bonnen']}")
        report_lines.append(f"Totale omzet: €{float(summary['totaal_omzet']):.2f}")
        if summary['eerste_bon']:
            report_lines.append(f"Eerste bon: {summary['eerste_bon']}")
            report_lines.append(f"Laatste bon: {summary['laatste_bon']}")
        if summary['totaal_bonnen'] > 0:
            gemiddeld = float(summary['totaal_omzet']) / summary['totaal_bonnen']
            report_lines.append(f"Gemiddeld per bon: €{gemiddeld:.2f}")
        report_lines.append("")
        
        report_lines.append("-" * 60)
        report_lines.append("OVERZICHT PER UUR")
        report_lines.append("-" * 60)
        report_lines.append(f"{'Uur':<10} {'Aantal':<10} {'Omzet (€)':<15}")
        report_lines.append("-" * 60)
        for row in per_uur:
            report_lines.append(f"{row['uur']:<10} {row['aantal']:<10} €{float(row['omzet']):.2f}")
        report_lines.append("")
        
        report_lines.append("-" * 60)
        report_lines.append("OVERZICHT PER KOERIER")
        report_lines.append("-" * 60)
        report_lines.append(f"{'Koerier':<20} {'Aantal':<10} {'Omzet (€)':<15}")
        report_lines.append("-" * 60)
        for row in per_koerier:
            report_lines.append(f"{row['koerier']:<20} {row['aantal']:<10} €{float(row['omzet']):.2f}")
        report_lines.append("")
        
        report_lines.append("=" * 60)
        report_lines.append(" " * 20 + "EINDE RAPPORT")
        report_lines.append("=" * 60)
        
        # Voeg tekst toe
        report_text.insert("1.0", "\n".join(report_lines))
        report_text.config(state=tk.DISABLED)
        
        # Knoppen
        button_frame = tk.Frame(z_win)
        button_frame.pack(pady=10)
        
        def print_z_rapport():
            """Print Z-rapport naar printer."""
            try:
                import win32print
                from config import load_settings
                
                app_settings = load_settings()
                printer_name = app_settings.get("thermal_printer_name", "Default")
                
                if not printer_name or printer_name == "Default":
                    messagebox.showwarning(
                        "Printer niet geconfigureerd",
                        "Er is geen printer geconfigureerd.\n\n"
                        "Ga naar Instellingen > Printer Instellingen om een printer te selecteren."
                    )
                    return
                
                try:
                    hprinter = win32print.OpenPrinter(printer_name)
                    try:
                        hjob = win32print.StartDocPrinter(hprinter, 1, ("Z-Rapport", None, "RAW"))
                        win32print.StartPagePrinter(hprinter)
                        
                        ESC = b'\x1b'
                        GS = b'\x1d'
                        
                        # Header
                        win32print.WritePrinter(hprinter, ESC + b'a' + b'\x01')  # Centreren
                        win32print.WritePrinter(hprinter, GS + b'!' + b'\x11')  # Groot
                        win32print.WritePrinter(hprinter, b'Z-RAPPORT\n')
                        win32print.WritePrinter(hprinter, GS + b'!' + b'\x00')  # Normale grootte
                        win32print.WritePrinter(hprinter, b'\n')
                        
                        # Print rapport
                        for line in report_lines:
                            win32print.WritePrinter(hprinter, (line + '\n').encode('cp858', errors='replace'))
                        
                        win32print.WritePrinter(hprinter, b'\n\n\n')
                        win32print.WritePrinter(hprinter, GS + b'V' + b'\x00')  # Snij papier
                        
                        win32print.EndPagePrinter(hprinter)
                        win32print.EndDocPrinter(hprinter)
                        
                        messagebox.showinfo("Voltooid", "Z-Rapport is afgedrukt!")
                    finally:
                        win32print.ClosePrinter(hprinter)
                except Exception as e:
                    messagebox.showerror("Fout", f"Kon Z-rapport niet afdrukken:\n{e}")
            except ImportError:
                messagebox.showerror("Fout", "Windows printer support niet beschikbaar.")
        
        tk.Button(button_frame, text="Print Z-Rapport", command=print_z_rapport, 
                 bg="#D1FFD1", font=("Arial", 10), padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Sluiten", command=z_win.destroy, 
                 bg="#FFADAD", font=("Arial", 10), padx=20).pack(side=tk.LEFT, padx=5)
    
    tk.Button(zrapport_frame, text="Genereer Z-Rapport (Vandaag)", 
             command=generate_z_rapport, bg="#FFE4B5", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=5)

    # --- Rechterzijde: tabs met rapporten ---
    right = tk.Frame(paned, padx=10, pady=10)
    paned.add(right, minsize=700)

    tabs = ttk.Notebook(right)
    tabs.pack(fill=tk.BOTH, expand=True)

    # Omzet tab
    omzet_tab = ttk.Frame(tabs)
    tabs.add(omzet_tab, text="Omzet")

    omzet_tree = ttk.Treeview(omzet_tab, columns=("periode", "orders", "omzet", "gemiddeld"), show="headings",
                              height=10)
    for col, text, w, anchor in [
        ("periode", "Periode", 160, "w"),
        ("orders", "Aantal orders", 120, "center"),
        ("omzet", "Omzet (€)", 120, "e"),
        ("gemiddeld", "Gem. per order (€)", 160, "e"),
    ]:
        omzet_tree.heading(col, text=text)
        omzet_tree.column(col, width=w, anchor=anchor)
    omzet_tree.pack(fill=tk.BOTH, expand=True)

    omzet_summary = tk.Label(omzet_tab, text="", font=("Arial", 11, "bold"))
    omzet_summary.pack(anchor="w", pady=(6, 0))

    # Populaire producten tab
    pop_tab = ttk.Frame(tabs)
    tabs.add(pop_tab, text="Populaire producten")

    pop_tree = ttk.Treeview(pop_tab, columns=("product", "categorie", "aantal", "omzet"), show="headings", height=14)
    for col, text, w, anchor in [
        ("product", "Product", 260, "w"),
        ("categorie", "Categorie", 160, "w"),
        ("aantal", "Aantal", 100, "center"),
        ("omzet", "Omzet (€)", 120, "e"),
    ]:
        pop_tree.heading(col, text=text)
        pop_tree.column(col, width=w, anchor=anchor)
    pop_tree.pack(fill=tk.BOTH, expand=True)

    # Koeriers tab
    koerier_tab = ttk.Frame(tabs)
    tabs.add(koerier_tab, text="Koeriers")

    koerier_tree = ttk.Treeview(koerier_tab, columns=("koerier", "orders", "omzet", "gem"), show="headings", height=14)
    for col, text, w, anchor in [
        ("koerier", "Koerier", 200, "w"),
        ("orders", "Aantal orders", 120, "center"),
        ("omzet", "Omzet (€)", 120, "e"),
        ("gem", "Gem. per order (€)", 160, "e"),
    ]:
        koerier_tree.heading(col, text=text)
        koerier_tree.column(col, width=w, anchor=anchor)
    koerier_tree.pack(fill=tk.BOTH, expand=True)

    def load_omzet(d1: datetime.date, d2: datetime.date):
        omzet_tree.delete(*omzet_tree.get_children())
        conn = database.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
                    SELECT datum, COUNT(*) AS orders, COALESCE(SUM(totaal), 0) AS omzet
                    FROM bestellingen
                    WHERE datum BETWEEN ? AND ?
                    GROUP BY datum
                    ORDER BY datum
                    """, (d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")))
        rows = cur.fetchall()

        total_orders = 0
        total_omzet = 0.0
        for r in rows:
            orders = r["orders"]
            omzet = float(r["omzet"])
            total_orders += orders
            total_omzet += omzet
            gem = (omzet / orders) if orders else 0.0
            periode_str = datetime.datetime.strptime(r["datum"], "%Y-%m-%d").strftime("%d/%m/%Y")
            omzet_tree.insert("", tk.END, values=(periode_str, orders, f"{omzet:.2f}", f"{gem:.2f}"))

        cur.execute("""
                    SELECT strftime('%Y-%W', datum) AS week, COUNT(*) AS orders, COALESCE(SUM(totaal), 0) AS omzet
                    FROM bestellingen
                    WHERE datum BETWEEN ? AND ?
                    GROUP BY week
                    ORDER BY week
                    """, (d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")))
        week_rows = cur.fetchall()
        cur.execute("""
                    SELECT strftime('%Y-%m', datum) AS maand, COUNT(*) AS orders, COALESCE(SUM(totaal), 0) AS omzet
                    FROM bestellingen
                    WHERE datum BETWEEN ? AND ?
                    GROUP BY maand
                    ORDER BY maand
                    """, (d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")))
        maand_rows = cur.fetchall()
        conn.close()

        omzet_tree.insert("", tk.END, values=("", "", "", ""))
        omzet_tree.insert("", tk.END, values=("Per week", "", "", ""))
        for r in week_rows:
            gem = (float(r["omzet"]) / r["orders"]) if r["orders"] else 0.0
            omzet_tree.insert("", tk.END,
                              values=(f"Week {r['week']}", r["orders"], f"{float(r['omzet']):.2f}", f"{gem:.2f}"))
        omzet_tree.insert("", tk.END, values=("", "", "", ""))
        omzet_tree.insert("", tk.END, values=("Per maand", "", "", ""))
        for r in maand_rows:
            gem = (float(r["omzet"]) / r["orders"]) if r["orders"] else 0.0
            omzet_tree.insert("", tk.END,
                              values=(f"Maand {r['maand']}", r["orders"], f"{float(r['omzet']):.2f}", f"{gem:.2f}"))

        omzet_summary.config(
            text=f"Totaal orders: {total_orders}   |   Totale omzet: €{total_omzet:.2f}   |   Gemiddeld per order: €{(total_omzet / total_orders if total_orders else 0):.2f}")
        export_data["omzet"] = ([(omzet_tree.set(i, "periode"), omzet_tree.set(i, "orders"), omzet_tree.set(i, "omzet"),
                                  omzet_tree.set(i, "gemiddeld")) for i in omzet_tree.get_children("")],
                                ["Periode", "Aantal orders", "Omzet (€)", "Gem. per order (€)"])

    def load_populair(d1: datetime.date, d2: datetime.date):
        pop_tree.delete(*pop_tree.get_children())
        conn = database.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
                    SELECT br.product,
                           br.categorie,
                           SUM(br.aantal)                         AS aantal,
                           COALESCE(SUM(br.aantal * br.prijs), 0) AS omzet
                    FROM bestelregels br
                             JOIN bestellingen b ON b.id = br.bestelling_id
                    WHERE b.datum BETWEEN ? AND ?
                    GROUP BY br.product, br.categorie
                    ORDER BY aantal DESC, omzet DESC LIMIT 200
                    """, (d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")))
        rows = cur.fetchall()
        conn.close()

        data = []
        for r in rows:
            pop_tree.insert("", tk.END, values=(r["product"], r["categorie"], r["aantal"], f"{float(r['omzet']):.2f}"))
            data.append((r["product"], r["categorie"], r["aantal"], f"{float(r['omzet']):.2f}"))

        export_data["populair"] = (data, ["Product", "Categorie", "Aantal", "Omzet (€)"])

    def load_koeriers(d1: datetime.date, d2: datetime.date):
        koerier_tree.delete(*koerier_tree.get_children())
        conn = database.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
                    SELECT COALESCE(ko.naam, 'Niet toegewezen') AS koerier,
                           COUNT(*)                             AS orders,
                           COALESCE(SUM(b.totaal), 0)           AS omzet
                    FROM bestellingen b
                             LEFT JOIN koeriers ko ON ko.id = b.koerier_id
                    WHERE b.datum BETWEEN ? AND ?
                    GROUP BY koerier
                    ORDER BY omzet DESC
                    """, (d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")))
        rows = cur.fetchall()
        conn.close()

        data = []
        for r in rows:
            orders = r["orders"]
            omzet = float(r["omzet"])
            gem = (omzet / orders) if orders else 0.0
            koerier_tree.insert("", tk.END, values=(r["koerier"], orders, f"{omzet:.2f}", f"{gem:.2f}"))
            data.append((r["koerier"], orders, f"{omzet:.2f}", f"{gem:.2f}"))

        export_data["koeriers"] = (data, ["Koerier", "Aantal orders", "Omzet (€)", "Gem. per order (€)"])

    # Init: vandaag
    periode_var.set("vandaag")
    refresh_all()