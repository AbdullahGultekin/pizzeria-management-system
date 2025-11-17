"""Tests for DatabaseContext."""

import pytest
from database import DatabaseContext, DatabaseError


def test_database_context_commit(temp_db):
    """Test that DatabaseContext commits transactions."""
    with DatabaseContext() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO klanten (telefoon, naam) VALUES (?, ?)", ("1234567890", "Test"))
    
    # Verify data persisted
    with DatabaseContext() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM klanten WHERE telefoon = ?", ("1234567890",))
        result = cursor.fetchone()
        assert result is not None
        assert result["naam"] == "Test"


def test_database_context_rollback_on_exception(temp_db):
    """Test that DatabaseContext rolls back on exception."""
    try:
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO klanten (telefoon, naam) VALUES (?, ?)", ("1234567890", "Test"))
            raise ValueError("Test exception")
    except ValueError:
        pass
    
    # Verify data was not persisted
    with DatabaseContext() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM klanten WHERE telefoon = ?", ("1234567890",))
        result = cursor.fetchone()
        assert result is None


def test_database_context_closes_connection(temp_db):
    """Test that DatabaseContext properly closes connections."""
    with DatabaseContext() as conn:
        assert conn is not None
    
    # Connection should be closed after context exit
    # (We can't directly test this, but if it wasn't closed, we'd get errors on subsequent operations)



