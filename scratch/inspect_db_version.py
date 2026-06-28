import os
from sqlalchemy import text
from app.database.connection import engine

def print_info():
    with engine.begin() as conn:
        # MySQL version
        version = conn.execute(text('SELECT VERSION()')).scalar()
        print('MySQL version:', version)
        # List tables of interest
        for table in ['usuario', 'servico']:
            print(f'\nTable: {table}')
            cols = conn.execute(text(f"SELECT COLUMN_NAME, CHARACTER_SET_NAME, COLLATION_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table}'")).fetchall()
            for col in cols:
                print(f"  {col[0]}: charset={col[1]}, collation={col[2]}")

if __name__ == '__main__':
    print_info()
