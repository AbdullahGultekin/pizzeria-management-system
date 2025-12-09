import tkinter as tk
from tkinter import ttk, Entry, StringVar
from typing import List
import database
from database import DatabaseContext
import threading
from queue import Queue


def open_klanten_zoeken(
    root: tk.Tk,
    tel_entry: Entry,
    naam_entry: Entry,
    adres_entry: Entry,
    nr_entry: Entry,
    postcode_var: StringVar,
    postcodes_lijst: List[str]
) -> None:
    """Open klant-zoekvenster in een apart Toplevel (hoofdschema blijft intact)."""
    top = tk.Toplevel(root)
    top.title("Klant zoeken")
    top.transient(root)
    top.grab_set()

    tk.Label(top, text="Zoek op Telefoonnummer:", font=("Arial", 11)).pack(pady=(10, 2), padx=10, anchor="w")

    zoek_var = tk.StringVar()
    zoek_entry = tk.Entry(top, textvariable=zoek_var, font=("Arial", 11))
    zoek_entry.pack(fill=tk.X, padx=10)
    zoek_entry.focus()

    result_frame = tk.Frame(top)
    result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    cols = ('telefoon', 'naam', 'adres')
    tree = ttk.Treeview(result_frame, columns=cols, show='headings', height=12)
    tree.heading('telefoon', text='Telefoonnummer')
    tree.heading('naam', text='Naam')
    tree.heading('adres', text='Adres')
    tree.column('telefoon', width=120)
    tree.column('naam', width=150)
    tree.column('adres', width=250)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Threading support for async search
    search_queue = Queue()
    searching = False
    search_lock = threading.Lock()

    def update_zoekresultaten(*_: str) -> None:
        """Update search results - uses async loading to prevent UI blocking."""
        term = zoek_var.get().strip()
        tree.delete(*tree.get_children())
        
        if not term:
            return
        
        # Use async search to prevent UI blocking
        def search_worker():
            """Background thread worker for database search."""
            try:
                with DatabaseContext() as conn:
                    cur = conn.execute(
                        "SELECT id, telefoon, naam, straat, huisnummer FROM klanten WHERE telefoon LIKE ?",
                        (f"%{term}%",)
                    )
                    results = []
                    for r in cur.fetchall():
                        adres = f"{r['straat'] or ''} {r['huisnummer'] or ''}".strip()
                        results.append((str(r['id']), r['telefoon'], r['naam'] or "", adres))
                    
                    # Put results in queue for main thread
                    search_queue.put(("success", results))
            except Exception as e:
                search_queue.put(("error", str(e)))
            finally:
                with search_lock:
                    nonlocal searching
                    searching = False
        
        # Start search in background thread
        with search_lock:
            if searching:
                return  # Already searching
            searching = True
        
        thread = threading.Thread(target=search_worker, daemon=True)
        thread.start()
        
        # Check queue for results
        check_search_queue()
    
    def check_search_queue():
        """Check for search results from background thread."""
        try:
            while True:
                result_type, data = search_queue.get_nowait()
                
                if result_type == "success":
                    # Update UI from main thread (thread-safe)
                    # Clear tree first
                    tree.delete(*tree.get_children())
                    
                    # Add results
                    for item_id, telefoon, naam, adres in data:
                        tree.insert("", "end", iid=item_id, values=(telefoon, naam, adres))
                elif result_type == "error":
                    # Show error (optional - can be silent for search)
                    pass
        except:
            pass  # Queue empty
        
        # Continue checking if still searching
        with search_lock:
            if searching:
                top.after(100, check_search_queue)

    def selecteer_klant_en_sluit() -> None:
        sel = tree.selection()
        if not sel:
            return
        klant_id = int(sel[0])
        with DatabaseContext() as conn:
            k = conn.execute("SELECT * FROM klanten WHERE id = ?", (klant_id,)).fetchone()
        if not k:
            return
        try:
            tel_entry.delete(0, tk.END);
            tel_entry.insert(0, k['telefoon'] or "")
            naam_entry.delete(0, tk.END);
            naam_entry.insert(0, k['naam'] or "")
            adres_entry.delete(0, tk.END);
            adres_entry.insert(0, k['straat'] or "")
            nr_entry.delete(0, tk.END);
            nr_entry.insert(0, k['huisnummer'] or "")
            plaats = k['plaats'] or ""
            match = next((p for p in postcodes_lijst if plaats in p), "")
            postcode_var.set(match if match else postcodes_lijst[0])
        except tk.TclError:
            pass
        top.destroy()

    zoek_var.trace_add("write", update_zoekresultaten)
    tree.bind("<Double-1>", lambda e: selecteer_klant_en_sluit())

    btns = tk.Frame(top, padx=10)
    btns.pack(fill=tk.X, pady=(0, 10))
    tk.Button(btns, text="Selecteer Klant", command=selecteer_klant_en_sluit, bg="#D1FFD1").pack(side=tk.LEFT)
    tk.Button(btns, text="Sluiten", command=top.destroy).pack(side=tk.RIGHT)