"""
Contact form API endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ContactRequest(BaseModel):
    """Contact form request model."""
    naam: str
    email: str
    telefoon: Optional[str] = None
    bericht: str


@router.post("/contact")
async def submit_contact_form(request: ContactRequest):
    """
    Submit contact form.
    
    This endpoint receives contact form submissions.
    In production, you would typically:
    - Send an email to the restaurant
    - Store the message in a database
    - Send a confirmation email to the customer
    """
    try:
        # Log the contact form submission
        logger.info(f"Contact form submission from {request.email}: {request.naam}")
        logger.info(f"Message: {request.bericht}")
        
        # TODO: Implement email sending
        # TODO: Store in database if needed
        # TODO: Send confirmation email to customer
        
        return {
            "message": "Bedankt voor je bericht! We nemen zo spoedig mogelijk contact met je op.",
            "success": True
        }
    except Exception as e:
        logger.error(f"Error processing contact form: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Er is een fout opgetreden. Probeer het later opnieuw."
        )

