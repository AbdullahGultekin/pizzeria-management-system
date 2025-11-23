"""
Order API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.order import Order, OrderItem
from app.models.customer import Customer
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderItemResponse, OrderStatusUpdate
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def generate_bonnummer(db: Session) -> str:
    """
    Generate receipt number in format YYYYNNNN.
    
    Args:
        db: Database session
        
    Returns:
        Receipt number string
    """
    now = datetime.now()
    jaar = now.year
    dag = now.timetuple().tm_yday  # Day of year (1-365/366)
    
    # Get or create bon_teller entry
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT laatste_nummer FROM bon_teller 
        WHERE jaar = :jaar AND dag = :dag
    """), {"jaar": jaar, "dag": dag})
    
    row = result.fetchone()
    if row:
        laatste_nummer = row[0] + 1
        db.execute(text("""
            UPDATE bon_teller 
            SET laatste_nummer = :num 
            WHERE jaar = :jaar AND dag = :dag
        """), {"num": laatste_nummer, "jaar": jaar, "dag": dag})
    else:
        laatste_nummer = 1
        db.execute(text("""
            INSERT INTO bon_teller (jaar, dag, laatste_nummer) 
            VALUES (:jaar, :dag, 1)
        """), {"jaar": jaar, "dag": dag})
    
    db.commit()
    
    # Format: YYYYNNNN (e.g., 20240001)
    bonnummer = f"{jaar}{laatste_nummer:04d}"
    return bonnummer


@router.get("/orders/public/{bonnummer}")
async def get_order_by_bonnummer_public(
    bonnummer: str,
    db: Session = Depends(get_db)
):
    """
    Get order by bonnummer (public endpoint, no authentication required).
    """
    order = db.query(Order).filter(Order.bonnummer == bonnummer).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestelling niet gevonden"
        )
    
    # Get customer name if klant_id exists
    klant_naam = None
    if order.klant_id:
        customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
        if customer:
            klant_naam = customer.naam
    
    return {
        "id": order.id,
        "klant_id": order.klant_id,
        "klant_naam": klant_naam,
        "koerier_id": order.koerier_id,
        "datum": order.datum,
        "tijd": order.tijd,
        "totaal": order.totaal,
        "opmerking": order.opmerking,
        "bonnummer": order.bonnummer,
        "levertijd": order.levertijd,
        "status": order.status or "Nieuw",
        "items": [
            {
                "id": item.id,
                "bestelling_id": item.bestelling_id,
                "product_naam": item.product_naam,
                "aantal": item.aantal,
                "prijs": item.prijs,
                "opmerking": item.opmerking,
                "extras": json.loads(item.extras) if item.extras else None
            }
            for item in order.items
        ]
    }


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of orders with optional filtering.
    """
    query = db.query(Order)
    
    if customer_id:
        query = query.filter(Order.klant_id == customer_id)
    
    orders = query.order_by(Order.datum.desc(), Order.tijd.desc()).offset(skip).limit(limit).all()
    
    # Load items for each order
    result = []
    for order in orders:
        # Get customer name if klant_id exists
        klant_naam = None
        if order.klant_id:
            customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
            if customer:
                klant_naam = customer.naam
        
        order_dict = {
            "id": order.id,
            "klant_id": order.klant_id,
            "klant_naam": klant_naam,
            "koerier_id": order.koerier_id,
            "datum": order.datum,
            "tijd": order.tijd,
            "totaal": order.totaal,
            "opmerking": order.opmerking,
            "bonnummer": order.bonnummer,
            "levertijd": order.levertijd,
            "status": order.status or "Nieuw",
            "items": [
                {
                    "id": item.id,
                    "bestelling_id": item.bestelling_id,
                    "product_naam": item.product_naam,
                    "aantal": item.aantal,
                    "prijs": item.prijs,
                    "opmerking": item.opmerking
                }
                for item in order.items
            ]
        }
        result.append(order_dict)
    
    return result


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific order by ID.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestelling niet gevonden"
        )
    
    # Get customer name if klant_id exists
    klant_naam = None
    if order.klant_id:
        customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
        if customer:
            klant_naam = customer.naam
    
    return {
        "id": order.id,
        "klant_id": order.klant_id,
        "klant_naam": klant_naam,
        "koerier_id": order.koerier_id,
        "datum": order.datum,
        "tijd": order.tijd,
        "totaal": order.totaal,
        "opmerking": order.opmerking,
        "bonnummer": order.bonnummer,
        "levertijd": order.levertijd,
        "status": order.status or "Nieuw",
        "items": [
            {
                "id": item.id,
                "bestelling_id": item.bestelling_id,
                "product_naam": item.product_naam,
                "aantal": item.aantal,
                "prijs": item.prijs,
                "opmerking": item.opmerking,
                "extras": json.loads(item.extras) if item.extras else None
            }
            for item in order.items
        ]
    }


@router.post("/orders/public", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_public_order(
    request: Request,
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new order (public endpoint, no authentication required).
    """
    # Validate customer exists if provided
    if order.klant_id:
        customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Klant niet gevonden"
            )
    
    # Generate bonnummer
    bonnummer = generate_bonnummer(db)
    
    # Get current date and time
    now = datetime.now()
    datum = now.strftime("%Y-%m-%d")
    tijd = now.strftime("%H:%M:%S")
    
    # Create order
    db_order = Order(
        klant_id=order.klant_id,
        koerier_id=order.koerier_id,
        datum=datum,
        tijd=tijd,
        totaal=order.totaal,
        opmerking=order.opmerking,
        bonnummer=bonnummer,
        levertijd=order.levertijd,
        status=order.status or "Nieuw",
        betaalmethode=getattr(order, 'betaalmethode', 'cash'),
        online_bestelling=1,  # Mark as online order
        status_updated_at=now
    )
    db.add(db_order)
    db.flush()  # Get order ID
    
    # Create order items
    for item_data in order.items:
        # Store extras as JSON string
        extras_json = None
        if hasattr(item_data, 'extras') and item_data.extras:
            extras_json = json.dumps(item_data.extras, ensure_ascii=False)
        
        db_item = OrderItem(
            bestelling_id=db_order.id,
            product_naam=item_data.product_naam,
            aantal=item_data.aantal,
            prijs=item_data.prijs,
            opmerking=item_data.opmerking,
            extras=extras_json
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    
    # Update customer statistics if customer exists
    if order.klant_id:
        customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
        if customer:
            customer.totaal_bestellingen += 1
            customer.totaal_besteed += order.totaal
            customer.laatste_bestelling = f"{datum} {tijd}"
            db.commit()
    
    logger.info(f"Public order created: {db_order.id} - Bonnummer: {bonnummer}")
    
    # Send notifications
    try:
        from app.services.notification import notification_service
        import asyncio
        
        # Get customer contact info if available
        customer_email = None
        customer_phone = None
        if order.klant_id:
            customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
            if customer:
                customer_email = None  # Email not available in Customer model
                customer_phone = customer.telefoon
        
        order_notification_data = {
            "id": db_order.id,
            "bonnummer": db_order.bonnummer,
            "totaal": db_order.totaal,
            "datum": db_order.datum,
            "tijd": db_order.tijd,
            "status": db_order.status or "Nieuw",
            "items": [
                {
                    "product_naam": item.product_naam,
                    "aantal": item.aantal,
                    "prijs": item.prijs
                }
                for item in db_order.items
            ]
        }
        
        # Send customer confirmation (async, don't wait)
        asyncio.create_task(
            notification_service.send_order_confirmation(
                order_notification_data,
                customer_email,
                customer_phone
            )
        )
        
        # Send admin notification (async, don't wait)
        asyncio.create_task(
            notification_service.send_admin_notification(order_notification_data)
        )
    except Exception as e:
        logger.warning(f"Could not send notifications: {e}")
    
    # Broadcast new order to admin clients via WebSocket
    try:
        from app.api.websocket import broadcast_new_order
        broadcast_new_order({
            "id": db_order.id,
            "bonnummer": db_order.bonnummer,
            "totaal": db_order.totaal,
            "datum": db_order.datum,
            "tijd": db_order.tijd,
            "status": db_order.status or "Nieuw",
            "klant_naam": None  # Will be filled if klant_id exists
        })
    except Exception as e:
        logger.warning(f"Could not broadcast new order: {e}")
    
    # Return order with items
    return {
        "id": db_order.id,
        "klant_id": db_order.klant_id,
        "koerier_id": db_order.koerier_id,
        "datum": db_order.datum,
        "tijd": db_order.tijd,
        "totaal": db_order.totaal,
        "opmerking": db_order.opmerking,
        "bonnummer": db_order.bonnummer,
        "levertijd": db_order.levertijd,
        "status": db_order.status or "Nieuw",
        "items": [
            {
                "id": item.id,
                "bestelling_id": item.bestelling_id,
                "product_naam": item.product_naam,
                "aantal": item.aantal,
                "prijs": item.prijs,
                "opmerking": item.opmerking
            }
            for item in db_order.items
        ]
    }


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: Request,
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new order.
    """
    # Validate customer exists if provided
    if order.klant_id:
        customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Klant niet gevonden"
            )
    
    # Generate bonnummer
    bonnummer = generate_bonnummer(db)
    
    # Get current date and time
    now = datetime.now()
    datum = now.strftime("%Y-%m-%d")
    tijd = now.strftime("%H:%M:%S")
    
    # Create order
    db_order = Order(
        klant_id=order.klant_id,
        koerier_id=order.koerier_id,
        datum=datum,
        tijd=tijd,
        totaal=order.totaal,
        opmerking=order.opmerking,
        bonnummer=bonnummer,
        levertijd=order.levertijd,
        status=order.status or "Nieuw"
    )
    db.add(db_order)
    db.flush()  # Get order ID
    
    # Create order items
    for item_data in order.items:
        # Store extras as JSON string
        extras_json = None
        if hasattr(item_data, 'extras') and item_data.extras:
            extras_json = json.dumps(item_data.extras, ensure_ascii=False)
        
        db_item = OrderItem(
            bestelling_id=db_order.id,
            product_naam=item_data.product_naam,
            aantal=item_data.aantal,
            prijs=item_data.prijs,
            opmerking=item_data.opmerking,
            extras=extras_json
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    
    # Update customer statistics if customer exists
    if order.klant_id:
        customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
        if customer:
            customer.totaal_bestellingen += 1
            customer.totaal_besteed += order.totaal
            customer.laatste_bestelling = f"{datum} {tijd}"
            db.commit()
    
    logger.info(f"Order created: {db_order.id} - Bonnummer: {bonnummer}")
    
    # Get customer name if klant_id exists
    klant_naam = None
    if db_order.klant_id:
        customer = db.query(Customer).filter(Customer.id == db_order.klant_id).first()
        if customer:
            klant_naam = customer.naam
    
    # Return order with items
    return {
        "id": db_order.id,
        "klant_id": db_order.klant_id,
        "klant_naam": klant_naam,
        "koerier_id": db_order.koerier_id,
        "datum": db_order.datum,
        "tijd": db_order.tijd,
        "totaal": db_order.totaal,
        "opmerking": db_order.opmerking,
        "bonnummer": db_order.bonnummer,
        "levertijd": db_order.levertijd,
        "status": db_order.status or "Nieuw",
        "items": [
            {
                "id": item.id,
                "bestelling_id": item.bestelling_id,
                "product_naam": item.product_naam,
                "aantal": item.aantal,
                "prijs": item.prijs,
                "opmerking": item.opmerking
            }
            for item in db_order.items
        ]
    }


@router.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update an order.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestelling niet gevonden"
        )
    
    update_data = order_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    # Update status_updated_at if status is being changed
    if 'status' in update_data:
        order.status_updated_at = datetime.now()
    
    db.commit()
    db.refresh(order)
    
    logger.info(f"Order updated: {order_id} - Status: {order.status}")
    
    # Send status update notification if status changed
    try:
        from app.services.notification import notification_service
        import asyncio
        
        # Get customer contact info if available
        customer_email = None
        customer_phone = None
        if order.klant_id:
            customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
            if customer:
                customer_email = None  # Email not available in Customer model
                customer_phone = customer.telefoon
        
        status_update_data = {
            "id": order.id,
            "bonnummer": order.bonnummer,
            "status": order.status or "Nieuw",
            "totaal": order.totaal,
            "datum": order.datum,
            "tijd": order.tijd
        }
        
        # Send status update notification (async, don't wait)
        asyncio.create_task(
            notification_service.send_status_update(
                status_update_data,
                customer_email,
                customer_phone
            )
        )
    except Exception as e:
        logger.warning(f"Could not send status update notification: {e}")
    
    # Broadcast status change via WebSocket
    try:
        from app.api.websocket import broadcast_status_change
        broadcast_status_change({
            "id": order.id,
            "bonnummer": order.bonnummer,
            "status": order.status or "Nieuw",
            "totaal": order.totaal,
            "datum": order.datum,
            "tijd": order.tijd
        })
    except Exception as e:
        logger.warning(f"Could not broadcast status change: {e}")
    
    return {
        "id": order.id,
        "klant_id": order.klant_id,
        "koerier_id": order.koerier_id,
        "datum": order.datum,
        "tijd": order.tijd,
        "totaal": order.totaal,
        "opmerking": order.opmerking,
        "bonnummer": order.bonnummer,
        "levertijd": order.levertijd,
        "status": order.status or "Nieuw",
        "items": [
            {
                "id": item.id,
                "bestelling_id": item.bestelling_id,
                "product_naam": item.product_naam,
                "aantal": item.aantal,
                "prijs": item.prijs,
                "opmerking": item.opmerking,
                "extras": json.loads(item.extras) if item.extras else None
            }
            for item in order.items
        ]
    }


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an order.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestelling niet gevonden"
        )
    
    db.delete(order)
    db.commit()
    
    logger.info(f"Order deleted: {order_id}")
    return None


@router.post("/orders/delete-multiple", status_code=status.HTTP_200_OK)
async def delete_orders(
    order_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete multiple orders or all orders.
    If order_ids is provided, delete only those orders.
    If order_ids is None or empty, delete all orders (requires confirmation).
    """
    try:
        from sqlalchemy import text
        
        if order_ids and len(order_ids) > 0:
            # Delete specific orders
            deleted_count = 0
            for order_id in order_ids:
                order = db.query(Order).filter(Order.id == order_id).first()
                if order:
                    db.delete(order)
                    deleted_count += 1
            
            db.commit()
            logger.info(f"Deleted {deleted_count} orders: {order_ids}")
            return {
                "message": f"{deleted_count} bestelling(en) succesvol verwijderd",
                "deleted_count": deleted_count
            }
        else:
            # Delete all orders
            result = db.execute(text("SELECT COUNT(*) as count FROM bestellingen"))
            total_count = result.fetchone()[0]
            
            if total_count == 0:
                return {
                    "message": "Geen bestellingen gevonden om te verwijderen",
                    "deleted_count": 0
                }
            
            # Delete all orders
            db.execute(text("DELETE FROM bestellingen"))
            db.commit()
            
            logger.info(f"Deleted all orders ({total_count} orders)")
            return {
                "message": f"Alle bestellingen ({total_count}) succesvol verwijderd",
                "deleted_count": total_count
            }
    except Exception as e:
        logger.exception(f"Error deleting orders: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fout bij verwijderen bestellingen: {str(e)}"
        )


@router.post("/orders/renumber", status_code=status.HTTP_200_OK)
async def renumber_receipts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Renumber all receipts in chronological order.
    This renumbers all orders by date and time, updating bon_teller table accordingly.
    """
    try:
        from sqlalchemy import text
        from datetime import datetime
        
        # Get all orders sorted by date and time
        orders = db.execute(text("""
            SELECT id, datum, tijd
            FROM bestellingen
            ORDER BY datum ASC, tijd ASC
        """)).fetchall()
        
        if not orders:
            return {"message": "Geen bestellingen gevonden om te hernummeren", "updated_count": 0}
        
        # Renumber per day
        current_date = None
        day_counter = {}
        updates = []
        
        for order in orders:
            order_id = order[0]  # id
            order_date = order[1]  # datum
            order_time = order[2]  # tijd
            
            # Reset counter for new day
            if order_date != current_date:
                current_date = order_date
                # Parse year from date
                try:
                    if isinstance(order_date, str):
                        year = int(order_date.split('-')[0])
                    else:
                        year = order_date.year
                except (ValueError, IndexError, AttributeError):
                    year = datetime.now().year
                
                # Start counter for this day
                day_counter[order_date] = {'year': year, 'counter': 0}
            
            # Increment counter
            day_counter[order_date]['counter'] += 1
            counter = day_counter[order_date]['counter']
            year = day_counter[order_date]['year']
            
            # Generate new bonnummer: YYYYNNNN
            new_bonnummer = f"{year}{counter:04d}"
            
            updates.append((new_bonnummer, order_id))
        
        # Update all bonnummers
        updated_count = 0
        for new_bonnummer, order_id in updates:
            db.execute(text("""
                UPDATE bestellingen
                SET bonnummer = :bonnummer
                WHERE id = :order_id
            """), {"bonnummer": new_bonnummer, "order_id": order_id})
            updated_count += 1
        
        # Update bon_teller table for all involved days
        for date_str, info in day_counter.items():
            try:
                # Parse date to get year and day of year
                if isinstance(date_str, str):
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    date_obj = date_str
                
                year = date_obj.year
                day_of_year = date_obj.timetuple().tm_yday
                last_number = info['counter']
                
                # Update bon_teller
                db.execute(text("""
                    INSERT OR REPLACE INTO bon_teller (jaar, dag, laatste_nummer)
                    VALUES (:jaar, :dag, :laatste_nummer)
                """), {"jaar": year, "dag": day_of_year, "laatste_nummer": last_number})
            except Exception as e:
                logger.warning(f"Kon bon_teller niet updaten voor {date_str}: {e}")
        
        db.commit()
        
        logger.info(f"Receipts renumbered: {updated_count} orders updated")
        return {
            "message": f"Bonnen succesvol hernummerd! Aantal bijgewerkte bonnen: {updated_count}",
            "updated_count": updated_count
        }
    except Exception as e:
        logger.exception(f"Error renumbering receipts: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fout bij hernummeren bonnen: {str(e)}"
        )


@router.get("/orders/online/pending")
async def get_pending_online_orders(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all pending online orders for the cash register system.
    Returns orders with status 'Nieuw', 'In de keuken', or 'Onderweg' that are online orders.
    """
    try:
        # Get pending online orders (status: Nieuw, In de keuken, or Onderweg)
        orders = db.query(Order).filter(
            Order.online_bestelling == 1,
            Order.status.in_(["Nieuw", "In de keuken", "Onderweg"])
        ).order_by(Order.datum.desc(), Order.tijd.desc()).all()
        
        result = []
        for order in orders:
            try:
                # Get customer details if klant_id exists
                klant_naam = None
                klant_adres = None
                klant_telefoon = None
                klant_email = None
                klant_straat = None
                klant_huisnummer = None
                klant_postcode = None
                klant_gemeente = None
                
                if order.klant_id:
                    customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
                    if customer:
                        klant_naam = customer.naam
                        klant_straat = customer.straat
                        klant_huisnummer = customer.huisnummer
                        klant_telefoon = customer.telefoon
                        klant_email = None  # Email not available in Customer model
                        
                        # Parse plaats (usually "Postcode Gemeente" format)
                        if customer.plaats:
                            import re
                            plaats = customer.plaats.strip()
                            # Try to extract postcode (4 digits) and gemeente
                            postcode_match = re.match(r'^(\d{4})\s+(.+)$', plaats)
                            if postcode_match:
                                klant_postcode = postcode_match.group(1)
                                klant_gemeente = postcode_match.group(2)
                            else:
                                # If no postcode pattern, assume it's just gemeente
                                klant_gemeente = plaats
                        
                        # Build address string for backward compatibility
                        adres_parts = []
                        if customer.straat:
                            adres_parts.append(customer.straat)
                        if customer.huisnummer:
                            adres_parts.append(str(customer.huisnummer))
                        if adres_parts:
                            adres_str = " ".join(adres_parts)
                            if customer.plaats:
                                klant_adres = f"{adres_str}, {customer.plaats}"
                            else:
                                klant_adres = adres_str
                        else:
                            klant_adres = customer.plaats if customer.plaats else None
                
                # Build items list
                items_list = []
                for item in order.items:
                    try:
                        extras_data = None
                        if item.extras:
                            try:
                                extras_data = json.loads(item.extras) if isinstance(item.extras, str) else item.extras
                            except json.JSONDecodeError:
                                logger.warning(f"Could not parse extras JSON for item {item.id}: {item.extras}")
                                extras_data = None
                        
                        items_list.append({
                            "id": item.id,
                            "bestelling_id": item.bestelling_id,
                            "product_naam": item.product_naam,
                            "aantal": item.aantal,
                            "prijs": float(item.prijs),
                            "opmerking": item.opmerking,
                            "extras": extras_data
                        })
                    except Exception as e:
                        logger.error(f"Error processing order item {item.id}: {e}")
                        continue
                
                order_dict = {
                    "id": order.id,
                    "klant_id": order.klant_id,
                    "klant_naam": klant_naam,
                    "klant_adres": klant_adres,
                    "klant_telefoon": klant_telefoon,
                    "klant_email": klant_email,
                    "klant_straat": klant_straat,
                    "klant_huisnummer": klant_huisnummer,
                    "klant_postcode": klant_postcode,
                    "klant_gemeente": klant_gemeente,
                    "koerier_id": order.koerier_id,
                    "datum": order.datum,
                    "tijd": order.tijd,
                    "totaal": float(order.totaal),
                    "opmerking": order.opmerking,
                    "bonnummer": order.bonnummer,
                    "levertijd": order.levertijd,
                    "status": order.status or "Nieuw",
                    "betaalmethode": getattr(order, 'betaalmethode', 'cash') or 'cash',
                    "afstand_km": float(getattr(order, 'afstand_km', 0)) if getattr(order, 'afstand_km', None) else None,
                    "online_bestelling": int(getattr(order, 'online_bestelling', 0)),
                    "items": items_list
                }
                result.append(order_dict)
            except Exception as e:
                logger.error(f"Error processing order {order.id}: {e}")
                continue
        
        return result
    except Exception as e:
        logger.error(f"Error in get_pending_online_orders: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching pending orders: {str(e)}"
        )


@router.put("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update order status and optionally delivery time and courier.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestelling niet gevonden"
        )
    
    order.status = status_update.new_status
    order.status_updated_at = datetime.now()
    
    if status_update.levertijd:
        order.levertijd = status_update.levertijd
    
    if status_update.koerier_id is not None:
        order.koerier_id = status_update.koerier_id
    
    db.commit()
    db.refresh(order)
    
    logger.info(f"Order status updated: {order_id} - Status: {status_update.new_status}")
    
    # Send status update notification
    try:
        from app.services.notification import notification_service
        import asyncio
        
        customer_email = None
        customer_phone = None
        if order.klant_id:
            customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
            if customer:
                customer_email = None  # Email not available in Customer model
                customer_phone = customer.telefoon
        
        status_update_data = {
            "id": order.id,
            "bonnummer": order.bonnummer,
            "status": status_update.new_status,
            "levertijd": status_update.levertijd or order.levertijd,
            "totaal": order.totaal,
            "datum": order.datum,
            "tijd": order.tijd
        }
        
        asyncio.create_task(
            notification_service.send_status_update(
                status_update_data,
                customer_email,
                customer_phone
            )
        )
    except Exception as e:
        logger.warning(f"Could not send status update notification: {e}")
    
    # Get customer details for response
    klant_naam = None
    klant_adres = None
    klant_telefoon = None
    klant_email = None
    
    if order.klant_id:
        customer = db.query(Customer).filter(Customer.id == order.klant_id).first()
        if customer:
            klant_naam = customer.naam
            # Build address using correct field names
            adres_parts = []
            if customer.straat:
                adres_parts.append(customer.straat)
            if customer.huisnummer:
                adres_parts.append(str(customer.huisnummer))
            if adres_parts:
                adres_str = " ".join(adres_parts)
                if customer.plaats:
                    klant_adres = f"{adres_str}, {customer.plaats}"
                else:
                    klant_adres = adres_str
            else:
                klant_adres = customer.plaats if customer.plaats else None
            klant_telefoon = customer.telefoon
            klant_email = None  # Email not available in Customer model
    
    return {
        "id": order.id,
        "klant_id": order.klant_id,
        "klant_naam": klant_naam,
        "klant_adres": klant_adres,
        "klant_telefoon": klant_telefoon,
        "klant_email": klant_email,
        "koerier_id": order.koerier_id,
        "datum": order.datum,
        "tijd": order.tijd,
        "totaal": order.totaal,
        "opmerking": order.opmerking,
        "bonnummer": order.bonnummer,
        "levertijd": order.levertijd,
        "status": order.status or "Nieuw",
        "betaalmethode": getattr(order, 'betaalmethode', 'cash'),
        "afstand_km": getattr(order, 'afstand_km', None),
        "online_bestelling": getattr(order, 'online_bestelling', 0),
        "items": [
            {
                "id": item.id,
                "bestelling_id": item.bestelling_id,
                "product_naam": item.product_naam,
                "aantal": item.aantal,
                "prijs": item.prijs,
                "opmerking": item.opmerking,
                "extras": json.loads(item.extras) if item.extras else None
            }
            for item in order.items
        ]
    }

