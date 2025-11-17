"""
History Service - Business Logic

This module contains business logic for order history operations.
"""

from typing import Dict, List, Optional, Tuple
from datetime import date, datetime
from database import DatabaseContext
from exceptions import DatabaseError
from logging_config import get_logger
import json

logger = get_logger("pizzeria.history_service")


class HistoryService:
    """Service class for order history operations."""
    
    @staticmethod
    def search_orders(
        search_term: Optional[str] = None,
        date_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Search orders with optional filters.
        
        Args:
            search_term: Search in name, phone, or address
            date_filter: Filter by date (YYYY-MM-DD format)
            limit: Maximum number of results
            
        Returns:
            List of order dictionaries
        """
        try:
            with DatabaseContext() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT b.id,
                           b.datum,
                           b.tijd,
                           b.totaal,
                           b.bonnummer,
                           b.opmerking,
                           b.levertijd,
                           k.naam,
                           k.telefoon,
                           k.straat,
                           k.huisnummer,
                           k.plaats
                    FROM bestellingen b
                    JOIN klanten k ON b.klant_id = k.id
                """
                
                params = []
                conditions = []
                
                if search_term and search_term.strip():
                    search = f"%{search_term.strip()}%"
                    conditions.append("(k.naam LIKE ? OR k.telefoon LIKE ? OR k.straat LIKE ?)")
                    params.extend([search, search, search])
                
                if date_filter and date_filter.strip():
                    conditions.append("b.datum = ?")
                    params.append(date_filter.strip())
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY b.datum DESC, b.tijd DESC"
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.exception(f"Error searching orders: {e}")
            raise DatabaseError(f"Kon bestellingen niet ophalen: {e}") from e
    
    @staticmethod
    def get_order_details(order_id: int) -> Optional[Dict]:
        """
        Get detailed information about a specific order.
        
        Args:
            order_id: ID of the order
            
        Returns:
            Dictionary with order details or None if not found
        """
        try:
            with DatabaseContext() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT b.id,
                           b.bonnummer,
                           b.opmerking,
                           b.datum,
                           b.tijd,
                           b.totaal,
                           b.levertijd,
                           b.klant_id,
                           k.telefoon,
                           k.straat,
                           k.huisnummer,
                           k.plaats,
                           k.naam
                    FROM bestellingen b
                    JOIN klanten k ON b.klant_id = k.id
                    WHERE b.id = ?
                """, (order_id,))
                order = cursor.fetchone()
                
                if not order:
                    return None
                
                # Get order items
                cursor.execute("""
                    SELECT categorie, product, aantal, prijs, extras, opmerking
                    FROM bestelregels
                    WHERE bestelling_id = ?
                    ORDER BY id
                """, (order_id,))
                items = cursor.fetchall()
                
                return {
                    'order': dict(order),
                    'items': [dict(item) for item in items]
                }
        except Exception as e:
            logger.exception(f"Error getting order details: {order_id}")
            raise DatabaseError(f"Kon bestellingdetails niet ophalen: {e}") from e
    
    @staticmethod
    def delete_order(order_id: int) -> Optional[int]:
        """
        Delete an order and its items.
        
        Args:
            order_id: ID of the order to delete
            
        Returns:
            Customer ID if order was deleted, None otherwise
        """
        try:
            with DatabaseContext() as conn:
                cursor = conn.cursor()
                
                # Get customer ID before deletion
                cursor.execute("SELECT klant_id FROM bestellingen WHERE id = ?", (order_id,))
                row = cursor.fetchone()
                klant_id = row['klant_id'] if row else None
                
                # Delete order items
                cursor.execute("DELETE FROM bestelregels WHERE bestelling_id = ?", (order_id,))
                
                # Delete order
                cursor.execute("DELETE FROM bestellingen WHERE id = ?", (order_id,))
                
                return klant_id
        except Exception as e:
            logger.exception(f"Error deleting order: {order_id}")
            raise DatabaseError(f"Kon bestelling niet verwijderen: {e}") from e
    
    @staticmethod
    def delete_all_orders() -> List[int]:
        """
        Delete all orders and their items.
        
        Returns:
            List of unique customer IDs that need statistics update
        """
        try:
            with DatabaseContext() as conn:
                cursor = conn.cursor()
                
                # Get all customer IDs before deletion
                cursor.execute("SELECT DISTINCT klant_id FROM bestellingen WHERE klant_id IS NOT NULL")
                klant_ids = [row['klant_id'] for row in cursor.fetchall()]
                
                # Delete all order items
                cursor.execute("DELETE FROM bestelregels")
                
                # Delete all orders
                cursor.execute("DELETE FROM bestellingen")
                
                return klant_ids
        except Exception as e:
            logger.exception("Error deleting all orders")
            raise DatabaseError(f"Kon alle bestellingen niet verwijderen: {e}") from e
    
    @staticmethod
    def get_statistics(search_term: Optional[str] = None, date_filter: Optional[str] = None) -> Dict[str, float]:
        """
        Get statistics for filtered orders.
        
        Args:
            search_term: Optional search filter
            date_filter: Optional date filter
            
        Returns:
            Dictionary with count and total
        """
        try:
            orders = HistoryService.search_orders(search_term, date_filter)
            count = len(orders)
            total = sum(float(order['totaal']) for order in orders)
            return {
                'count': count,
                'total': round(total, 2),
                'average': round(total / count, 2) if count > 0 else 0.0
            }
        except Exception as e:
            logger.exception("Error calculating statistics")
            return {'count': 0, 'total': 0.0, 'average': 0.0}

