"""
Courier Management Configuration

This module contains constants and configuration for the courier management system.
"""

# Payment rates
STARTGELD = 31.0  # Starting money per courier
KM_TARIEF = 0.25  # Rate per kilometer
UUR_TARIEF = 10.0  # Rate per hour

# UI Colors
CARD_COLORS = [
    ("#FFF3CD", "#7A5E00"),  # Yellow
    ("#E3F2FD", "#0D47A1"),  # Blue
    ("#E8F5E9", "#1B5E20"),  # Green
    ("#F3E5F5", "#4A148C"),  # Purple
    ("#FFEDE7", "#BF360C"),  # Orange
    ("#EDE7F6", "#283593"),  # Indigo
    ("#E0F7FA", "#006064"),  # Cyan
    ("#FFF8E1", "#8D6E63"),  # Brown
]

# Table row colors
ROW_COLOR_A = "#E6EBFF"  # Light blue (zebra)
ROW_COLOR_B = "#FFFFFF"  # White (zebra)
UNASSIGNED_COLOR = "#FFEB99"  # Yellow for unassigned orders

# Table configuration
TABLE_COLUMNS = ("tijd", "adres", "nr", "gemeente", "tel", "totaal", "koerier")
TABLE_HEADERS = {
    "tijd": "Tijd",
    "adres": "Adres",
    "nr": "Nr",
    "gemeente": "Gemeente",
    "tel": "Tel",
    "totaal": "Totaal (€)",
    "koerier": "Koerier"
}
TABLE_WIDTHS = {
    "tijd": 70,
    "adres": 240,
    "nr": 50,
    "gemeente": 150,
    "tel": 120,
    "totaal": 90,
    "koerier": 140
}



