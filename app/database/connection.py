from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carrega .env se existir, mas não falha se não houver
load_dotenv(override=True)

# Prioriza URL completa se fornecida (ex.: para cloud/Aiven)
CUSTOM_DATABASE_URL = os.getenv("DATABASE_URL")
if CUSTOM_DATABASE_URL:
    DATABASE_URL = CUSTOM_DATABASE_URL
else:
    # Variáveis essenciais (lançar erro claro caso faltem)
    MYSQL_USER = os.getenv("MYSQL_USER", "avnadmin!")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    missing = [var for var in ("MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DB") if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"As variáveis de ambiente {', '.join(missing)} são obrigatórias para conectar ao MySQL."
        )
    DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# Detecta se o host é um provedor cloud (ex.: Aiven) que requer SSL
is_cloud = MYSQL_HOST not in ("localhost", "127.0.0.1")

if is_cloud:
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"ssl_disabled": False},
        pool_recycle=300,
        pool_pre_ping=True,
    )
else:
    engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()
