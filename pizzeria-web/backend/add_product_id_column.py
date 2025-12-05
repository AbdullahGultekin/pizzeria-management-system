"""
Script to add product_id column to bestelregels table.
This allows accurate category detection using product IDs.
"""
import sqlite3
import os
from pathlib import Path

def add_product_id_column():
    """Add product_id column to bestelregels table."""
    # Find database file
    db_path = Path(__file__).parent / "pizzeria.db"
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        print("Please ensure the database file is in the backend directory.")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(bestelregels)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'product_id' in columns:
            print("Column 'product_id' already exists in bestelregels table.")
            conn.close()
            return True
        
        # Add product_id column
        print("Adding product_id column to bestelregels table...")
        cursor.execute("ALTER TABLE bestelregels ADD COLUMN product_id INTEGER")
        conn.commit()
        
        print("Successfully added product_id column to bestelregels table.")
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error adding product_id column: {e}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    add_product_id_column()

