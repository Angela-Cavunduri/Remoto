from dotenv import load_dotenv
load_dotenv()

import sys
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

# -------------------------------------------------
# Garantir que a raiz do projeto está no sys.path
# -------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# -------------------------------------------------
# Configuração do Alembic
# -------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------------------------
# Importar engine e Base
# -------------------------------------------------
from app.database.connection import engine, Base

# -------------------------------------------------
# Importar TODOS os modelos (muito importante!)
# -------------------------------------------------
from app.models.user import Usuario
from app.models.user_sigle import UserSigle
from app.models.company import Company
from app.models.message import Message
from app.models.review import Review
from app.models.transfer import Transfer
from app.models.exchangeOffer import ExchangeOffer
from app.models.servico import Servico
from app.models.category import Category

# -------------------------------------------------
# Metadata usada pelo Alembic
# -------------------------------------------------
target_metadata = Base.metadata

# -------------------------------------------------
# Migrations OFFLINE
# -------------------------------------------------
def run_migrations_offline():
    context.configure(
        url=str(engine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# -------------------------------------------------
# Migrations ONLINE (USANDO O ENGINE DO PROJETO)
# -------------------------------------------------
def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            poolclass=pool.NullPool,
        )

        with context.begin_transaction():
            context.run_migrations()

# -------------------------------------------------
# Executar
# -------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
