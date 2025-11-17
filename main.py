"""
Pizzeria Management System - Main Entry Point

This file serves as the main entry point for the application.
It uses the PizzeriaApp class from app.py for a clean, object-oriented architecture.

The old procedural code has been refactored into the PizzeriaApp class.
This wrapper maintains backward compatibility while using the new architecture.
"""

from app import main

if __name__ == "__main__":
    main()
