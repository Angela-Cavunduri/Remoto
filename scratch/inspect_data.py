import os
from dotenv import load_dotenv
load_dotenv(override=True)
from sqlalchemy import create_engine, text

user = os.getenv('MYSQL_USER')
pwd = os.getenv('MYSQL_PASSWORD')
host = os.getenv('MYSQL_HOST')
dbname = os.getenv('MYSQL_DB')

engine = create_engine(f'mysql+mysqlconnector://{user}:{pwd}@{host}/{dbname}', echo=False)

with engine.connect() as conn:
    # fetch some users
    rows = conn.execute(text('SELECT id_usuario, nome, email FROM usuario LIMIT 10')).fetchall()
    print('usuario rows:', rows)
    # fetch some services
    serv = conn.execute(text('SELECT id_servico, nome, descricao FROM servico LIMIT 10')).fetchall()
    print('servico rows:', serv)
