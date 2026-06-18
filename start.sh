#!/bin/bash
# Aplicar migrações pendentes antes de arrancar o servidor
echo "A aplicar migrações da base de dados..."

# Usar o caminho do .venv onde o Render instala os pacotes
if [ -f ".venv/bin/alembic" ]; then
    .venv/bin/alembic upgrade head
elif command -v alembic &> /dev/null; then
    alembic upgrade head
else
    echo "AVISO: alembic não encontrado, a saltar migrações..."
fi

# Arrancar o servidor FastAPI
echo "A iniciar o servidor..."

if [ -f ".venv/bin/uvicorn" ]; then
    .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
elif command -v uvicorn &> /dev/null; then
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
else
    echo "ERRO: uvicorn não encontrado!"
    exit 1
fi
