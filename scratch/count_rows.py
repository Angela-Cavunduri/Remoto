import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(override=True)
CUSTOM_DATABASE_URL = os.getenv('DATABASE_URL')
if CUSTOM_DATABASE_URL:
    db_url = CUSTOM_DATABASE_URL
else:
    user = os.getenv('MYSQL_USER')
    pwd = os.getenv('MYSQL_PASSWORD')
    db = os.getenv('MYSQL_DB')
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = os.getenv('MYSQL_PORT', '3306')
    db_url = f'mysql+mysqlconnector://{user}:{pwd}@{host}:{port}/{db}'

engine = create_engine(db_url, echo=False)
with engine.connect() as conn:
    for tbl in ['usuario', 'servico', 'category']:
        result = conn.execute(text(f'SELECT COUNT(*) FROM {tbl}'))
        print(tbl, result.scalar())
