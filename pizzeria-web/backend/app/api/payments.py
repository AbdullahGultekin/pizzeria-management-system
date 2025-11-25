"""
Stripe payment integration endpoints.

Initial minimal integration:
- Create PaymentIntent for an order
- Webhook endpoint to receive payment status updates

All keys are read from environment variables via Settings:
- STRIPE_SECRET_KEY
- STRIPE_WEBHOOK_SECRET
"""

from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel, Field, condecimal
from typing import Optional
import stripe

from app.core.config import settings
from app.core.database import get_db
from app.models import order as order_models  # for future use

router = APIRouter()


class CreatePaymentRequest(BaseModel):
    order_id: int = Field(..., description="ID van de bestelling")
    amount: condecimal(max_digits=10, decimal_places=2) = Field(
        ..., description="Bedrag in EUR, bijvoorbeeld 25.00"
    )


class CreatePaymentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str


def _ensure_stripe_config():
    """Ensure Stripe is configured, otherwise raise a clear error."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe is niet geconfigureerd. STRIPE_SECRET_KEY ontbreekt.",
        )
    stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/payments/create", response_model=CreatePaymentResponse)
async def create_payment(payload: CreatePaymentRequest):
    """
    Maak een Stripe PaymentIntent voor een bestelling.

    Frontend gebruikt `client_secret` om de betaling af te ronden.
    """
    _ensure_stripe_config()

    try:
        amount_cents = int(payload.amount * 100)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ongeldig bedrag",
        )

    if amount_cents <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bedrag moet groter dan 0 zijn.",
        )

    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="eur",
            payment_method_types=["card", "bancontact", "ideal"],
            metadata={"order_id": str(payload.order_id)},
        )
    except stripe.error.StripeError as e:
        # Stripe-specifieke fout
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe fout: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kon betaling niet aanmaken: {str(e)}",
        )

    return CreatePaymentResponse(
        client_secret=payment_intent.client_secret,
        payment_intent_id=payment_intent.id,
    )


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """
    Stripe webhook endpoint.

    Voor nu: alleen basisvalidatie en logging.
    Later kunnen we hier orderstatus bijwerken in de database.
    """
    _ensure_stripe_config()

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not settings.STRIPE_WEBHOOK_SECRET:
        # Zonder webhook secret kunnen we het event niet verifiëren
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe webhook secret ontbreekt (STRIPE_WEBHOOK_SECRET).",
        )

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ongeldige Stripe webhook signature.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ongeldige webhook payload.",
        )

    # Basisafhandeling: in de toekomst orderstatus updaten
    event_type = event.get("type")
    data_object = event.get("data", {}).get("object", {})

    if event_type == "payment_intent.succeeded":
        # Voorbeeld: order_id uit metadata halen
        order_id = data_object.get("metadata", {}).get("order_id")
        # TODO: bestelling in DB markeren als betaald
        # met behulp van order_id

    # Stripe verwacht altijd een 2xx response
    return {"status": "ok"}


