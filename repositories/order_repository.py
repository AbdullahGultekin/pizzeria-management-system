"""Repository for order data access operations."""

from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from database import DatabaseContext
from logging_config import get_logger

logger = get_logger("pizzeria.repositories.order")


class OrderRepository:
    """Repository for order-related database operations."""
    
    @staticmethod
    def create(
        klant_id: int,
        datum: str,
        tijd: str,
        totaal: float,
        opmerking: Optional[str],
        bonnummer: str,
        koerier_id: Optional[int] = None,
        levertijd: Optional[str] = None,
        afhaal: bool = False
    ) -> int:
        """
        Create a new order.
        
        Args:
            klant_id: Customer ID
            datum: Order date (YYYY-MM-DD)
            tijd: Order time (HH:MM)
            totaal: Total price
            opmerking: Optional order notes
            bonnummer: Receipt number
            koerier_id: Optional courier ID
            levertijd: Optional delivery time (e.g., "19:30")
            afhaal: Whether this is a pickup order (default: False)
            
        Returns:
            Order ID
        """
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            # Check if afhaal and status columns exist (cached check)
            from modules.courier_service import CourierService
            has_afhaal = CourierService._has_column("bestellingen", "afhaal")
            has_status = CourierService._has_column("bestellingen", "status")
            
            if has_afhaal:
                if has_status:
                    # Set status to "Nieuw" for pickup orders, NULL for delivery orders
                    status_value = "Nieuw" if afhaal else None
                    cursor.execute(
                        "INSERT INTO bestellingen (klant_id, datum, tijd, totaal, opmerking, bonnummer, koerier_id, levertijd, afhaal, status) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (klant_id, datum, tijd, totaal, opmerking, bonnummer, koerier_id, levertijd, 1 if afhaal else 0, status_value)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO bestellingen (klant_id, datum, tijd, totaal, opmerking, bonnummer, koerier_id, levertijd, afhaal) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (klant_id, datum, tijd, totaal, opmerking, bonnummer, koerier_id, levertijd, 1 if afhaal else 0)
                    )
            else:
                # Fallback for older databases
                cursor.execute(
                    "INSERT INTO bestellingen (klant_id, datum, tijd, totaal, opmerking, bonnummer, koerier_id, levertijd) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (klant_id, datum, tijd, totaal, opmerking, bonnummer, koerier_id, levertijd)
                )
            return cursor.lastrowid
    
    @staticmethod
    def add_order_item(
        bestelling_id: int,
        categorie: str,
        product: str,
        aantal: int,
        prijs: float,
        extras: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Add an item to an order.
        
        Args:
            bestelling_id: Order ID
            categorie: Product category
            product: Product name
            aantal: Quantity
            prijs: Price per unit
            extras: Optional extras dictionary
            
        Returns:
            Order item ID
        """
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            extras_json = json.dumps(extras) if extras else None
            cursor.execute(
                "INSERT INTO bestelregels (bestelling_id, categorie, product, aantal, prijs, extras) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (bestelling_id, categorie, product, aantal, prijs, extras_json)
            )
            return cursor.lastrowid
    
    @staticmethod
    def get_by_id(bestelling_id: int) -> Optional[Dict[str, Any]]:
        """
        Get order by ID.
        
        Args:
            bestelling_id: Order ID
            
        Returns:
            Order data as dict or None if not found
        """
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT b.*, k.telefoon, k.naam as klant_naam, k.straat, k.huisnummer, k.plaats,
                       ko.naam as koerier_naam
                FROM bestellingen b
                JOIN klanten k ON b.klant_id = k.id
                LEFT JOIN koeriers ko ON b.koerier_id = ko.id
                WHERE b.id = ?
                """,
                (bestelling_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    @staticmethod
    def get_order_items(bestelling_id: int) -> List[Dict[str, Any]]:
        """
        Get all items for an order.
        
        Args:
            bestelling_id: Order ID
            
        Returns:
            List of order item dictionaries
        """
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM bestelregels WHERE bestelling_id = ? ORDER BY id",
                (bestelling_id,)
            )
            items = []
            for row in cursor.fetchall():
                item = dict(row)
                # Parse extras JSON
                if item.get('extras'):
                    try:
                        item['extras'] = json.loads(item['extras'])
                    except (json.JSONDecodeError, TypeError):
                        item['extras'] = {}
                items.append(item)
            return items
    
    @staticmethod
    def get_by_date(datum: str) -> List[Dict[str, Any]]:
        """
        Get all orders for a specific date.
        
        Args:
            datum: Date in YYYY-MM-DD format
            
        Returns:
            List of order dictionaries
        """
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT b.id, b.totaal, b.tijd, k.straat, k.huisnummer, k.plaats, k.telefoon,
                       ko.naam AS koerier_naam
                FROM bestellingen b
                JOIN klanten k ON b.klant_id = k.id
                LEFT JOIN koeriers ko ON b.koerier_id = ko.id
                WHERE b.datum = ?
                ORDER BY b.tijd
                """,
                (datum,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_by_customer(klant_id: int) -> List[Dict[str, Any]]:
        """
        Get all orders for a customer.
        
        Args:
            klant_id: Customer ID
            
        Returns:
            List of order dictionaries
        """
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM bestellingen WHERE klant_id = ? ORDER BY datum DESC, tijd DESC",
                (klant_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update_courier(bestelling_id: int, koerier_id: Optional[int]) -> None:
        """
        Update courier assignment for an order.
        
        Args:
            bestelling_id: Order ID
            koerier_id: Courier ID or None to remove assignment
        """
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE bestellingen SET koerier_id = ? WHERE id = ?",
                (koerier_id, bestelling_id)
            )
    
    @staticmethod
    def delete(bestelling_id: int) -> None:
        """
        Delete an order and its items.
        
        Args:
            bestelling_id: Order ID to delete
        """
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            # Delete order items first (foreign key constraint)
            cursor.execute("DELETE FROM bestelregels WHERE bestelling_id = ?", (bestelling_id,))
            # Delete order
            cursor.execute("DELETE FROM bestellingen WHERE id = ?", (bestelling_id,))

