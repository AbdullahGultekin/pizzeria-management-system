"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user
from fastapi import Request
import logging
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def load_settings() -> dict:
    """Load settings from settings.json file."""
    # Try multiple paths to find settings.json
    current_file = Path(__file__).resolve()
    # From backend/app/api/auth.py -> go up 4 levels to project root
    project_root = current_file.parent.parent.parent.parent
    
    possible_paths = [
        project_root / "settings.json",  # Project root
        project_root.parent / "settings.json",  # One level up
        Path("settings.json"),  # Current working directory
        Path("../settings.json"),  # Parent directory
    ]
    
    for path in possible_paths:
        try:
            if not path.is_absolute():
                path_resolved = path.resolve()
            else:
                path_resolved = path
            
            if path_resolved.exists() and path_resolved.is_file():
                with open(path_resolved, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Successfully loaded settings from {path_resolved}")
                    return data
        except Exception as e:
            logger.debug(f"Could not load settings from {path}: {e}")
            continue
    
    logger.warning("settings.json not found, using default credentials")
    return {}


# Lazy initialization to avoid bcrypt issues during module import
_USERS = None

def get_users():
    """Load users from settings.json or use defaults."""
    global _USERS
    if _USERS is None:
        settings_data = load_settings()
        admin_credentials = settings_data.get("admin_credentials", {})
        
        # Default credentials if not in settings
        default_admin = admin_credentials.get("admin", {"username": "admin", "password": "admin123"})
        default_kassa = admin_credentials.get("kassa", {"username": "kassa", "password": "kassa123"})
        
        _USERS = {
            default_admin.get("username", "admin"): {
                "username": default_admin.get("username", "admin"),
                "hashed_password": get_password_hash(default_admin.get("password", "admin123")),
                "role": "admin"
            },
            default_kassa.get("username", "kassa"): {
                "username": default_kassa.get("username", "kassa"),
                "hashed_password": get_password_hash(default_kassa.get("password", "kassa123")),
                "role": "kassa"
            }
        }
        logger.info(f"Loaded users from settings: {list(_USERS.keys())}")
    return _USERS


def authenticate_user(username: str, password: str) -> dict:
    """
    Authenticate user and return user data if valid.
    
    Args:
        username: Username
        password: Plain text password
        
    Returns:
        User data dict or None if invalid
    """
    users = get_users()
    user = users.get(username)
    if not user:
        return None
    
    if not verify_password(password, user["hashed_password"]):
        return None
    
    return {
        "username": user["username"],
        "role": user["role"]
    }


@router.post("/auth/login")
@limiter.limit("30/minute")  # 30 login attempts per minute (more reasonable for development)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login endpoint - returns JWT token.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Successful login for {user['username']}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "role": user["role"]
        }
    }


@router.get("/auth/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user information.
    """
    return current_user

