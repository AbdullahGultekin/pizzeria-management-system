"""
Script to import menu data from menu.json into the database.
"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, init_db
from app.models.menu import MenuCategory, MenuItem
from sqlalchemy.exc import IntegrityError

def load_menu_json(file_path: str = "../../menu.json") -> dict:
    """Load menu data from JSON file."""
    # Try multiple paths
    possible_paths = [
        file_path,
        os.path.join(os.path.dirname(__file__), file_path),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "menu.json"),
        "../../menu.json",
        "../menu.json",
        "menu.json",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Loading menu from: {path}")
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    raise FileNotFoundError(f"Could not find menu.json in any of these locations: {possible_paths}")

def import_menu():
    """Import menu data into database."""
    print("🚀 Starting menu import...")
    
    # Initialize database
    init_db()
    
    # Load menu data
    try:
        menu_data = load_menu_json()
        print(f"✅ Loaded menu.json with {len(menu_data)} top-level keys")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return
    
    db = SessionLocal()
    
    try:
        # Track created categories
        categories_map = {}
        item_count = 0
        category_count = 0
        
        # Process each category in menu.json
        for category_name, items in menu_data.items():
            if not isinstance(items, list):
                continue
            
            # Create or get category
            category = db.query(MenuCategory).filter(MenuCategory.naam == category_name).first()
            if not category:
                category = MenuCategory(
                    naam=category_name,
                    volgorde=len(categories_map)
                )
                db.add(category)
                db.flush()
                category_count += 1
                print(f"  ✅ Created category: {category_name}")
            else:
                print(f"  ℹ️  Category already exists: {category_name}")
            
            categories_map[category_name] = category
            
            # Add items in this category
            for item_data in items:
                if isinstance(item_data, dict):
                    item_name = item_data.get('naam', '')
                    item_price = item_data.get('prijs', 0)
                    item_desc = item_data.get('desc', '') or item_data.get('beschrijving', '')
                    
                    if not item_name or item_price == 0:
                        continue
                    
                    # Check if item already exists
                    existing = db.query(MenuItem).filter(
                        MenuItem.naam == item_name,
                        MenuItem.categorie == category_name
                    ).first()
                    
                    if not existing:
                        menu_item = MenuItem(
                            naam=item_name,
                            categorie=category_name,
                            prijs=float(item_price),
                            beschrijving=item_desc,
                            beschikbaar=1,
                            volgorde=item_count
                        )
                        db.add(menu_item)
                        item_count += 1
                        print(f"    ✅ Added: {item_name} (€{item_price})")
                    else:
                        # Update existing item with new data from menu.json
                        existing.prijs = float(item_price)
                        existing.beschrijving = item_desc
                        existing.beschikbaar = 1
                        print(f"    🔄 Updated: {item_name} (€{item_price}, desc: {item_desc})")
        
        db.commit()
        print(f"\n✅ Import complete!")
        print(f"   Categories: {category_count} created")
        print(f"   Items: {item_count} added")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error importing menu: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import_menu()


