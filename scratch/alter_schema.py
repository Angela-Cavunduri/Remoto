import os
from sqlalchemy import create_engine, text

# Load env vars (use defaults if missing)
user = os.getenv('MYSQL_USER', 'root')
password = os.getenv('MYSQL_PASSWORD', 'root')
host = os.getenv('MYSQL_HOST', 'localhost')
db = os.getenv('MYSQL_DB', 'troca_facil')

engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{db}')

with engine.begin() as conn:
    # Ensure servico.data_criacao NOT NULL with default CURRENT_TIMESTAMP
    # Update NULL data_criacao to current timestamp before altering
    conn.execute(text("UPDATE servico SET data_criacao = CURRENT_TIMESTAMP WHERE data_criacao IS NULL"))
    conn.execute(text("ALTER TABLE servico MODIFY data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"))
    # For transfer columns, set NOT NULL. First update any NULLs to sensible defaults
    conn.execute(text("UPDATE transfer SET id_user = 0 WHERE id_user IS NULL"))
    conn.execute(text("UPDATE transfer SET id_exchangeoffer = 0 WHERE id_exchangeoffer IS NULL"))
    conn.execute(text("UPDATE transfer SET data_datroca = CURRENT_TIMESTAMP WHERE data_datroca IS NULL"))
    conn.execute(text("UPDATE transfer SET estados = '' WHERE estados IS NULL"))
    conn.execute(text("UPDATE transfer SET id_usuario_solicitante = 0 WHERE id_usuario_solicitante IS NULL"))
    # Alter columns to NOT NULL
    conn.execute(text("ALTER TABLE transfer MODIFY id_user INTEGER NOT NULL"))
    conn.execute(text("ALTER TABLE transfer MODIFY id_exchangeoffer INTEGER NOT NULL"))
    conn.execute(text("ALTER TABLE transfer MODIFY data_datroca DATETIME NOT NULL"))
    conn.execute(text("ALTER TABLE transfer MODIFY estados VARCHAR(50) NOT NULL"))
    conn.execute(text("ALTER TABLE transfer MODIFY id_usuario_solicitante INTEGER NOT NULL"))
print('Schema alteration completed.')
