"""
Email verification service for customer accounts.
"""
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.services.notification import notification_service
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class EmailVerificationService:
    """Service for handling email verification."""
    
    def __init__(self):
        self.token_expiry_hours = 24  # Token expires after 24 hours
    
    def generate_verification_token(self) -> str:
        """Generate a secure random token for email verification."""
        return secrets.token_urlsafe(32)
    
    def create_verification_token(self, customer: Customer, db: Session) -> str:
        """
        Create and store verification token for customer.
        
        Args:
            customer: Customer to create token for
            db: Database session
            
        Returns:
            Verification token
        """
        token = self.generate_verification_token()
        expires_at = (datetime.utcnow() + timedelta(hours=self.token_expiry_hours)).isoformat()
        
        customer.verification_token = token
        customer.verification_token_expires = expires_at
        db.commit()
        
        logger.info(f"Verification token created for customer {customer.id} ({customer.email})")
        return token
    
    def verify_token(self, token: str, db: Session) -> Optional[Customer]:
        """
        Verify a token and mark email as verified.
        
        Args:
            token: Verification token
            db: Database session
            
        Returns:
            Customer if token is valid, None otherwise
        """
        if not token or not token.strip():
            logger.warning("Empty token provided to verify_token")
            return None
        
        # Clean the token (remove whitespace)
        clean_token = token.strip()
        
        customer = db.query(Customer).filter(Customer.verification_token == clean_token).first()
        
        if not customer:
            logger.warning(f"Invalid verification token attempted: {clean_token[:20]}...")
            return None
        
        logger.info(f"Found customer {customer.id} for token, checking expiration...")
        
        # Check if token expired
        if customer.verification_token_expires:
            try:
                expires_at = datetime.fromisoformat(customer.verification_token_expires)
                if datetime.utcnow() > expires_at:
                    logger.warning(f"Expired verification token for customer {customer.id}")
                    # Clear expired token
                    customer.verification_token = None
                    customer.verification_token_expires = None
                    db.commit()
                    return None
            except (ValueError, TypeError) as e:
                logger.error(f"Error parsing token expiration: {e}")
                # If we can't parse the expiration, consider token invalid
                customer.verification_token = None
                customer.verification_token_expires = None
                db.commit()
                return None
        else:
            # If no expiration date is set, consider token invalid for security
            logger.warning(f"Verification token for customer {customer.id} has no expiration date")
            customer.verification_token = None
            customer.verification_token_expires = None
            db.commit()
            return None
        
        # Mark email as verified
        customer.email_verified = 1
        customer.verification_token = None
        customer.verification_token_expires = None
        db.commit()
        
        logger.info(f"Email verified for customer {customer.id} ({customer.email})")
        return customer
    
    async def send_verification_email(self, customer: Customer, base_url: str = "http://localhost:3000", order_bonnummer: Optional[str] = None) -> bool:
        """
        Send verification email to customer.
        
        Args:
            customer: Customer to send email to
            base_url: Base URL for verification link
            
        Returns:
            True if email was sent successfully
        """
        if not customer.verification_token:
            logger.error(f"No verification token for customer {customer.id}")
            return False
        
        verification_link = f"{base_url}/verify-email?token={customer.verification_token}"
        
        email_subject = "Verifieer je e-mailadres - Pita Pizza Napoli"
        email_body = f"""
Beste {customer.naam or 'klant'},

Bedankt voor je registratie bij Pita Pizza Napoli!

Klik op de onderstaande link om je e-mailadres te verifiëren:

{verification_link}

Deze link is 24 uur geldig.

Als je deze link niet hebt aangevraagd, negeer dan deze e-mail.

Met vriendelijke groet,
Pita Pizza Napoli
Brugstraat 12, 9120 Vrasene
Tel: 03 775 72 28
www.pitapizzanapoli.be
        """
        
        try:
            # Use email service to send verification email
            success = await email_service.send_verification_email(
                to_email=customer.email,
                customer_name=customer.naam,
                verification_link=verification_link,
                order_bonnummer=order_bonnummer
            )
            
            if success:
                logger.info(f"Verification email sent to {customer.email}")
            else:
                logger.warning(f"Failed to send verification email to {customer.email}")
            
            return success
        except Exception as e:
            logger.error(f"Error sending verification email: {e}")
            return False
    
    def is_token_valid(self, token: str, db: Session) -> bool:
        """
        Check if a verification token is valid (not expired).
        
        Args:
            token: Verification token
            db: Database session
            
        Returns:
            True if token is valid, False otherwise
        """
        customer = db.query(Customer).filter(Customer.verification_token == token).first()
        
        if not customer:
            return False
        
        if not customer.verification_token_expires:
            return False
        
        try:
            expires_at = datetime.fromisoformat(customer.verification_token_expires)
            return datetime.utcnow() <= expires_at
        except (ValueError, TypeError):
            return False


# Global email verification service instance
email_verification_service = EmailVerificationService()

