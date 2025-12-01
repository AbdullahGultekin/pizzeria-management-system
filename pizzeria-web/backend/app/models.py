"""
Central database models file for deployment.
This file imports and exports all models for easy deployment.
"""
from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.menu import MenuItem, MenuCategory

# Export all models
__all__ = [
    "Customer",
    "Order",
    "OrderItem",
    "MenuItem",
    "MenuCategory",
]

