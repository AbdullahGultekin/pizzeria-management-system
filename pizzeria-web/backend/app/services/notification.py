"""
Notification service for sending order confirmations via email/SMS.
"""
import logging
import os
import base64
from typing import Optional, Dict, Any
from datetime import datetime
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications."""
    
    def __init__(self):
        # Check email service status dynamically (it may change)
        self.sms_enabled = False  # Set to True when SMS is configured
    
    @property
    def email_enabled(self):
        """Check if email service is enabled (dynamic check)."""
        return email_service.enabled
    
    async def send_order_confirmation(
        self,
        order_data: Dict[str, Any],
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None
    ) -> bool:
        """
        Send order confirmation to customer.
        
        Args:
            order_data: Order information
            customer_email: Customer email address (optional)
            customer_phone: Customer phone number (optional)
            
        Returns:
            True if notification was sent successfully
        """
        try:
            bonnummer = order_data.get('bonnummer', 'N/A')
            logger.info(f"Order confirmation notification for order {bonnummer}")
            logger.info(f"Customer email: {customer_email or 'NOT PROVIDED'}")
            logger.info(f"Customer phone: {customer_phone or 'NOT PROVIDED'}")
            logger.info(f"Email service enabled: {self.email_enabled}")
            
            # Send email if customer has email and email service is enabled
            if customer_email:
                if self.email_enabled:
                    try:
                        # Format email content
                        email_content = self.format_order_email(order_data)
                        html_content, logo_path = self.format_order_email_html(order_data)
                        
                        success = await email_service.send_email(
                            to_email=customer_email,
                            subject=f"Bestelling Bevestiging - Bonnummer {bonnummer} - Pita Pizza Napoli",
                            body=email_content,
                            html_body=html_content,
                            logo_path=logo_path
                        )
                        
                        if success:
                            logger.info(f"Order confirmation email sent to {customer_email} for order {bonnummer}")
                        else:
                            logger.warning(f"Failed to send order confirmation email to {customer_email}")
                        
                        return success
                    except Exception as e:
                        logger.error(f"Error sending order confirmation email: {e}")
                        logger.exception("Full error traceback:")
                        return False
                else:
                    logger.warning(f"Email service not enabled - cannot send confirmation to {customer_email}")
                    logger.warning(f"SMTP configuration check: host={email_service.smtp_host}, user={email_service.smtp_user}, enabled={email_service.enabled}")
            else:
                logger.warning(f"No customer email provided for order {bonnummer} - skipping email confirmation")
                logger.warning(f"This means the customer was created/updated without an email address")
            
            # TODO: Implement SMS sending if customer_phone and self.sms_enabled
            
            return True
        except Exception as e:
            logger.error(f"Error sending order confirmation: {e}")
            logger.exception("Full error traceback:")
            return False
    
    async def send_admin_notification(
        self,
        order_data: Dict[str, Any]
    ) -> bool:
        """
        Send notification to admin about new order.
        
        Args:
            order_data: Order information
            
        Returns:
            True if notification was sent successfully
        """
        try:
            logger.info(f"Admin notification for new order {order_data.get('bonnummer')}")
            
            # TODO: Implement actual notification (email, push, etc.)
            # This could send an email to admin or trigger a push notification
            
            return True
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
            return False
    
    async def send_status_update(
        self,
        order_data: Dict[str, Any],
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None
    ) -> bool:
        """
        Send status update notification to customer.
        
        Args:
            order_data: Order information with updated status
            customer_email: Customer email address (optional)
            customer_phone: Customer phone number (optional)
            
        Returns:
            True if notification was sent successfully
        """
        try:
            status = order_data.get('status', 'Unknown')
            bonnummer = order_data.get('bonnummer', 'Unknown')
            
            logger.info(f"Status update notification: Order {bonnummer} -> {status}")
            logger.info(f"Customer: {customer_email or customer_phone or 'No contact info'}")
            
            # TODO: Implement actual notification sending
            
            return True
        except Exception as e:
            logger.error(f"Error sending status update: {e}")
            return False
    
    def format_order_email(self, order_data: Dict[str, Any]) -> str:
        """
        Format order confirmation email content (plain text).
        
        Args:
            order_data: Order information
            
        Returns:
            Formatted email text
        """
        bonnummer = order_data.get('bonnummer', 'N/A')
        totaal = order_data.get('totaal', 0)
        status = order_data.get('status', 'Nieuw')
        datum = order_data.get('datum', '')
        tijd = order_data.get('tijd', '')
        items = order_data.get('items', [])
        
        email_content = f"""Beste klant,

Bedankt voor uw bestelling bij Pita Pizza Napoli!

📦 BONNUMMER: {bonnummer}
📅 Datum: {datum} {tijd}
📊 Status: {status}

Bestelde items:
"""
        
        for item in items:
            aantal = item.get('aantal', 1)
            prijs = item.get('prijs', 0)
            totaal_item = prijs * aantal
            product_naam = item.get('product_naam', 'N/A')
            extras = item.get('extras')
            
            email_content += f"  • {aantal}x {product_naam} - €{totaal_item:.2f}\n"
            
            # Add extras details
            if extras:
                if isinstance(extras, str):
                    import json
                    try:
                        extras = json.loads(extras)
                    except:
                        extras = None
                
                if extras and isinstance(extras, dict):
                    details = []
                    if extras.get('vlees'):
                        details.append(f"    Vlees: {extras['vlees']}")
                    if extras.get('bijgerecht'):
                        bijgerecht = extras['bijgerecht']
                        if isinstance(bijgerecht, list):
                            details.append(f"    Bijgerecht: {', '.join(bijgerecht)}")
                        else:
                            details.append(f"    Bijgerecht: {bijgerecht}")
                    if extras.get('sauzen'):
                        sauzen = extras['sauzen']
                        if isinstance(sauzen, list):
                            details.append(f"    Sauzen: {', '.join(sauzen)}")
                        else:
                            details.append(f"    Sauzen: {sauzen}")
                    if extras.get('saus1'):
                        details.append(f"    Saus 1: {extras['saus1']}")
                    if extras.get('saus2'):
                        details.append(f"    Saus 2: {extras['saus2']}")
                    if extras.get('garnering'):
                        garnering = extras['garnering']
                        if isinstance(garnering, list):
                            details.append(f"    Extra: {', '.join(garnering)}")
                        else:
                            details.append(f"    Extra: {garnering}")
                    if extras.get('half_half'):
                        half_half = extras['half_half']
                        if isinstance(half_half, list) and len(half_half) == 2:
                            details.append(f"    Half-half: {half_half[0]} / {half_half[1]}")
                    if extras.get('opmerking'):
                        details.append(f"    Opmerking: {extras['opmerking']}")
                    
                    for detail in details:
                        email_content += f"    {detail}\n"
        
        email_content += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAAL: €{totaal:.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

U kunt de status van uw bestelling volgen met uw bonnummer en telefoonnummer.

Met vriendelijke groet,
Pita Pizza Napoli
Brugstraat 12, 9120 Vrasene
Tel: 03 775 72 28
www.pitapizzanapoli.be
"""
        
        return email_content
    
    def format_order_email_html(self, order_data: Dict[str, Any]) -> tuple[str, Optional[str]]:
        """
        Format order confirmation email content (HTML).
        
        Args:
            order_data: Order information
            
        Returns:
            Tuple of (formatted email HTML, logo_path for CID attachment)
        """
        bonnummer = order_data.get('bonnummer', 'N/A')
        totaal = order_data.get('totaal', 0)
        status = order_data.get('status', 'Nieuw')
        datum = order_data.get('datum', '')
        tijd = order_data.get('tijd', '')
        items = order_data.get('items', [])
        
        # Find logo file path for CID attachment
        logo_path = None
        logo_url = "cid:logo"  # Use CID by default
        
        try:
            # Get the directory where this file is located (app/services/)
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to backend directory
            backend_dir = os.path.dirname(os.path.dirname(current_file_dir))
            # Try relative path from backend to frontend/public
            logo_paths = [
                os.path.join(backend_dir, "..", "frontend", "public", "LOGO-MAGNEET.jpg"),  # From backend: ../frontend/public/
                os.path.join(backend_dir, "pizzeria-web", "frontend", "public", "LOGO-MAGNEET.jpg"),  # Alternative structure
                os.path.join(os.path.dirname(backend_dir), "pizzeria-web", "frontend", "public", "LOGO-MAGNEET.jpg"),
                os.path.join(backend_dir, "frontend", "public", "LOGO-MAGNEET.jpg"),
                "LOGO-MAGNEET.jpg",  # Try current directory
            ]
            
            for path in logo_paths:
                abs_path = os.path.abspath(path)
                if os.path.exists(abs_path):
                    logo_path = abs_path
                    break
            
            if logo_path and os.path.exists(logo_path):
                logger.info(f"Logo found at {logo_path}, will be attached as CID")
            else:
                # Fallback to URL if logo file not found
                from app.core.config import settings
                base_url = getattr(settings, 'FRONTEND_URL', 'https://www.pitapizzanapoli.be')
                if not base_url or base_url == 'http://localhost:3000':
                    base_url = 'https://www.pitapizzanapoli.be'
                logo_url = f"{base_url}/LOGO-MAGNEET.jpg"
                logo_path = None  # No local file, use URL
                logger.warning(f"Logo file not found in any of these paths: {logo_paths}, using URL: {logo_url}")
        except Exception as e:
            logger.error(f"Error finding logo: {e}")
            logger.exception("Full error traceback:")
            # Fallback to URL
            from app.core.config import settings
            base_url = getattr(settings, 'FRONTEND_URL', 'https://www.pitapizzanapoli.be')
            if not base_url or base_url == 'http://localhost:3000':
                base_url = 'https://www.pitapizzanapoli.be'
            logo_url = f"{base_url}/LOGO-MAGNEET.jpg"
            logo_path = None
        
        items_html = ""
        for item in items:
            aantal = item.get('aantal', 1)
            prijs = item.get('prijs', 0)
            totaal_item = prijs * aantal
            product_naam = item.get('product_naam', 'N/A')
            extras = item.get('extras')
            
            # Parse extras if it's a string
            if extras and isinstance(extras, str):
                import json
                try:
                    extras = json.loads(extras)
                except:
                    extras = None
            
            # Build extras details HTML
            extras_html = ""
            if extras and isinstance(extras, dict):
                details = []
                if extras.get('vlees'):
                    details.append(f"<li><strong>Vlees:</strong> {extras['vlees']}</li>")
                if extras.get('bijgerecht'):
                    bijgerecht = extras['bijgerecht']
                    if isinstance(bijgerecht, list):
                        details.append(f"<li><strong>Bijgerecht:</strong> {', '.join(bijgerecht)}</li>")
                    else:
                        details.append(f"<li><strong>Bijgerecht:</strong> {bijgerecht}</li>")
                if extras.get('sauzen'):
                    sauzen = extras['sauzen']
                    if isinstance(sauzen, list):
                        details.append(f"<li><strong>Sauzen:</strong> {', '.join(sauzen)}</li>")
                    else:
                        details.append(f"<li><strong>Sauzen:</strong> {sauzen}</li>")
                if extras.get('saus1'):
                    details.append(f"<li><strong>Saus 1:</strong> {extras['saus1']}</li>")
                if extras.get('saus2'):
                    details.append(f"<li><strong>Saus 2:</strong> {extras['saus2']}</li>")
                if extras.get('garnering'):
                    garnering = extras['garnering']
                    if isinstance(garnering, list):
                        details.append(f"<li><strong>Extra:</strong> {', '.join(garnering)}</li>")
                    else:
                        details.append(f"<li><strong>Extra:</strong> {garnering}</li>")
                if extras.get('half_half'):
                    half_half = extras['half_half']
                    if isinstance(half_half, list) and len(half_half) == 2:
                        details.append(f"<li><strong>Half-half:</strong> {half_half[0]} / {half_half[1]}</li>")
                if extras.get('opmerking'):
                    details.append(f"<li><strong>Opmerking:</strong> {extras['opmerking']}</li>")
                
                if details:
                    extras_html = f"""
                    <div style="margin-top: 5px; font-size: 0.9em; color: #666;">
                        <ul style="margin: 0; padding-left: 20px;">
                            {''.join(details)}
                        </ul>
                    </div>
                    """
            
            # Build the row with product info
            items_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee; vertical-align: top;">{aantal}x</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; vertical-align: top;">
                    <strong>{product_naam}</strong>
                    {extras_html}
                </td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right; vertical-align: top;">€{totaal_item:.2f}</td>
            </tr>
            """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 0; }}
        .header {{ background-color: #ad2929; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .header img {{ max-width: 120px; height: auto; margin-bottom: 10px; display: block; margin-left: auto; margin-right: auto; }}
        .header h1 {{ margin: 0; font-size: 1.5em; display: none; }}
        .header p {{ margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.9; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .order-info {{ background-color: white; padding: 15px; margin: 15px 0; border-radius: 5px; }}
        .items-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; background-color: white; }}
        .items-table th {{ background-color: #f0f0f0; padding: 10px 8px; text-align: left; font-weight: 600; }}
        .total {{ font-size: 1.2em; font-weight: bold; color: #ad2929; text-align: right; padding: 10px; background-color: #fff; border-top: 2px solid #ad2929; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{logo_url}" alt="Pita Pizza Napoli Logo" width="120" height="120" style="max-width: 120px; height: auto; display: block; margin: 0 auto 10px auto; border-radius: 50%; border: 3px solid white; object-fit: cover;" />
            <p>Bestelling Bevestiging</p>
        </div>
        <div class="content">
            <p>Beste klant,</p>
            <p>Bedankt voor uw bestelling bij Pita Pizza Napoli!</p>
            
            <div class="order-info">
                <p><strong>📦 Bonnummer:</strong> {bonnummer}</p>
                <p><strong>📅 Datum:</strong> {datum} {tijd}</p>
                <p><strong>📊 Status:</strong> {status}</p>
            </div>
            
            <h3>Bestelde items:</h3>
            <table class="items-table">
                <thead>
                    <tr>
                        <th style="width: 15%;">Aantal</th>
                        <th style="width: 50%;">Product</th>
                        <th style="width: 35%; text-align: right;">Prijs</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
                <tfoot>
                    <tr>
                        <td colspan="3" class="total">TOTAAL: €{totaal:.2f}</td>
                    </tr>
                </tfoot>
            </table>
            
            <p>U kunt de status van uw bestelling volgen met uw bonnummer en telefoonnummer.</p>
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
        
        # Return HTML and logo path for CID attachment
        return html_content, logo_path if 'logo_path' in locals() and logo_path else None


# Global notification service instance
notification_service = NotificationService()


