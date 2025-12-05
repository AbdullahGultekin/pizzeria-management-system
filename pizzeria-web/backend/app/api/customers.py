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
    CustomerRegister, CustomerLogin, CustomerTokenResponse, CustomerRegisterResponse,
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.services.email_verification import email_verification_service
from app.services.password_reset import password_reset_service
from app.utils.password_validator import validate_password_strength
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


# IMPORTANT: Public routes must come BEFORE parameterized routes like /customers/{customer_id}
# FastAPI matches routes in order, so /customers/public must be defined before /customers/{customer_id}
# Otherwise, /customers/public could be matched as /customers/{customer_id} with customer_id="public"

# Public customer endpoints (no authentication required)
@router.post("/customers/public", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_customer_public(
    request: Request,
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new customer (public endpoint, no authentication required).
    Used during checkout.
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
    
    logger.info(f"Customer created (public): {db_customer.id} - {db_customer.telefoon}")
    return db_customer


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
        # Try to get base URL from Origin header, Referer header, or use configured FRONTEND_URL
        base_url = request.headers.get("Origin")
        if not base_url and request.headers.get("Referer"):
            # Extract base URL from Referer (remove path)
            referer = request.headers.get("Referer")
            base_url = referer.rsplit("/", 1)[0] if "/" in referer else referer
        if not base_url:
            base_url = settings.FRONTEND_URL
        logger.info(f"Sending verification email to {db_customer.email} with base_url: {base_url}")
        email_sent = await email_verification_service.send_verification_email(db_customer, base_url)
        
        if email_sent:
            logger.info(f"Customer registered (unverified): {db_customer.id} - {db_customer.email} - Verification email sent")
            message = "Registratie succesvol! Controleer je e-mail om je account te verifiëren. Je kunt pas inloggen na verificatie."
        else:
            logger.error(f"Customer registered (unverified): {db_customer.id} - {db_customer.email} - Verification email FAILED to send")
            logger.error("Check SMTP configuration: SMTP_HOST, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL must be set")
            message = (
                "Registratie succesvol, maar verificatie-e-mail kon niet worden verzonden. "
                "Neem contact op met de beheerder of probeer later opnieuw een verificatie-e-mail aan te vragen."
            )
        
        # Return response indicating email verification is required
        return CustomerRegisterResponse(
            message=message,
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
    logger.info(f"Verification attempt with token: {token[:20]}...")
    
    if not token or not token.strip():
        logger.warning("Empty token provided for verification")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ongeldige of verlopen verificatielink"
        )
    
    customer = email_verification_service.verify_token(token.strip(), db)
    
    if not customer:
        logger.warning(f"Verification failed for token: {token[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ongeldige of verlopen verificatielink"
        )
    
    logger.info(f"Email verified for customer {customer.id} ({customer.email})")
    
    return {
        "message": "E-mailadres succesvol geverifieerd! Je kunt nu inloggen.",
        "customer_id": customer.id,
        "email": customer.email
    }


@router.get("/customers/public/phone/{phone}", response_model=Optional[CustomerResponse])
@limiter.limit("30/minute")
async def get_customer_by_phone_public(
    request: Request,
    phone: str,
    db: Session = Depends(get_db)
):
    """
    Get customer by phone number (public endpoint, no authentication required).
    Returns null if not found (not 404).
    Used during checkout to check if customer exists.
    """
    # Clean phone number
    cleaned_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
    customer = db.query(Customer).filter(Customer.telefoon == cleaned_phone).first()
    if not customer:
        return None
    return customer


@router.put("/customers/public/{customer_id}", response_model=CustomerResponse)
@limiter.limit("30/minute")
async def update_customer_public(
    request: Request,
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a customer (public endpoint, no authentication required).
    Used during checkout.
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
    
    logger.info(f"Customer updated (public): {customer_id}")
    return customer


@router.post("/customers/public/resend-verification")
@limiter.limit("5/minute")
async def resend_verification_email(
    request: Request,
    email: str,
    db: Session = Depends(get_db)
):
    """
    Resend verification email (public endpoint).
    """
    customer = db.query(Customer).filter(Customer.email == email).first()
    if not customer:
        # Don't reveal if email exists or not for security
        return {"message": "Als dit e-mailadres geregistreerd is, is er een verificatielink verzonden."}
    
    if customer.email_verified == 1:
        return {"message": "Dit e-mailadres is al geverifieerd."}
    
    # Generate new verification token
    verification_token = email_verification_service.create_verification_token(customer, db)
    
    # Get base URL for verification link
    base_url = request.headers.get("Origin")
    if not base_url and request.headers.get("Referer"):
        referer = request.headers.get("Referer")
        base_url = referer.rsplit("/", 1)[0] if "/" in referer else referer
    if not base_url:
        base_url = settings.FRONTEND_URL
    
    email_sent = await email_verification_service.send_verification_email(customer, base_url)
    
    if email_sent:
        logger.info(f"Verification email resent to {customer.email}")
        return {"message": "Verificatielink is verzonden. Controleer je inbox."}
    else:
        logger.error(f"Failed to resend verification email to {customer.email}")
        return {
            "message": "Verificatielink kon niet worden verzonden. Neem contact op met de beheerder of probeer later opnieuw."
        }


@router.post("/customers/public/forgot-password")
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    forgot_request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset (public endpoint).
    Sends password reset email if customer exists.
    """
    # Find customer by email
    customer = db.query(Customer).filter(Customer.email == forgot_request.email).first()
    
    # Always return success message (don't reveal if email exists)
    # This prevents email enumeration attacks
    if not customer:
        logger.warning(f"Password reset requested for non-existent email: {forgot_request.email}")
        return {
            "message": "Als dit e-mailadres geregistreerd is, is er een wachtwoord reset link verzonden."
        }
    
    # Check if customer has verified email
    if customer.email_verified != 1:
        logger.warning(f"Password reset requested for unverified email: {forgot_request.email}")
        return {
            "message": "Als dit e-mailadres geregistreerd is, is er een wachtwoord reset link verzonden."
        }
    
    # Create reset token
    reset_token = password_reset_service.create_reset_token(customer, db)
    
    # Get base URL for reset link
    base_url = request.headers.get("Origin")
    if not base_url and request.headers.get("Referer"):
        referer = request.headers.get("Referer")
        base_url = referer.rsplit("/", 1)[0] if "/" in referer else referer
    if not base_url:
        base_url = settings.FRONTEND_URL
    
    # Send reset email
    email_sent = await password_reset_service.send_reset_email(customer, base_url)
    
    if email_sent:
        logger.info(f"Password reset email sent to {customer.email}")
        return {
            "message": "Als dit e-mailadres geregistreerd is, is er een wachtwoord reset link verzonden."
        }
    else:
        logger.error(f"Failed to send password reset email to {customer.email}")
        return {
            "message": "Als dit e-mailadres geregistreerd is, is er een wachtwoord reset link verzonden."
        }


@router.post("/customers/public/reset-password")
@limiter.limit("10/minute")
async def reset_password(
    request: Request,
    reset_request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password with token (public endpoint).
    """
    # Verify reset token
    customer = password_reset_service.verify_reset_token(reset_request.token, db)
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ongeldige of verlopen reset link. Vraag een nieuwe reset link aan."
        )
    
    # Validate password strength
    is_valid, error_message = validate_password_strength(reset_request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Hash new password
    from app.core.security import get_password_hash
    customer.password_hash = get_password_hash(reset_request.new_password)
    
    # Clear reset token
    password_reset_service.clear_reset_token(customer, db)
    
    logger.info(f"Password reset successful for customer {customer.id} ({customer.email})")
    
    return {
        "message": "Wachtwoord succesvol gereset. Je kunt nu inloggen met je nieuwe wachtwoord."
    }


# Authenticated customer endpoints (require authentication)
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
    Get customer by phone number (admin endpoint).
    Returns null if not found (not 404).
    """
    # Clean phone number
    cleaned_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
    customer = db.query(Customer).filter(Customer.telefoon == cleaned_phone).first()
    if not customer:
        return None
    return customer

