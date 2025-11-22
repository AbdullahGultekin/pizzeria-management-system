"""
Courier Service - Business Logic

This module contains business logic for courier management operations.
"""

from typing import Dict, List, Optional, Tuple
from datetime import date
import sqlite3
from database import DatabaseContext
from exceptions import DatabaseError
from logging_config import get_logger
from modules.courier_config import STARTGELD, KM_TARIEF, UUR_TARIEF

logger = get_logger("pizzeria.courier_service")


class CourierService:
    """Service class for courier-related business operations."""
    
    @staticmethod
    def get_all_couriers() -> Dict[str, int]:
        """
        Get all couriers from database.
        
        Returns:
            Dictionary mapping courier names to their IDs
        """
        try:
            with DatabaseContext() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, naam FROM koeriers ORDER BY naam")
                return {row['naam']: row['id'] for row in cursor.fetchall()}
        except sqlite3.Error as e:
            logger.exception(f"Error fetching couriers: {e}")
            raise DatabaseError(f"Kon koeriers niet ophalen: {e}") from e
    
    @staticmethod
    def add_courier(naam: str) -> None:
        """
        Add a new courier to the database.
        
        Args:
            naam: Name of the courier
            
        Raises:
            DatabaseError: If courier already exists or database error occurs
        """
        if not naam or not naam.strip():
            raise ValueError("Koerier naam mag niet leeg zijn")
        
        naam = naam.strip()
        try:
            with DatabaseContext() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO koeriers (naam) VALUES (?)", (naam,))
            logger.info(f"Courier '{naam}' added successfully")
        except sqlite3.IntegrityError:
            raise DatabaseError(f"Koerier '{naam}' bestaat al.")
        except sqlite3.Error as e:
            logger.exception(f"Error adding courier: {e}")
            raise DatabaseError(f"Kon koerier niet toevoegen: {e}") from e
    
    @staticmethod
    def delete_courier(koerier_id: int, naam: str) -> None:
        """
        Delete a courier from the database.
        
        Args:
            koerier_id: ID of the courier to delete
            naam: Name of the courier (for error messages)
            
        Raises:
            DatabaseError: If courier has assigned orders or database error occurs
        """
        try:
            with DatabaseContext() as conn:
                cursor = conn.cursor()
                # Check if courier has assigned orders
                cursor.execute("SELECT COUNT(*) FROM bestellingen WHERE koerier_id = ?", (koerier_id,))
                count = cursor.fetchone()[0]
                if count > 0:
                    raise DatabaseError(
                        f"Kan '{naam}' niet verwijderen. De koerier is nog aan {count} bestelling(en) toegewezen."
                    )
                cursor.execute("DELETE FROM koeriers WHERE id = ?", (koerier_id,))
            logger.info(f"Courier '{naam}' deleted successfully")
        except DatabaseError:
            raise
        except sqlite3.Error as e:
            logger.exception(f"Error deleting courier: {e}")
            raise DatabaseError(f"Kon koerier niet verwijderen: {e}") from e
    
    @staticmethod
    def get_orders_for_date(order_date: date, exclude_afhaal: bool = True, only_without_courier: bool = False) -> List[Dict]:
        """
        Get all orders for a specific date.
        
        Args:
            order_date: Date to get orders for
            exclude_afhaal: If True, exclude pickup orders (default: True for courier page)
            only_without_courier: If True, only return orders without assigned courier
            
        Returns:
            List of order dictionaries with customer and courier information
        """
        try:
            with DatabaseContext() as conn:
                cursor = conn.cursor()
                # Check if afhaal column exists
                cursor.execute("PRAGMA table_info(bestellingen)")
                columns = [row[1] for row in cursor.fetchall()]
                has_afhaal = 'afhaal' in columns
                
                # Build query with filters
                conditions = ["b.datum = ?"]
                params = [order_date.strftime('%Y-%m-%d')]
                
                if exclude_afhaal and has_afhaal:
                    conditions.append("(b.afhaal IS NULL OR b.afhaal = 0)")
                
                if only_without_courier:
                    conditions.append("b.koerier_id IS NULL")
                
                where_clause = " AND ".join(conditions)
                
                query = f"""
                    SELECT b.id,
                           b.totaal,
                           b.tijd,
                           k.straat,
                           k.huisnummer,
                           k.plaats,
                           k.telefoon,
                           ko.naam AS koerier_naam,
                           b.afhaal
                    FROM bestellingen b
                    JOIN klanten k ON b.klant_id = k.id
                    LEFT JOIN koeriers ko ON b.koerier_id = ko.id
                    WHERE {where_clause}
                    ORDER BY b.tijd
                """
                cursor.execute(query, tuple(params))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.exception(f"Error fetching orders: {e}")
            raise DatabaseError(f"Kon bestellingen niet ophalen: {e}") from e
    
    @staticmethod
    def assign_courier_to_orders(order_ids: List[int], koerier_id: int) -> None:
        """
        Assign a courier to multiple orders.
        
        Args:
            order_ids: List of order IDs to assign
            koerier_id: ID of the courier to assign
        """
        try:
            with DatabaseContext() as conn:
                cursor = conn.cursor()
                for order_id in order_ids:
                    cursor.execute(
                        "UPDATE bestellingen SET koerier_id = ? WHERE id = ?",
                        (koerier_id, order_id)
                    )
            logger.info(f"Assigned courier {koerier_id} to {len(order_ids)} orders")
        except sqlite3.Error as e:
            logger.exception(f"Error assigning courier: {e}")
            raise DatabaseError(f"Kon koerier niet toewijzen: {e}") from e
    
    @staticmethod
    def remove_courier_from_orders(order_ids: List[int]) -> None:
        """
        Remove courier assignment from multiple orders.
        
        Args:
            order_ids: List of order IDs to unassign
        """
        try:
            with DatabaseContext() as conn:
                cursor = conn.cursor()
                for order_id in order_ids:
                    cursor.execute(
                        "UPDATE bestellingen SET koerier_id = NULL WHERE id = ?",
                        (order_id,)
                    )
            logger.info(f"Removed courier from {len(order_ids)} orders")
        except sqlite3.Error as e:
            logger.exception(f"Error removing courier: {e}")
            raise DatabaseError(f"Kon toewijzing niet verwijderen: {e}") from e
    
    @staticmethod
    def calculate_payment(
        subtotal: float,
        extra_km: float = 0.0,
        extra_uur: float = 0.0,
        extra_bedrag: float = 0.0
    ) -> float:
        """
        Calculate total payment for a courier.
        
        Args:
            subtotal: Subtotal from orders
            extra_km: Extra kilometers
            extra_uur: Extra hours
            extra_bedrag: Extra amount
            
        Returns:
            Total payment amount
        """
        try:
            total = (extra_km * KM_TARIEF) + (extra_uur * UUR_TARIEF) + extra_bedrag
            return round(total, 2)
        except (TypeError, ValueError):
            logger.warning("Invalid payment calculation parameters")
            return 0.0
    
    @staticmethod
    def calculate_final_total(subtotal: float) -> float:
        """
        Calculate final total including starting money.
        
        Args:
            subtotal: Subtotal from orders
            
        Returns:
            Final total including starting money
        """
        return round(subtotal + STARTGELD, 2)



