"""
Customer API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_customer
from app.models.customer import Customer
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    CustomerRegister, CustomerLogin, CustomerTokenResponse, CustomerRegisterResponse
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.services.email_verification import email_verification_service
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/customers", response_model=List[CustomerResponse])
@limiter.limit("60/minute")
async def get_customers(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of customers with optional search.
    """
    query = db.query(Customer)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Customer.naam.ilike(search_term)) |
            (Customer.telefoon.ilike(search_term))
        )
    
    customers = query.offset(skip).limit(limit).all()
    return customers


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific customer by ID.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Klant niet gevonden"
        )
    return customer


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_customer(
    request: Request,
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new customer.
    """
    # Check if customer with phone already exists
    existing = db.query(Customer).filter(Customer.telefoon == customer.telefoon).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Klant met dit telefoonnummer bestaat al"
        )
    
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    logger.info(f"Customer created: {db_customer.id} - {db_customer.telefoon}")
    return db_customer


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a customer.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Klant niet gevonden"
        )
    
    update_data = customer_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    
    logger.info(f"Customer updated: {customer_id}")
    return customer


@router.get("/customers/phone/{phone}", response_model=Optional[CustomerResponse])
async def get_customer_by_phone(
    phone: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get customer by phone number.
    Returns null if not found (not 404).
    """
    # Clean phone number
    cleaned_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
    customer = db.query(Customer).filter(Customer.telefoon == cleaned_phone).first()
    if not customer:
        return None
    return customer


# Public customer endpoints (no authentication required)
@router.post("/customers/public/register", response_model=CustomerRegisterResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register_customer(
    request: Request,
    customer_data: CustomerRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new customer account (public endpoint).
    """
    logger.info(f"Registration attempt for email: {customer_data.email}, phone: {customer_data.telefoon}")
    
    try:
        # Check if email already exists
        existing_email = db.query(Customer).filter(Customer.email == customer_data.email).first()
        if existing_email:
            logger.warning(f"Registration failed: Email already exists - {customer_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="E-mailadres is al geregistreerd"
            )
        
        # Check if phone already exists
        existing_phone = db.query(Customer).filter(Customer.telefoon == customer_data.telefoon).first()
        if existing_phone:
            logger.warning(f"Registration failed: Phone already exists - {customer_data.telefoon}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Telefoonnummer is al geregistreerd"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error checking existing customer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Er is een fout opgetreden bij het controleren van bestaande gegevens"
        )
    
    # Hash password
    password_hash = get_password_hash(customer_data.password)
    
    # Check if email verification is required
    email_verification_required = settings.EMAIL_VERIFICATION_REQUIRED
    
    # Create customer
    db_customer = Customer(
        email=customer_data.email,
        password_hash=password_hash,
        telefoon=customer_data.telefoon,
        naam=customer_data.naam,
        straat=customer_data.straat,
        huisnummer=customer_data.huisnummer,
        plaats=customer_data.plaats,
        email_verified=1 if not email_verification_required else 0  # Auto-verify if verification disabled
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    if email_verification_required:
        # Generate verification token
        verification_token = email_verification_service.create_verification_token(db_customer, db)
        
        # Send verification email
        base_url = request.headers.get("Origin") or "http://localhost:3000"
        email_sent = await email_verification_service.send_verification_email(db_customer, base_url)
        
        if email_sent:
            logger.info(f"Customer registered (unverified): {db_customer.id} - {db_customer.email} - Verification email sent")
        else:
            logger.warning(f"Customer registered (unverified): {db_customer.id} - {db_customer.email} - Verification email FAILED to send")
        
        # Return response indicating email verification is required
        return CustomerRegisterResponse(
            message="Registratie succesvol! Controleer je e-mail om je account te verifiëren. Je kunt pas inloggen na verificatie.",
            email=db_customer.email,
            requires_verification=True
        )
    else:
        # Email verification disabled - auto-verify and return success
        logger.info(f"Customer registered (auto-verified): {db_customer.id} - {db_customer.email}")
        
        # Return success message (user can login immediately)
        return CustomerRegisterResponse(
            message="Registratie succesvol! Je kunt nu direct inloggen.",
            email=db_customer.email,
            requires_verification=False
        )


@router.post("/customers/public/login", response_model=CustomerTokenResponse)
@limiter.limit("10/minute")
async def login_customer(
    request: Request,
    login_data: CustomerLogin,
    db: Session = Depends(get_db)
):
    """
    Login customer (public endpoint).
    """
    # Find customer by email
    customer = db.query(Customer).filter(Customer.email == login_data.email).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ongeldig e-mailadres of wachtwoord"
        )
    
    # Verify password
    if not customer.password_hash or not verify_password(login_data.password, customer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ongeldig e-mailadres of wachtwoord"
        )
    
    # Check if email is verified (only if verification is required)
    if settings.EMAIL_VERIFICATION_REQUIRED and customer.email_verified != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Je e-mailadres is nog niet geverifieerd. Controleer je inbox en klik op de verificatielink. Je kunt ook een nieuwe link aanvragen."
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(customer.id), "email": customer.email, "type": "customer"},
        expires_delta=timedelta(days=30)  # 30 days for customers
    )
    
    logger.info(f"Customer logged in: {customer.id} - {customer.email}")
    
    return CustomerTokenResponse(
        access_token=access_token,
        customer=CustomerResponse.model_validate(customer)
    )


@router.get("/customers/public/me", response_model=CustomerResponse)
async def get_me(
    customer: Customer = Depends(get_current_customer)
):
    """
    Get current logged-in customer data (public endpoint).
    Requires valid customer token in Authorization header.
    """
    return CustomerResponse.model_validate(customer)


@router.get("/customers/public/verify-email")
@limiter.limit("10/minute")
async def verify_email(
    request: Request,
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify customer email with token (public endpoint).
    """
    customer = email_verification_service.verify_token(token, db)
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ongeldige of verlopen verificatielink"
        )
    
    logger.info(f"Email verified for customer {customer.id}")
    
    return {
        "message": "E-mailadres succesvol geverifieerd! Je kunt nu inloggen.",
        "customer_id": customer.id,
        "email": customer.email
    }


@router.post("/customers/public/resend-verification")
@limiter.limit("5/minute")
async def resend_verification_email(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Resend verification email (public endpoint).
    """
    from pydantic import BaseModel
    
    class ResendVerificationRequest(BaseModel):
        email: str
    
    body = await request.json()
    email_data = ResendVerificationRequest(**body)
    email = email_data.email
    
    customer = db.query(Customer).filter(Customer.email == email).first()
    
    if not customer:
        # Don't reveal if email exists or not for security
        return {"message": "Als dit e-mailadres geregistreerd is, is er een verificatielink verzonden."}
    
    if customer.email_verified == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mailadres is al geverifieerd"
        )
    
    # Generate new token
    verification_token = email_verification_service.create_verification_token(customer, db)
    
    # Send verification email
    base_url = request.headers.get("Origin") or "http://localhost:3000"
    await email_verification_service.send_verification_email(customer, base_url)
    
    logger.info(f"Verification email resent to {customer.email}")
    
    return {"message": "Verificatielink is opnieuw verzonden naar je e-mailadres."}

