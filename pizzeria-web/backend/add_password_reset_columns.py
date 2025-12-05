"""
Script to add password reset columns to the klanten table.
Run this once to add the new columns to the database.
"""
import sqlite3
import os
from pathlib import Path

# Find database file - check multiple locations
possible_paths = [
    Path(__file__).parent / "pizzeria.db",  # pizzeria-web/backend/pizzeria.db
    Path(__file__).parent.parent / "pizzeria.db",  # pizzeria-web/pizzeria.db
    Path(__file__).parent.parent.parent / "pizzeria.db",  # root/pizzeria.db
]

db_path = None
for path in possible_paths:
    if path.exists():
        db_path = path
        break

if not db_path:
    print("Database not found in any of these locations:")
    for path in possible_paths:
        print(f"  - {path}")
    print("Please specify the database path manually.")
    exit(1)

print(f"Connecting to database: {db_path}")

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

try:
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(klanten)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'password_reset_token' in columns:
        print("Column 'password_reset_token' already exists.")
    else:
        print("Adding column 'password_reset_token'...")
        cursor.execute("ALTER TABLE klanten ADD COLUMN password_reset_token TEXT")
        print("✓ Column 'password_reset_token' added.")
    
    if 'password_reset_token_expires' in columns:
        print("Column 'password_reset_token_expires' already exists.")
    else:
        print("Adding column 'password_reset_token_expires'...")
        cursor.execute("ALTER TABLE klanten ADD COLUMN password_reset_token_expires TEXT")
        print("✓ Column 'password_reset_token_expires' added.")
    
    conn.commit()
    print("\n✓ Database migration completed successfully!")
    
except sqlite3.Error as e:
    print(f"❌ Database error: {e}")
    conn.rollback()
    exit(1)
finally:
    conn.close()


