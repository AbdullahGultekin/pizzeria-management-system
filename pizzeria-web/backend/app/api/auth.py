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

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


# Temporary user store (replace with database later)
# In production, this should be in a database
# Lazy initialization to avoid bcrypt issues during module import
_USERS = None

def get_users():
    """Lazy initialization of users to avoid bcrypt issues."""
    global _USERS
    if _USERS is None:
        _USERS = {
            "admin": {
                "username": "admin",
                "hashed_password": get_password_hash("admin123"),  # Change in production!
                "role": "admin"
            },
            "kassa": {
                "username": "kassa",
                "hashed_password": get_password_hash("kassa123"),  # Change in production!
                "role": "kassa"
            }
        }
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

