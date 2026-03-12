"""
Fix database schema - Add missing columns for farmer products feature
"""
import sys
sys.path.insert(0, '.')

from sqlalchemy import inspect, text
from app.db.database import engine, Base

def fix_products_table():
    """Add missing columns to products table"""
    inspector = inspect(engine)
    
    # Check existing columns
    columns = [col['name'] for col in inspector.get_columns('products')]
    print("Current columns in products table:")
    print(columns)
    
    # Get database type
    db_url = str(engine.url)
    is_sqlite = 'sqlite' in db_url
    
    # Get connection
    with engine.begin() as connection:
        # Check if columns exist
        missing_columns = []
        
        if 'farmer_id' not in columns:
            missing_columns.append('farmer_id')
            print("\n❌ Missing column: farmer_id")
            
        if 'product_source' not in columns:
            missing_columns.append('product_source')
            print("❌ Missing column: product_source")
        
        if not missing_columns:
            print("\n✅ All required columns already exist!")
            return
        
        print(f"\n🔧 Adding missing columns: {missing_columns}")
        print(f"Database type: {'SQLite' if is_sqlite else 'PostgreSQL/MySQL'}")
        
        # Add farmer_id column
        if 'farmer_id' not in columns:
            try:
                if is_sqlite:
                    # SQLite: Simple column addition without foreign key constraint
                    connection.execute(text('ALTER TABLE products ADD COLUMN farmer_id INTEGER'))
                    print("✅ Added farmer_id column (SQLite - foreign key not added, must be managed at app level)")
                else:
                    # PostgreSQL/MySQL: Add with foreign key
                    connection.execute(text('ALTER TABLE products ADD COLUMN farmer_id INTEGER'))
                    connection.execute(text('ALTER TABLE products ADD CONSTRAINT fk_products_farmer_id FOREIGN KEY(farmer_id) REFERENCES users(id)'))
                    print("✅ Added farmer_id column with foreign key constraint")
            except Exception as e:
                print(f"⚠️  Could not add farmer_id: {e}")
        
        # Add product_source column (if not already added)
        if 'product_source' not in columns:
            try:
                connection.execute(text("ALTER TABLE products ADD COLUMN product_source VARCHAR(50) DEFAULT 'supplier'"))
                print("✅ Added product_source column")
            except Exception as e:
                print(f"⚠️  Could not add product_source: {e}")
        
        print("\n✅ Database schema updated successfully!")

if __name__ == '__main__':
    try:
        print("Checking and fixing products table schema...")
        print("=" * 50)
        fix_products_table()
        print("=" * 50)
        print("Done!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
