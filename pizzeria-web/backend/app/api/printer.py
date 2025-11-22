"""
API endpoints for printer management and print jobs.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
import logging
import json

from app.core.dependencies import get_db, get_current_user, require_role
from app.services.printer import printer_service
from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.customer import Customer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/printer", tags=["printer"])


class PrintJobRequest(BaseModel):
    """Request model for print job."""
    order_id: int
    custom_footer: Optional[str] = None


class PrintJobResponse(BaseModel):
    """Response model for print job."""
    job_id: str
    status: str
    message: str


class PrinterInfoResponse(BaseModel):
    """Response model for printer information."""
    available_printers: List[str]
    current_printer: Optional[str]
    direct_print_enabled: bool
    pending_jobs: int


@router.get("/info", response_model=PrinterInfoResponse)
async def get_printer_info(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get printer information and status."""
    available_printers = printer_service.get_available_printers()
    pending_jobs = len(printer_service.get_pending_jobs())
    
    return {
        "available_printers": available_printers,
        "current_printer": printer_service.printer_name,
        "direct_print_enabled": printer_service.direct_print_enabled,
        "pending_jobs": pending_jobs
    }


@router.post("/print", response_model=PrintJobResponse)
async def print_order(
    request: PrintJobRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Print receipt for an order.
    
    Requires admin or kassa role.
    """
    # Get order
    order = db.query(Order).filter(Order.id == request.order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Get customer if available
    customer_data = None
    if order.klant_id:
        customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
        if customer:
            customer_data = {
                "naam": customer.naam,
                "telefoon": customer.telefoon,
                "straat": getattr(customer, 'straat', None),
                "huisnummer": getattr(customer, 'huisnummer', None),
                "postcode": getattr(customer, 'postcode', None),
                "plaats": getattr(customer, 'plaats', None),
            }
    
    # Prepare order data
    order_data = {
        "id": order.id,
        "bonnummer": order.bonnummer,
        "datum": order.datum,
        "tijd": order.tijd,
        "totaal": order.totaal,
        "items": [
            {
                "product_naam": item.product_naam,
                "aantal": item.aantal,
                "prijs": item.prijs,
                "opmerking": getattr(item, 'opmerking', None),
                "extras": json.loads(item.extras) if getattr(item, 'extras', None) else None,
            }
            for item in order.items
        ]
    }
    
    # Format receipt
    receipt_text = printer_service.format_receipt(
        order_data,
        customer_data,
        request.custom_footer
    )
    
    # Generate QR data (optional)
    qr_data = f"https://pitapizzanapoli.be/status?bonnummer={order.bonnummer}"
    
    # Queue print job
    job_id = printer_service.queue_print_job(order_data, receipt_text, qr_data)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Print job queued successfully"
    }


@router.get("/jobs/pending")
async def get_pending_jobs(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all pending print jobs (admin only)."""
    # Check if user is admin
    if not current_user or current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    jobs = printer_service.get_pending_jobs()
    return {"jobs": jobs, "count": len(jobs)}


@router.post("/jobs/{job_id}/complete")
async def complete_print_job(
    job_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a print job as completed (admin only)."""
    # Check if user is admin
    if not current_user or current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    success = printer_service.mark_job_printed(job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Print job not found"
        )
    return {"message": "Print job marked as completed"}


class PrinterConfigRequest(BaseModel):
    """Request model for printer configuration."""
    printer_name: str


@router.post("/configure")
async def configure_printer(
    request: PrinterConfigRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Configure printer name (admin only)."""
    available_printers = printer_service.get_available_printers()
    if request.printer_name not in available_printers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Printer '{request.printer_name}' not found. Available printers: {', '.join(available_printers)}"
        )
    
    printer_service.set_printer_name(request.printer_name)
    return {"message": f"Printer configured: {request.printer_name}"}

