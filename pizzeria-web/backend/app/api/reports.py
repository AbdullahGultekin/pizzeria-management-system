"""
Reports API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.order import Order, OrderItem
from app.models.customer import Customer
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/reports/daily")
async def get_daily_report(
    request: Request,
    report_date: str = None,  # Format: YYYY-MM-DD
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    """
    Get daily sales report.
    """
    if not report_date:
        report_date = date.today().isoformat()
    
    try:
        report_dt = datetime.fromisoformat(report_date).date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ongeldig datum formaat. Gebruik YYYY-MM-DD"
        )
    
    # Get orders for the day
    orders = db.query(Order).filter(
        func.date(Order.datum) == report_dt
    ).all()
    
    total_revenue = sum(order.totaal for order in orders)
    total_orders = len(orders)
    
    # Get order items for product statistics
    order_ids = [order.id for order in orders]
    items = db.query(OrderItem).filter(OrderItem.bestelling_id.in_(order_ids)).all()
    
    # Product statistics
    product_stats: Dict[str, Dict[str, Any]] = {}
    for item in items:
        if item.product_naam not in product_stats:
            product_stats[item.product_naam] = {
                "naam": item.product_naam,
                "aantal": 0,
                "omzet": 0.0
            }
        product_stats[item.product_naam]["aantal"] += item.aantal
        product_stats[item.product_naam]["omzet"] += item.prijs * item.aantal
    
    # Hourly breakdown
    hourly_stats: Dict[int, Dict[str, Any]] = {}
    for order in orders:
        hour = order.tijd.hour if order.tijd else 0
        if hour not in hourly_stats:
            hourly_stats[hour] = {"orders": 0, "revenue": 0.0}
        hourly_stats[hour]["orders"] += 1
        hourly_stats[hour]["revenue"] += order.totaal
    
    return {
        "date": report_date,
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "average_order_value": float(total_revenue / total_orders) if total_orders > 0 else 0.0,
        "product_stats": list(product_stats.values()),
        "hourly_stats": [
            {
                "hour": hour,
                "orders": stats["orders"],
                "revenue": float(stats["revenue"])
            }
            for hour, stats in sorted(hourly_stats.items())
        ]
    }


@router.get("/reports/monthly")
async def get_monthly_report(
    request: Request,
    year: int = None,
    month: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    """
    Get monthly sales report.
    """
    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month
    
    # Get orders for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    orders = db.query(Order).filter(
        and_(
            func.date(Order.datum) >= start_date,
            func.date(Order.datum) <= end_date
        )
    ).all()
    
    total_revenue = sum(order.totaal for order in orders)
    total_orders = len(orders)
    
    # Daily breakdown
    daily_stats: Dict[str, Dict[str, Any]] = {}
    for order in orders:
        # Extract date from datetime
        if isinstance(order.datum, date):
            order_date_str = str(order.datum)
        else:
            # If it's a datetime, extract just the date part
            order_date_str = str(order.datum.date()) if hasattr(order.datum, 'date') else str(order.datum)
        
        if order_date_str not in daily_stats:
            daily_stats[order_date_str] = {"orders": 0, "revenue": 0.0}
        daily_stats[order_date_str]["orders"] += 1
        daily_stats[order_date_str]["revenue"] += order.totaal
    
    return {
        "year": year,
        "month": month,
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "average_order_value": float(total_revenue / total_orders) if total_orders > 0 else 0.0,
        "daily_stats": [
            {
                "date": day,
                "orders": stats["orders"],
                "revenue": float(stats["revenue"])
            }
            for day, stats in sorted(daily_stats.items())
        ]
    }


@router.get("/reports/z-report")
async def get_z_report(
    request: Request,
    report_date: str = None,  # Format: YYYY-MM-DD
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    """
    Generate Z-report (daily closing report).
    """
    if not report_date:
        report_date = date.today().isoformat()
    
    try:
        report_dt = datetime.fromisoformat(report_date).date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ongeldig datum formaat. Gebruik YYYY-MM-DD"
        )
    
    # Get orders for the day
    orders = db.query(Order).filter(
        func.date(Order.datum) == report_dt
    ).all()
    
    total_revenue = sum(order.totaal for order in orders)
    total_orders = len(orders)
    
    # Get order items
    order_ids = [order.id for order in orders]
    items = db.query(OrderItem).filter(OrderItem.bestelling_id.in_(order_ids)).all()
    
    # Hourly breakdown
    hourly_stats: Dict[int, Dict[str, Any]] = {}
    for order in orders:
        hour = order.tijd.hour if order.tijd else 0
        if hour not in hourly_stats:
            hourly_stats[hour] = {"orders": 0, "revenue": 0.0}
        hourly_stats[hour]["orders"] += 1
        hourly_stats[hour]["revenue"] += order.totaal
    
    # Courier breakdown (if koerier_id exists)
    courier_stats: Dict[int, Dict[str, Any]] = {}
    for order in orders:
        if order.koerier_id:
            if order.koerier_id not in courier_stats:
                courier_stats[order.koerier_id] = {"orders": 0, "revenue": 0.0}
            courier_stats[order.koerier_id]["orders"] += 1
            courier_stats[order.koerier_id]["revenue"] += order.totaal
    
    return {
        "date": report_date,
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "average_order_value": float(total_revenue / total_orders) if total_orders > 0 else 0.0,
        "hourly_breakdown": [
            {
                "hour": hour,
                "orders": stats["orders"],
                "revenue": float(stats["revenue"])
            }
            for hour, stats in sorted(hourly_stats.items())
        ],
        "courier_breakdown": [
            {
                "koerier_id": koerier_id,
                "orders": stats["orders"],
                "revenue": float(stats["revenue"])
            }
            for koerier_id, stats in sorted(courier_stats.items())
        ]
    }

