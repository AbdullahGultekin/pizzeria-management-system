"""
Courier Management Configuration

This module contains constants and configuration for the courier management system.
"""

# Payment rates
STARTGELD = 31.0  # Starting money per courier
KM_TARIEF = 0.25  # Rate per kilometer
UUR_TARIEF = 10.0  # Rate per hour

# UI Colors - Improved with better contrast and colorblind-friendly options
# Format: (background, foreground, border) - optimized for readability
CARD_COLORS = [
    ("#FFF3CD", "#856404", "#FFC107"),  # Yellow - high contrast
    ("#D1ECF1", "#0C5460", "#17A2B8"),  # Blue - colorblind friendly
    ("#D4EDDA", "#155724", "#28A745"),  # Green - high contrast
    ("#E2D9F3", "#4A148C", "#6F42C1"),  # Purple - distinct
    ("#FDEBD0", "#B7791F", "#FF9800"),  # Orange - warm, distinct
    ("#E1BEE7", "#4A148C", "#9C27B0"),  # Indigo/Purple variant
    ("#B2EBF2", "#006064", "#00BCD4"),  # Cyan - bright, distinct
    ("#FFE0B2", "#E65100", "#FF9800"),  # Orange variant
]

# Table row colors - improved contrast
ROW_COLOR_A = "#F8F9FA"  # Very light gray (zebra) - better contrast
ROW_COLOR_B = "#FFFFFF"  # White (zebra)

# Status colors - clear visual indicators
UNASSIGNED_COLOR = "#FFF3CD"  # Light yellow for unassigned orders
UNASSIGNED_TEXT = "#856404"   # Dark yellow text for contrast
ASSIGNED_COLOR = "#D1ECF1"    # Light blue for assigned orders
ONLINE_COLOR = "#E3F2FD"      # Light blue for online orders
URGENT_COLOR = "#F8D7DA"      # Light red for urgent orders
URGENT_TEXT = "#721C24"      # Dark red text for contrast

# Colorblind-friendly alternative palette (optional)
COLORBLIND_COLORS = [
    ("#F0F0F0", "#333333", "#808080"),  # Gray scale
    ("#E8F4F8", "#2C3E50", "#3498DB"),  # Blue tones
    ("#F5E6D3", "#8B4513", "#D2691E"),  # Brown tones
    ("#E8F8E8", "#2D5016", "#52B788"),  # Green tones
]

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



