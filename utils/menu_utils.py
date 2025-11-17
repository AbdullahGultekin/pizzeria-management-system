"""Menu-related utility functions."""

import json
from typing import List, Dict, Any
from logging_config import get_logger
from config import load_json_file

logger = get_logger("pizzeria.utils.menu")


def get_pizza_num(naam: str) -> str:
    """Haalt het nummer voor de punt uit een pizzanaam.
    
    Args:
        naam: Pizza name (e.g., "1. Margherita")
        
    Returns:
        Pizza number (e.g., "1") or full name if no number found
    """
    if '.' in naam:
        return naam.split('.')[0].strip()
    return naam.strip()


def load_menu_categories() -> List[str]:
    """Load menu categories from menu.json.
    
    Returns:
        List of category names, or empty list if file not found
    """
    try:
        menu_data = load_json_file("menu.json", fallback_data={})
        if isinstance(menu_data, dict):
            return list(menu_data.keys())
        return []
    except Exception as e:
        logger.error(f"Error loading menu categories: {e}")
        return []



