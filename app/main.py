from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Importação direta das rotas
from app.database.connection import engine, Base
from app.models import (
    user, servico, category, company, denuncia, exchangeOffer, 
    message, paymentExchange, review, transfer, user_sigle, service_booking
)

# Criar todas as tabelas na base de dados se não existirem
# Attempt to create tables; ignore errors if DB is unreachable
try:
    from sqlalchemy import text
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE transfer ADD COLUMN id_usuario_solicitante INT NULL;"))
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE transfer ADD CONSTRAINT fk_transfer_usuario_solicitante FOREIGN KEY (id_usuario_solicitante) REFERENCES usuario(id_usuario);"))
        except Exception:
            pass

    Base.metadata.create_all(bind=engine)
except Exception as e:
    # Log the error but allow the app to start (useful for dev when DB is offline)
    import logging
    logging.getLogger(__name__).warning("Database tables not created: %s", e)

from app.routes.profile_photos import router as profile_photos_router
from app.routes.cleanup_images import router as cleanup_router
from app.routes import (
    usuario, 
    auth, 
    servico as servico_router, 
    category, 
    dashboard, 
    exchangeoffer, 
    message, 
    transfer,
    review,
    payment,
    subscription,
    service_booking,
    busca,
)

app = FastAPI(
    title="Troca Fácil API",
    description="Backend do sistema Troca Fácil",
    version="1.0.0"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ], 
    allow_origin_regex="https://.*", # Permite qualquer domínio em Produção (Vercel, Netlify, Render)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import os

# Ensure upload directory exists on startup
upload_dir = os.path.join('app', 'static', 'uploads', 'perfil')
os.makedirs(upload_dir, exist_ok=True)

# Serve static files (profile photos, etc.)
app.mount(
    "/static",
    StaticFiles(directory=os.path.join('app', 'static')),
    name="static",
)


# Inclusão das rotas no servidor
app.include_router(usuario.router)
app.include_router(auth.router)
app.include_router(servico_router.router)
app.include_router(category.router)
app.include_router(dashboard.router)
app.include_router(exchangeoffer.router)
app.include_router(message.router)
app.include_router(transfer.router)
app.include_router(review.router)
app.include_router(payment.router)
app.include_router(subscription.router)
app.include_router(cleanup_router)
app.include_router(service_booking.router)
app.include_router(profile_photos_router, prefix="/profile")

@app.get("/")
def root():
    return {"message": "Backend do Troca Fácil está a funcionar"}

@app.get("/run-alembic")
def run_alembic():
    import subprocess
    from app.database.connection import engine
    from sqlalchemy import text
    try:
        # Tenta criar a coluna que está a faltar caso o Alembic esteja preso
        with engine.begin() as conn:
            try:
                conn.execute(text("ALTER TABLE transfer ADD COLUMN id_usuario_solicitante INT NULL;"))
            except Exception as e:
                pass # Ignora se a coluna já existir
                
            try:
                conn.execute(text("ALTER TABLE transfer ADD CONSTRAINT fk_transfer_usuario_solicitante FOREIGN KEY (id_usuario_solicitante) REFERENCES usuario(id_usuario);"))
            except Exception as e:
                pass # Ignora se a chave já existir
                
        # Agora corre o alembic upgrade head
        result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True, check=True)
        return {"success": True, "output": result.stdout, "message": "Banco de dados corrigido e atualizado com sucesso!"}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr}

