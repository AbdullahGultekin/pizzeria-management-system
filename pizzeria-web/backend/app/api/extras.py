"""
Extras configuration API endpoints.
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.database import get_db
from app.core.dependencies import get_current_user
import json
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/extras/public")
async def get_public_extras(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get extras configuration from extras.json (public endpoint, no authentication required).
    """
    # Try to find extras.json in multiple locations
    possible_paths = [
        "../../extras.json",
        "../extras.json",
        "extras.json",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "extras.json"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    extras_data = json.load(f)
                    logger.info(f"Loaded extras from: {path}")
                    return extras_data
            except Exception as e:
                logger.error(f"Error loading extras from {path}: {e}")
                continue
    
    logger.warning("extras.json not found, returning empty config")
    return {}


@router.get("/extras")
async def get_extras(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get extras configuration from extras.json.
    """
    # Try to find extras.json in multiple locations
    possible_paths = [
        "../../extras.json",
        "../extras.json",
        "extras.json",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "extras.json"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    extras_data = json.load(f)
                    logger.info(f"Loaded extras from: {path}")
                    return extras_data
            except Exception as e:
                logger.error(f"Error loading extras from {path}: {e}")
                continue
    
    logger.warning("extras.json not found, returning empty config")
    return {}

