from sqlalchemy import create_engine #cocneção com o banco de dados
from sqlalchemy.ext.declarative import declarative_base #permite criar as tabelas usando a línguagem do python
from dotenv import load_dotenv #lê os arquivos env (lê as regras)
from sqlalchemy.orm import sessionmaker
import os #pega as variaveis do sistema
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER") #quem és (usuário)
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD") #senha
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost") #onde fica a casa (host)
MYSQL_DB = os.getenv("MYSQL_DB") #qual casa exatamente (nome do banco)

DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker( #um “canal” por onde entram e saem dados
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base = declarative_base() #Cria a base para todas as tabelas
