import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(override=True)
user = os.getenv('MYSQL_USER')
pwd = os.getenv('MYSQL_PASSWORD')
host = os.getenv('MYSQL_HOST')
dbname = os.getenv('MYSQL_DB')

engine = create_engine(f'mysql+mysqlconnector://{user}:{pwd}@{host}/{dbname}', echo=False)

with engine.connect() as conn:
    # raw query similar to buscar_trabalhadores_servicos filters for nome_trabalhador
    sql = text("""
        SELECT id_usuario, nome FROM usuario
        WHERE lower(nome) LIKE lower(:p1) OR lower(nome) LIKE lower(:p2)
        LIMIT 10
    """)
    params = {'p1': '%angela cavunduri%', 'p2': '%Angela Cavunduri%'}
    rows = conn.execute(sql, params).fetchall()
    print('matching rows:', rows)
"
