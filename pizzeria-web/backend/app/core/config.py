"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Pizzeria Management API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Pizzeria Management System"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3002",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:5173",
    ]
    
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from environment variable or use default."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # Database
    # Use database in backend directory (where import_menu.py creates it)
    _db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "pizzeria.db")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{_db_path}"  # Point to backend directory
    )
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Printer
    PRINTER_ENABLED: bool = os.getenv("PRINTER_ENABLED", "false").lower() == "true"
    PRINTER_NAME: Optional[str] = os.getenv("PRINTER_NAME", "EPSON TM-T20II Receipt5")
    
    # Email (SMTP)
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST", None)
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER", None)
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD", None)
    SMTP_FROM_EMAIL: Optional[str] = os.getenv("SMTP_FROM_EMAIL", "noreply@pitapizzanapoli.be")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    # Email Verification
    EMAIL_VERIFICATION_REQUIRED: bool = os.getenv("EMAIL_VERIFICATION_REQUIRED", "true").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

