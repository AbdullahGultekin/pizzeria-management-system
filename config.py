"""
Configuration management for the pizzeria application.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from logging_config import get_logger

logger = get_logger("pizzeria.config")

# Default configuration
DEFAULT_SETTINGS = {
    "thermal_printer_name": "Default",
    "category_order": [],
    "product_order": {}  # Dict mapping category names to ordered product name lists
}

SETTINGS_FILE = "settings.json"


def load_settings() -> Dict[str, Any]:
    """
    Load application settings from file.
    
    Returns:
        Dictionary with settings
    """
    if not os.path.exists(SETTINGS_FILE):
        logger.info(f"Settings file not found, creating with defaults: {SETTINGS_FILE}")
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
            # Merge with defaults to ensure all keys exist
            merged = DEFAULT_SETTINGS.copy()
            merged.update(settings)
            return merged
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in settings file: {e}")
        return DEFAULT_SETTINGS.copy()
    except Exception as e:
        logger.exception(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: Dict[str, Any]) -> bool:
    """
    Save application settings to file.
    
    Args:
        settings: Settings dictionary to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        logger.info("Settings saved successfully")
        return True
    except Exception as e:
        logger.exception(f"Error saving settings: {e}")
        return False


def load_json_file(path: str, fallback_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Load JSON file with error handling.
    
    Args:
        path: Path to JSON file
        fallback_data: Optional fallback data if file doesn't exist
        
    Returns:
        Loaded JSON data or fallback
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if fallback_data is not None:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(fallback_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Created {path} with fallback data")
            except Exception as e:
                logger.error(f"Error creating {path}: {e}")
            return fallback_data
        logger.error(f"{path} niet gevonden!")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"{path} is geen geldige JSON: {e}")
        return {}
    except Exception as e:
        logger.exception(f"Error loading {path}: {e}")
        return {}


def save_json_file(path: str, data: Dict[str, Any]) -> bool:
    """
    Save JSON file with error handling.
    
    Args:
        path: Path to JSON file
        data: Data dictionary to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {path} successfully")
        return True
    except Exception as e:
        logger.exception(f"Error saving {path}: {e}")
        return False

