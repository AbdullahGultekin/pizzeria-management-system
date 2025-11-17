"""Address and postcode utility functions."""

import json
import tkinter as tk
from typing import List, Dict, Any, Optional
from tkinter import Entry, Listbox, StringVar
from database import DatabaseContext

# Load street names once at module level
def _load_straatnamen() -> List[str]:
    """Load street names from JSON file."""
    try:
        with open("straatnamen.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

straatnamen = _load_straatnamen()


def suggest_straat(zoekterm: str) -> List[str]:
    """Suggest street names based on search term."""
    zoekterm = zoekterm.lower().strip()
    return [naam for naam in straatnamen if zoekterm in naam.lower()]


def suggest_postcode(zoekterm: str, postcodes: List[str]) -> List[str]:
    """Suggest postcodes based on search term.
    
    Args:
        zoekterm: Search term to match
        postcodes: List of postcode strings (format: "1234 City")
        
    Returns:
        List of matching postcodes
    """
    zoekterm = zoekterm.strip().lower()
    return [pc for pc in postcodes
            if zoekterm in pc.lower()]


def voeg_adres_toe(straat: str, postcode: str, gemeente: str) -> None:
    """Add address to database."""
    with DatabaseContext() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO adressen (straat, postcode, gemeente) VALUES (?, ?, ?)",
            (straat, postcode, gemeente)
        )


def update_straatnamen_json(nieuwe_straat: str, json_path: str = "straatnamen.json") -> bool:
    """
    Update street names JSON file with new street name.
    
    Args:
        nieuwe_straat: New street name to add
        json_path: Path to JSON file
        
    Returns:
        True if street was added, False if it already existed
    """
    global straatnamen
    
    # Normalize street name (strip and capitalize first letter)
    nieuwe_straat = nieuwe_straat.strip()
    if not nieuwe_straat:
        return False
    
    # Load existing data
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    
    # Check if street already exists (case-insensitive)
    nieuwe_straat_lower = nieuwe_straat.lower()
    if any(straat.lower() == nieuwe_straat_lower for straat in data):
        return False  # Street already exists
    
    # Add new street
    data.append(nieuwe_straat)
    # Sort alphabetically for better organization
    data.sort(key=str.lower)
    
    # Save to file
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Update module-level variable
    straatnamen = data
    return True


def reload_straatnamen() -> None:
    """Reload street names from JSON file."""
    global straatnamen
    straatnamen = _load_straatnamen()


def on_adres_entry(
    event: tk.Event,
    adres_entry: Entry,
    lb_suggesties: Listbox
) -> None:
    """Handle address entry key release event."""
    typed_str = adres_entry.get()
    lb_suggesties.delete(0, tk.END)
    
    # Only show suggestions if user has typed at least 2 characters
    if len(typed_str.strip()) < 2:
        # Hide listbox - check which geometry manager is used
        try:
            lb_suggesties.grid_remove()
        except:
            try:
                lb_suggesties.pack_forget()
            except:
                pass
        return
    
    suggesties = suggest_straat(typed_str)
    if suggesties:
        # Limit to 10 suggestions for better UX
        for s in suggesties[:10]:
            lb_suggesties.insert(tk.END, s)
        # Show listbox - check which geometry manager is used
        # First check if it's currently using grid
        try:
            # Try to get grid info - if it works, use grid
            lb_suggesties.grid_info()
            lb_suggesties.grid()
        except:
            # If grid doesn't work, try pack
            try:
                lb_suggesties.pack()
            except:
                # If both fail, just make it visible
                try:
                    lb_suggesties.grid()
                except:
                    pass
    else:
        # Hide listbox
        try:
            lb_suggesties.grid_remove()
        except:
            try:
                lb_suggesties.pack_forget()
            except:
                pass


def selectie_suggestie(
    event: tk.Event,
    adres_entry: Entry,
    lb_suggesties: Listbox
) -> None:
    """Handle street suggestion selection."""
    if lb_suggesties.curselection():
        keuze = lb_suggesties.get(lb_suggesties.curselection())
        adres_entry.delete(0, tk.END)
        adres_entry.insert(0, keuze)
        lb_suggesties.grid_remove()

