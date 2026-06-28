import os
from sqlalchemy import create_engine, text

# Carrega variáveis .env (já carregado pelo app)
user = os.getenv('MYSQL_USER')
pwd = os.getenv('MYSQL_PASSWORD')
host = os.getenv('MYSQL_HOST')
dbname = os.getenv('MYSQL_DB')

engine = create_engine(f'mysql+mysqlconnector://{user}:{pwd}@{host}/{dbname}', echo=False)

with engine.connect() as conn:
    for tbl in ['usuario', 'servico']:
        result = conn.execute(text(f'SELECT COUNT(*) FROM {tbl}'))
        print(tbl, result.scalar())
        # Mostrar algumas linhas de exemplo
        rows = conn.execute(text(f'SELECT * FROM {tbl} LIMIT 5')).fetchall()
        print('sample rows', rows)
