"""
Fix supplier_id NOT NULL constraint in products table
SQLite doesn't support ALTER COLUMN, so we need to recreate the table
"""
import sys
sys.path.insert(0, '.')

from sqlalchemy import text, inspect
from app.db.database import engine
from datetime import datetime, timezone

def fix_supplier_id_constraint():
    """Fix the supplier_id NOT NULL constraint"""
    
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('products')]
    
    print("Checking supplier_id constraint...")
    print(f"Columns: {columns}")
    
    with engine.begin() as connection:
        # For SQLite, we need to recreate the table
        # Check current table schema
        result = connection.execute(text("PRAGMA table_info(products)"))
        
        rows = result.fetchall()
        print("\nCurrent products table schema:")
        for row in rows:
            col_id, col_name, col_type, notnull, default, pk = row
            null_str = "NOT NULL" if notnull else "NULL"
            print(f"  {col_name}: {col_type} ({null_str})")
        
        if len(rows) > 0:
            # Get the current timestamp for default values
            now = datetime.now(timezone.utc).isoformat()
            
            print("\n🔧 Recreating table with nullable supplier_id...")
            
            try:
                # Create temporary table with data
                connection.execute(text("""
                    CREATE TABLE products_new AS 
                    SELECT 
                        id,
                        supplier_id,
                        farmer_id,
                        product_source,
                        name,
                        category,
                        description,
                        product_image,
                        unit_price,
                        unit_of_measure,
                        stock_quantity,
                        is_active,
                        visible_to_farmers_only,
                        created_at,
                        updated_at
                    FROM products
                """))
                
                # Drop the old table
                connection.execute(text("DROP TABLE products"))
                
                # Recreate with correct schema
                connection.execute(text("""
                    CREATE TABLE products (
                        id INTEGER PRIMARY KEY,
                        supplier_id INTEGER REFERENCES users(id),
                        farmer_id INTEGER REFERENCES users(id),
                        product_source VARCHAR(50) DEFAULT 'supplier',
                        name VARCHAR(120) NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        description TEXT,
                        product_image VARCHAR(255) NOT NULL,
                        unit_price FLOAT NOT NULL,
                        unit_of_measure VARCHAR(30) NOT NULL DEFAULT 'unit',
                        stock_quantity INTEGER NOT NULL DEFAULT 0,
                        is_active BOOLEAN NOT NULL DEFAULT 1,
                        visible_to_farmers_only BOOLEAN NOT NULL DEFAULT 0,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Copy data back (SQLite will use DEFAULT for NULLs if needed)
                connection.execute(text("""
                    INSERT INTO products 
                    (id, supplier_id, farmer_id, product_source, name, category, 
                     description, product_image, unit_price, unit_of_measure, 
                     stock_quantity, is_active, visible_to_farmers_only, 
                     created_at, updated_at)
                    SELECT 
                        id, supplier_id, farmer_id, product_source, name, category, 
                        description, product_image, unit_price, unit_of_measure, 
                        stock_quantity, is_active, visible_to_farmers_only, 
                        COALESCE(created_at, datetime('now')),
                        COALESCE(updated_at, datetime('now'))
                    FROM products_new
                """))
                
                # Drop temporary table
                connection.execute(text("DROP TABLE products_new"))
                
                print("✅ supplier_id constraint fixed (table recreated)")
                
                # Verify the fix
                connection.execute(text("PRAGMA table_info(products)"))
                result = connection.execute(text("PRAGMA table_info(products)"))
                rows = result.fetchall()
                print("\n✅ New products table schema:")
                for row in rows:
                    col_id, col_name, col_type, notnull, default, pk = row
                    null_str = "NOT NULL" if notnull else "NULL"
                    print(f"  {col_name}: {col_type} ({null_str})")
                    
            except Exception as e:
                print(f"❌ Failed: {e}")
                raise

if __name__ == '__main__':
    try:
        print("Fixing product table schema...")
        print("=" * 50)
        fix_supplier_id_constraint()
        print("=" * 50)
        print("Done!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
