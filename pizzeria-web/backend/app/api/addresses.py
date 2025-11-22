"""
Address API endpoints for street names and address lookup.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
import json
import os
from app.core.database import get_db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Postcode and gemeente mapping
POSTCODES = [
    "2070 Zwijndrecht",
    "4568 Nieuw-Namen",
    "9100 Nieuwkerken-Waas",
    "9100 Sint-Niklaas",
    "9120 Beveren",
    "9120 Vrasene",
    "9120 Haasdonk",
    "9120 Kallo",
    "9120 Melsele",
    "9130 Verrebroek",
    "9130 Kieldrecht",
    "9130 Doel",
    "9170 Klein meerdonk",
    "9170 Meerdonk",
    "9170 Sint-Gillis-Waas",
    "9170 De Klinge"
]

def parse_postcode(postcode_str: str) -> Dict[str, str]:
    """Parse postcode string like '9120 Vrasene' into postcode and gemeente."""
    parts = postcode_str.strip().split(' ', 1)
    if len(parts) == 2:
        return {"postcode": parts[0], "gemeente": parts[1]}
    return {"postcode": parts[0], "gemeente": ""}


class AddressSuggestion(BaseModel):
    """Address suggestion model."""
    straat: str
    postcode: str
    gemeente: str


@router.get("/addresses/streets")
async def get_street_names():
    """
    Get all street names from straatnamen.json (public endpoint, no authentication required).
    """
    try:
        # Get the project root (where straatnamen.json should be)
        # __file__ is at: pizzeria-web/backend/app/api/addresses.py
        # We need to go: backend -> pizzeria-web -> project root
        current_file = os.path.abspath(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))  # pizzeria-web
        project_root = os.path.dirname(backend_dir)  # Project root (Deskcomputer)
        
        # Try multiple possible paths
        possible_paths = [
            os.path.join(project_root, "straatnamen.json"),  # Project root
            os.path.join(os.path.dirname(project_root), "straatnamen.json"),  # One level up from project
            "straatnamen.json",  # Current directory
            os.path.join("..", "straatnamen.json"),  # Parent directory
            os.path.join("..", "..", "straatnamen.json"),  # Two levels up
            os.path.join("..", "..", "..", "straatnamen.json"),  # Three levels up
        ]
        
        json_path = None
        for path in possible_paths:
            abs_path = os.path.abspath(path) if not os.path.isabs(path) else path
            if os.path.exists(abs_path):
                json_path = abs_path
                break
        
        if not json_path:
            logger.warning(f"straatnamen.json not found. Searched paths: {possible_paths}")
            logger.warning(f"Current file location: {current_file}")
            logger.warning(f"Project root: {project_root}")
            return {"streets": []}
        
        with open(json_path, "r", encoding="utf-8") as f:
            streets = json.load(f)
        
        logger.info(f"Loaded {len(streets)} street names from {json_path}")
        return {"streets": streets}
    except Exception as e:
        logger.error(f"Error loading street names: {e}", exc_info=True)
        return {"streets": []}


@router.get("/addresses/lookup")
async def lookup_address(
    straat: str,
    db: Session = Depends(get_db)
):
    """
    Lookup postcode and gemeente for a given street name from database (public endpoint).
    Falls back to default postcode list if not found in database.
    """
    if not straat or not straat.strip():
        return {"postcode": None, "gemeente": None}
    
    straat_clean = straat.strip()
    
    try:
        # First try to query adressen table if it exists
        try:
            result = db.execute(
                text("SELECT postcode, gemeente FROM adressen WHERE straat = :straat LIMIT 1"),
                {"straat": straat_clean}
            ).fetchone()
            
            if result:
                postcode = result[0] or ""
                gemeente = result[1] or ""
                # If postcode is just numbers, try to find matching postcode from list
                if postcode.isdigit() and gemeente:
                    # Format as "9120 Vrasene"
                    return {
                        "postcode": f"{postcode} {gemeente}",
                        "gemeente": gemeente
                    }
                elif postcode and gemeente:
                    return {
                        "postcode": postcode,
                        "gemeente": gemeente
                    }
        except Exception as db_error:
            logger.debug(f"Database query failed (table might not exist): {db_error}")
        
        # If not found in database, try to match street name patterns with known postcodes
        # For now, default to Vrasene (most common)
        default_postcode = parse_postcode("9120 Vrasene")
        return {
            "postcode": default_postcode["postcode"],
            "gemeente": default_postcode["gemeente"]
        }
        
    except Exception as e:
        logger.warning(f"Error looking up address: {e}")
        # Default to Vrasene if error
        default_postcode = parse_postcode("9120 Vrasene")
        return {
            "postcode": default_postcode["postcode"],
            "gemeente": default_postcode["gemeente"]
        }


@router.get("/addresses/postcodes")
async def get_postcodes():
    """
    Get all available postcodes and gemeentes (public endpoint).
    """
    return {
        "postcodes": POSTCODES,
        "mapping": [parse_postcode(pc) for pc in POSTCODES]
    }


@router.get("/addresses/suggestions")
async def get_address_suggestions(
    straat: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get address suggestions based on street name (public endpoint).
    Returns list of addresses with straat, postcode, and gemeente.
    """
    suggestions = []
    
    try:
        if straat and straat.strip():
            # Query adressen table for matching streets
            result = db.execute(
                text("SELECT DISTINCT straat, postcode, gemeente FROM adressen WHERE straat LIKE :straat LIMIT 20"),
                {"straat": f"%{straat.strip()}%"}
            ).fetchall()
            
            suggestions = [
                {
                    "straat": row[0],
                    "postcode": row[1],
                    "gemeente": row[2]
                }
                for row in result
            ]
    except Exception as e:
        logger.warning(f"Error getting address suggestions: {e}")
    
    return {"suggestions": suggestions}

