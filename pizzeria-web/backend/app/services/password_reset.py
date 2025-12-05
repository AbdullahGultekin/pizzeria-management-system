"""
Password reset service for customer accounts.
"""
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.services.email_service import email_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class PasswordResetService:
    """Service for handling password resets."""
    
    def __init__(self):
        self.token_expiry_hours = 1  # Token expires after 1 hour (shorter than email verification)
    
    def generate_reset_token(self) -> str:
        """Generate a secure random token for password reset."""
        return secrets.token_urlsafe(32)
    
    def create_reset_token(self, customer: Customer, db: Session) -> str:
        """
        Create and store password reset token for customer.
        
        Args:
            customer: Customer to create token for
            db: Database session
            
        Returns:
            Reset token
        """
        token = self.generate_reset_token()
        expires_at = (datetime.utcnow() + timedelta(hours=self.token_expiry_hours)).isoformat()
        
        customer.password_reset_token = token
        customer.password_reset_token_expires = expires_at
        db.commit()
        
        logger.info(f"Password reset token created for customer {customer.id} ({customer.email})")
        return token
    
    def verify_reset_token(self, token: str, db: Session) -> Optional[Customer]:
        """
        Verify a password reset token.
        
        Args:
            token: Reset token
            db: Database session
            
        Returns:
            Customer if token is valid, None otherwise
        """
        customer = db.query(Customer).filter(Customer.password_reset_token == token).first()
        
        if not customer:
            logger.warning(f"Invalid password reset token attempted")
            return None
        
        # Check if token expired
        if customer.password_reset_token_expires:
            try:
                expires_at = datetime.fromisoformat(customer.password_reset_token_expires)
                if datetime.utcnow() > expires_at:
                    logger.warning(f"Expired password reset token for customer {customer.id}")
                    # Clear expired token
                    customer.password_reset_token = None
                    customer.password_reset_token_expires = None
                    db.commit()
                    return None
            except (ValueError, TypeError) as e:
                logger.error(f"Error parsing token expiration: {e}")
        
        return customer
    
    def clear_reset_token(self, customer: Customer, db: Session):
        """
        Clear password reset token after successful reset.
        
        Args:
            customer: Customer to clear token for
            db: Database session
        """
        customer.password_reset_token = None
        customer.password_reset_token_expires = None
        db.commit()
        logger.info(f"Password reset token cleared for customer {customer.id}")
    
    async def send_reset_email(self, customer: Customer, base_url: str = "http://localhost:3000") -> bool:
        """
        Send password reset email to customer.
        
        Args:
            customer: Customer to send email to
            base_url: Base URL for reset link
            
        Returns:
            True if email was sent successfully
        """
        if not customer.password_reset_token:
            logger.error(f"No password reset token for customer {customer.id}")
            return False
        
        reset_link = f"{base_url}/reset-password?token={customer.password_reset_token}"
        
        subject = "Wachtwoord resetten - Pita Pizza Napoli"
        
        # Plain text version
        body = f"""
Beste {customer.naam or 'klant'},

Je hebt een verzoek gedaan om je wachtwoord te resetten voor je account bij Pita Pizza Napoli.

Klik op de onderstaande link om een nieuw wachtwoord in te stellen:

{reset_link}

Deze link is 1 uur geldig.

Als je dit verzoek niet hebt gedaan, negeer dan deze e-mail. Je wachtwoord blijft ongewijzigd.

Voor je veiligheid:
- Gebruik een sterk wachtwoord met minimaal 8 tekens
- Gebruik hoofdletters, kleine letters, cijfers en speciale tekens
- Deel je wachtwoord nooit met anderen

Met vriendelijke groet,
Pita Pizza Napoli
Brugstraat 12, 9120 Vrasene
Tel: 03 775 72 28
www.pitapizzanapoli.be
        """
        
        # HTML version
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #ad2929; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #ad2929; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
        .warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Pita Pizza Napoli</h1>
            <p>Wachtwoord Resetten</p>
        </div>
        <div class="content">
            <p>Beste {customer.naam or 'klant'},</p>
            <p>Je hebt een verzoek gedaan om je wachtwoord te resetten voor je account bij Pita Pizza Napoli.</p>
            <p>Klik op de onderstaande knop om een nieuw wachtwoord in te stellen:</p>
            <p style="text-align: center;">
                <a href="{reset_link}" class="button">Wachtwoord Resetten</a>
            </p>
            <p>Of kopieer en plak deze link in je browser:</p>
            <p style="word-break: break-all; color: #666;">{reset_link}</p>
            <p><small>Deze link is 1 uur geldig.</small></p>
            <div class="warning">
                <strong>⚠️ Belangrijk:</strong> Als je dit verzoek niet hebt gedaan, negeer dan deze e-mail. Je wachtwoord blijft ongewijzigd.
            </div>
            <h3>Wachtwoord vereisten:</h3>
            <ul>
                <li>Minimaal 8 tekens</li>
                <li>Minimaal één hoofdletter</li>
                <li>Minimaal één kleine letter</li>
                <li>Minimaal één cijfer</li>
                <li>Minimaal één speciaal teken (!@#$%^&*()_+-=[]{{}}|;:,.<>?)</li>
            </ul>
        </div>
        <div class="footer">
            <p><strong>Pita Pizza Napoli</strong><br>
            Brugstraat 12, 9120 Vrasene<br>
            Tel: 03 775 72 28<br>
            www.pitapizzanapoli.be</p>
        </div>
    </div>
</body>
</html>
        """
        
        try:
            success = await email_service.send_email(
                to_email=customer.email,
                subject=subject,
                body=body,
                html_body=html_body
            )
            
            if success:
                logger.info(f"Password reset email sent to {customer.email}")
            else:
                logger.warning(f"Failed to send password reset email to {customer.email}")
            
            return success
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            return False


# Global password reset service instance
password_reset_service = PasswordResetService()


