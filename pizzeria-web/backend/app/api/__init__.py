"""
API routes.
"""
from app.api import auth, customers, orders, menu, extras, reports, websocket, printer, contact, addresses, settings

__all__ = ['auth', 'customers', 'orders', 'menu', 'extras', 'reports', 'websocket', 'printer', 'contact', 'addresses', 'settings']
