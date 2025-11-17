"""Shared pytest fixtures for testing."""

import pytest
import sqlite3
import os
import tempfile
from database import DatabaseContext, create_tables, add_database_indexes
from repositories.customer_repository import CustomerRepository
from repositories.order_repository import OrderRepository
from services.customer_service import CustomerService
from services.order_service import OrderService


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Save original DB file name
    from database import DB_FILE
    original_db = DB_FILE
    
    # Create temporary database
    fd, temp_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Temporarily change DB_FILE
    import database
    database.DB_FILE = temp_path
    
    # Create tables and indexes
    with DatabaseContext() as conn:
        cursor = conn.cursor()
        # Create minimal schema for testing
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS klanten (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telefoon TEXT UNIQUE NOT NULL,
                straat TEXT,
                huisnummer TEXT,
                plaats TEXT,
                naam TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bestellingen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                klant_id INTEGER,
                datum TEXT NOT NULL,
                tijd TEXT NOT NULL,
                totaal REAL NOT NULL,
                opmerking TEXT,
                bonnummer TEXT,
                koerier_id INTEGER,
                FOREIGN KEY (klant_id) REFERENCES klanten(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bestelregels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bestelling_id INTEGER NOT NULL,
                categorie TEXT,
                product TEXT,
                aantal INTEGER,
                prijs REAL,
                extras TEXT,
                FOREIGN KEY (bestelling_id) REFERENCES bestellingen(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bon_teller (
                jaar INTEGER NOT NULL,
                dag INTEGER NOT NULL,
                laatste_nummer INTEGER NOT NULL,
                PRIMARY KEY (jaar, dag)
            )
        ''')
        add_database_indexes(cursor)
    
    yield temp_path
    
    # Cleanup
    database.DB_FILE = original_db
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def customer_repo(temp_db):
    """Provide a CustomerRepository instance."""
    return CustomerRepository()


@pytest.fixture
def order_repo(temp_db):
    """Provide an OrderRepository instance."""
    return OrderRepository()


@pytest.fixture
def customer_service(customer_repo):
    """Provide a CustomerService instance."""
    return CustomerService(customer_repo)


@pytest.fixture
def order_service(order_repo, customer_repo):
    """Provide an OrderService instance."""
    return OrderService(order_repo, customer_repo)


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return {
        "telefoon": "0123456789",
        "straat": "Teststraat",
        "huisnummer": "123",
        "plaats": "Teststad",
        "naam": "Test Klant"
    }


@pytest.fixture
def sample_order_items():
    """Sample order items for testing."""
    return [
        {
            "categorie": "Pizza's",
            "product": "Margherita",
            "aantal": 2,
            "prijs": 10.50,
            "extras": {}
        }
    ]



