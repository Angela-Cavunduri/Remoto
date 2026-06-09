#!/bin/bash
# Aplicar migrações pendentes antes de arrancar o servidor
echo "A aplicar migrações da base de dados..."
alembic upgrade head

# Arrancar o servidor FastAPI
echo "A iniciar o servidor..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
