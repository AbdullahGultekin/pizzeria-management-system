"""
Email service for sending emails via SMTP.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        # SMTP configuration from environment variables
        self.smtp_host = settings.SMTP_HOST if hasattr(settings, 'SMTP_HOST') else None
        self.smtp_port = settings.SMTP_PORT if hasattr(settings, 'SMTP_PORT') else 587
        self.smtp_user = settings.SMTP_USER if hasattr(settings, 'SMTP_USER') else None
        self.smtp_password = settings.SMTP_PASSWORD if hasattr(settings, 'SMTP_PASSWORD') else None
        self.smtp_from_email = settings.SMTP_FROM_EMAIL if hasattr(settings, 'SMTP_FROM_EMAIL') else None
        self.smtp_use_tls = settings.SMTP_USE_TLS if hasattr(settings, 'SMTP_USE_TLS') else True
        
        # Check if email is configured
        self.enabled = bool(self.smtp_host and self.smtp_user and self.smtp_password and self.smtp_from_email)
        
        if not self.enabled:
            logger.warning("Email service is not configured. Emails will be logged but not sent.")
            logger.warning("Set SMTP_HOST, SMTP_USER, SMTP_PASSWORD, and SMTP_FROM_EMAIL environment variables to enable email sending.")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send an email via SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.enabled:
            # Log the email instead of sending
            logger.info(f"Email would be sent to: {to_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body:\n{body}")
            if html_body:
                logger.info(f"HTML Body:\n{html_body}")
            return True
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_from_email
            msg['To'] = to_email
            
            # Add plain text part
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Send email via SMTP
            # Try SMTP_SSL first if port is 465, otherwise use regular SMTP with TLS
            if self.smtp_port == 465:
                # Port 465 requires SSL from the start
                import ssl
                # Create SSL context that doesn't verify certificate (for development)
                # In production, you should use proper certificate verification
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=60, context=context) as server:
                    # Enable debug output in development
                    if hasattr(settings, 'DEBUG') and settings.DEBUG:
                        server.set_debuglevel(1)
                    
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
            else:
                # Port 587 or 25 uses STARTTLS
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=60) as server:
                    # Enable debug output in development
                    if hasattr(settings, 'DEBUG') and settings.DEBUG:
                        server.set_debuglevel(1)
                    
                    if self.smtp_use_tls:
                        server.starttls()
                    
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error sending email to {to_email}: {e}"
            logger.error(error_msg)
            logger.error(f"SMTP Host: {self.smtp_host}, Port: {self.smtp_port}")
            print(f"ERROR: {error_msg}")
            return False
        except OSError as e:
            error_msg = f"Network/DNS error sending email to {to_email}: {e}"
            logger.error(error_msg)
            logger.error(f"SMTP Host: {self.smtp_host}, Port: {self.smtp_port}")
            logger.error("Controleer of de SMTP hostnaam correct is en of je internetverbinding werkt.")
            print(f"ERROR: {error_msg}")
            print(f"Controleer of '{self.smtp_host}' de juiste SMTP hostnaam is voor one.com")
            return False
        except Exception as e:
            error_msg = f"Error sending email to {to_email}: {e}"
            logger.error(error_msg)
            logger.exception("Full error traceback:")
            print(f"ERROR: {error_msg}")
            return False
    
    async def send_verification_email(
        self,
        to_email: str,
        customer_name: str,
        verification_link: str,
        order_bonnummer: Optional[str] = None
    ) -> bool:
        """
        Send email verification email.
        
        Args:
            to_email: Customer email address
            customer_name: Customer name
            verification_link: Email verification link
            
        Returns:
            True if email was sent successfully
        """
        subject = "Verifieer je e-mailadres - Pita Pizza Napoli"
        
        # Add order tracking info if available
        order_info_text = ""
        if order_bonnummer:
            order_info_text = f"""

📦 BELANGRIJK: Je bestelnummer is {order_bonnummer}
Je kunt je bestelling volgen met dit nummer en je telefoonnummer, ook als je e-mailadres niet geverifieerd is.
"""
        
        # Plain text version
        body = f"""
Beste {customer_name or 'klant'},

Bedankt voor je registratie bij Pita Pizza Napoli!
{order_info_text}
Klik op de onderstaande link om je e-mailadres te verifiëren:

{verification_link}

Deze link is 24 uur geldig.

Waarom verificatie belangrijk is:
- Je kunt je bestellingen volgen via je account
- Je ontvangt updates over je bestelling
- Je gegevens worden automatisch ingevuld bij volgende bestellingen

Als je deze link niet hebt aangevraagd, negeer dan deze e-mail.

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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Pita Pizza Napoli</h1>
        </div>
        <div class="content">
            <p>Beste {customer_name or 'klant'},</p>
            <p>Bedankt voor je registratie bij Pita Pizza Napoli!</p>
            <p>Klik op de onderstaande knop om je e-mailadres te verifiëren:</p>
            <p style="text-align: center;">
                <a href="{verification_link}" class="button">E-mailadres verifiëren</a>
            </p>
            <p>Of kopieer en plak deze link in je browser:</p>
            <p style="word-break: break-all; color: #666;">{verification_link}</p>
            <p><small>Deze link is 24 uur geldig.</small></p>
            <p>Als je deze link niet hebt aangevraagd, negeer dan deze e-mail.</p>
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
        
        return await self.send_email(to_email, subject, body, html_body)


# Global email service instance
email_service = EmailService()

