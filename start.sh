#!/bin/bash
set -e

echo "A sincronizar versão do Alembic com a base de dados..."

# stamp head: regista que a BD já está na versão mais recente
# sem tentar correr nenhuma migração SQL.
# Isto resolve o erro "Table already exists" quando as tabelas
# já foram criadas diretamente (Base.metadata.create_all).
.venv/bin/alembic stamp head

echo "A iniciar o servidor..."
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
