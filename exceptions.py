"""
Custom exceptions for the pizzeria application.
"""


class PizzeriaError(Exception):
    """Base exception for all pizzeria application errors."""
    pass


class DatabaseError(PizzeriaError):
    """Raised when database operations fail."""
    pass


class ValidationError(PizzeriaError):
    """Raised when input validation fails."""
    pass


class ConfigurationError(PizzeriaError):
    """Raised when configuration is invalid or missing."""
    pass


class PrinterError(PizzeriaError):
    """Raised when printer operations fail."""
    pass


class OrderError(PizzeriaError):
    """Raised when order operations fail."""
    pass



