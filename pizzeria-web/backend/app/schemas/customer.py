"""
Customer Pydantic schemas.
"""
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
import html
from app.utils.phone_validator import validate_phone_number


class CustomerBase(BaseModel):
    """Base customer schema."""
    telefoon: str = Field(..., min_length=10, max_length=15)
    naam: Optional[str] = Field(None, max_length=100)
    straat: Optional[str] = Field(None, max_length=200)
    huisnummer: Optional[str] = Field(None, max_length=20)
    plaats: Optional[str] = Field(None, max_length=100)
    notities: Optional[str] = None
    voorkeur_levering: Optional[str] = None
    
    @validator('telefoon')
    def validate_phone(cls, v):
        """Validate and clean phone number."""
        cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
        if len(cleaned) < 10:
            raise ValueError('Ongeldig telefoonnummer')
        return cleaned
    
    @validator('naam', 'straat', 'plaats')
    def sanitize_input(cls, v):
        """Sanitize input to prevent XSS."""
        if v:
            return html.escape(v.strip())
        return v


class CustomerCreate(CustomerBase):
    """Schema for creating a customer."""
    pass


class CustomerUpdate(BaseModel):
    """Schema for updating a customer."""
    naam: Optional[str] = Field(None, max_length=100)
    straat: Optional[str] = Field(None, max_length=200)
    huisnummer: Optional[str] = Field(None, max_length=20)
    plaats: Optional[str] = Field(None, max_length=100)
    notities: Optional[str] = None
    voorkeur_levering: Optional[str] = None


class CustomerRegister(BaseModel):
    """Schema for customer registration."""
    email: EmailStr = Field(..., description="E-mailadres (wordt gebruikt als gebruikersnaam)")
    password: str = Field(..., min_length=6, max_length=100, description="Wachtwoord (minimaal 6 tekens)")
    telefoon: str = Field(..., description="Telefoonnummer (alle EU landen)")
    naam: str = Field(..., min_length=2, max_length=100)
    straat: Optional[str] = Field(None, max_length=200)
    huisnummer: Optional[str] = Field(None, max_length=20)
    plaats: Optional[str] = Field(None, max_length=100)
    
    @validator('email')
    def validate_email(cls, v):
        """Validate and normalize email."""
        if not v:
            raise ValueError('E-mailadres is verplicht')
        # Additional validation beyond EmailStr
        email_lower = v.lower().strip()
        if len(email_lower) < 5:
            raise ValueError('E-mailadres is te kort')
        if '@' not in email_lower or '.' not in email_lower.split('@')[1]:
            raise ValueError('Ongeldig e-mailadres formaat')
        return email_lower
    
    @validator('telefoon')
    def validate_phone(cls, v):
        """Validate and normalize phone number for EU countries."""
        is_valid, normalized, error_msg = validate_phone_number(v)
        if not is_valid:
            raise ValueError(error_msg or 'Ongeldig telefoonnummer. Alleen EU landen toegestaan.')
        return normalized


class CustomerLogin(BaseModel):
    """Schema for customer login."""
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    
    @validator('email')
    def validate_email(cls, v):
        """Normalize email."""
        return v.lower().strip()


class CustomerResponse(CustomerBase):
    """Schema for customer response."""
    id: int
    email: Optional[str] = None
    email_verified: int = 0  # 0 = not verified, 1 = verified
    totaal_bestellingen: int = 0
    totaal_besteed: float = 0.0
    volle_kaart: int = 0
    laatste_bestelling: Optional[str] = None
    
    class Config:
        from_attributes = True


class CustomerTokenResponse(BaseModel):
    """Schema for customer login response with token."""
    access_token: str
    token_type: str = "bearer"
    customer: CustomerResponse


class CustomerRegisterResponse(BaseModel):
    """Schema for customer registration response (before email verification)."""
    message: str
    email: str
    requires_verification: bool = True


