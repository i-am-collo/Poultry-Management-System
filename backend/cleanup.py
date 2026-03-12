from sqlalchemy import text
from app.db.database import engine

try:
    with engine.begin() as conn:
        conn.execute(text('DROP TABLE IF EXISTS products_new'))
    print('✅ Cleaned up products_new table')
except Exception as e:
    print(f'Error: {e}')
