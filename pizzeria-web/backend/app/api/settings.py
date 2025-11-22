"""
Settings API endpoints for public information.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def load_settings() -> Dict[str, Any]:
    """Load settings from settings.json file."""
    # Try multiple paths to find settings.json
    # Backend is in pizzeria-web/backend, settings.json is in project root
    current_file = Path(__file__).resolve()
    # From backend/app/api/settings.py -> go up 4 levels to project root
    # backend/app/api/settings.py -> backend/app/api -> backend/app -> backend -> project root
    project_root = current_file.parent.parent.parent.parent
    
    possible_paths = [
        project_root / "settings.json",  # Project root
        project_root.parent / "settings.json",  # One level up from project root
        Path("settings.json"),  # Current working directory
        Path("../settings.json"),  # Parent of current working directory
        Path("../../settings.json"),  # Two levels up
        Path("../../../settings.json"),  # Three levels up
        Path("../../../../settings.json"),  # Four levels up
    ]
    
    for path in possible_paths:
        try:
            # Resolve relative paths
            if not path.is_absolute():
                path_resolved = path.resolve()
            else:
                path_resolved = path
            
            if path_resolved.exists() and path_resolved.is_file():
                try:
                    with open(path_resolved, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        logger.info(f"Successfully loaded settings from {path_resolved}")
                        return data
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in settings file {path_resolved}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error loading settings from {path_resolved}: {e}")
                    continue
        except Exception as e:
            # Skip paths that can't be resolved
            logger.debug(f"Could not resolve path {path}: {e}")
            continue
    
    # Return default if file not found
    logger.warning(f"settings.json not found in any expected location. Searched: {[str(p) for p in possible_paths]}")
    return {
        "customer_info": {
            "message": "Beste klanten,\n\nLevertijd in het weekend kan oplopen tot 75 minuten.\n\nMet vriendelijke groeten,\nPita Pizza Napoli"
        }
    }


@router.get("/settings/customer-info")
async def get_customer_info() -> Dict[str, Any]:
    """
    Get customer information message (public endpoint, no authentication required).
    """
    try:
        settings = load_settings()
        customer_info = settings.get("customer_info", {})
        
        # Default message if not found
        if not customer_info or "message" not in customer_info:
            customer_info = {
                "message": "Beste klanten,\n\nLevertijd in het weekend kan oplopen tot 75 minuten.\n\nMet vriendelijke groeten,\nPita Pizza Napoli"
            }
        
        return customer_info
    except Exception as e:
        logger.error(f"Error getting customer info: {str(e)}", exc_info=True)
        # Return default message on error
        return {
            "message": "Beste klanten,\n\nLevertijd in het weekend kan oplopen tot 75 minuten.\n\nMet vriendelijke groeten,\nPita Pizza Napoli"
        }


@router.get("/settings/delivery-zones")
async def get_delivery_zones() -> Dict[str, float]:
    """
    Get delivery zones with minimum delivery amounts per municipality (public endpoint).
    Returns a dictionary mapping municipality names to minimum delivery amounts.
    """
    default_zones = {
        "Zwijndrecht": 15.00,
        "Nieuw-Namen": 15.00,
        "Nieuwkerken-Waas": 15.00,
        "Sint-Niklaas": 15.00,
        "Beveren": 15.00,
        "Vrasene": 15.00,
        "Haasdonk": 15.00,
        "Kallo": 15.00,
        "Melsele": 15.00,
        "Verrebroek": 15.00,
        "Kieldrecht": 15.00,
        "Doel": 15.00,
        "Klein meerdonk": 15.00,
        "Meerdonk": 15.00,
        "Sint-Gillis-Waas": 15.00,
        "De Klinge": 15.00,
    }
    
    try:
        settings = load_settings()
        
        # Get delivery zones from settings, or use defaults
        delivery_zones = settings.get("delivery_zones", {})
        
        # If no delivery zones in settings, return default minimum amounts
        if not delivery_zones or not isinstance(delivery_zones, dict):
            logger.warning("No delivery zones found in settings, using defaults")
            return default_zones
        
        # Ensure all values are floats
        result = {}
        for gemeente, amount in delivery_zones.items():
            try:
                result[gemeente] = float(amount)
            except (ValueError, TypeError):
                logger.warning(f"Invalid amount for {gemeente}: {amount}, using default 15.00")
                result[gemeente] = 15.00
        
        return result
    except Exception as e:
        logger.error(f"Error getting delivery zones: {str(e)}", exc_info=True)
        # Return default on error
        return default_zones

