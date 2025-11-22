"""
Script to add status column to existing orders table.
Run this once to migrate existing database.
"""
import sqlite3
import os

def add_status_column():
    db_path = os.path.join(os.path.dirname(__file__), 'pizzeria.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(bestellingen)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'status' in columns:
            print("Status column already exists")
            return
        
        # Add status column with default value
        cursor.execute("""
            ALTER TABLE bestellingen 
            ADD COLUMN status TEXT DEFAULT 'Nieuw' NOT NULL
        """)
        
        # Update existing orders to have a default status
        cursor.execute("""
            UPDATE bestellingen 
            SET status = 'Voltooid' 
            WHERE status IS NULL OR status = ''
        """)
        
        conn.commit()
        print("Status column added successfully")
        
    except Exception as e:
        print(f"Error adding status column: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_status_column()


