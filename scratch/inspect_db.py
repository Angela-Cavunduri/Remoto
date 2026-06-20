import os
from sqlalchemy import create_engine, inspect

# Load DB connection variables (adjust if needed)
user = os.getenv('MYSQL_USER', 'root')
password = os.getenv('MYSQL_PASSWORD', 'root')
host = os.getenv('MYSQL_HOST', 'localhost')
dbname = os.getenv('MYSQL_DB', 'troca_facil')

engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{dbname}')
inspector = inspect(engine)

def print_table_info(table_name):
    print(f'\nTable: {table_name}')
    columns = inspector.get_columns(table_name)
    for col in columns:
        print(f"  {col['name']}: type={col['type']}, nullable={col['nullable']}, default={col.get('default')} ")

for tbl in ['transfer', 'servico']:
    print_table_info(tbl)
