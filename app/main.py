from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
import cloudinary

# Configuração do Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Importação direta das rotas
from app.database.connection import engine, Base
from app.models import (
    user, servico, category, company, denuncia, exchangeOffer,
    message, review, transfer, user_sigle, service_booking
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
# Debug route import removed per user request
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
    service_booking,
    busca,
)

app = FastAPI(
    title="Troca Fácil API",
    description="Backend do sistema Troca Fácil",
    version="1.0.0"
)

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = exc.errors()
    msg = "Erro de preenchimento. Verifique os campos."
    if errors:
        campo = str(errors[0].get('loc', [''])[-1])
        msg_erro = errors[0].get('msg', 'inválido')
        msg = f"Erro no campo '{campo}': {msg_erro}"
    return JSONResponse(status_code=422, content={"detail": msg})

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
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import os

# Ensure upload directory exists on startup
# Garantir que a pasta de uploads de perfil exista (já está criada acima)
upload_dir = os.path.join('app', 'static', 'uploads', 'perfil')
os.makedirs(upload_dir, exist_ok=True)

# --- Startup event: corrigir caminhos de foto que não começam com '/' ---
@app.on_event("startup")
def fix_foto_paths():
    from app.database.connection import SessionLocal
    from app.models.user import Usuario
    db = SessionLocal()
    try:
        # Selecionar utilizadores cujo caminho não começa com '/static'
        usuarios = db.query(Usuario).all()
        for user in usuarios:
            if user.foto_perfil:
                nome_ficheiro = user.foto_perfil.split("/")[-1]
                user.foto_perfil = f"/static/uploads/perfil/{nome_ficheiro}"
                db.add(user)
        db.commit()
    finally:
        db.close()



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
app.include_router(cleanup_router)
app.include_router(service_booking.router)
app.include_router(profile_photos_router, prefix="/profile")
app.include_router(busca.router)
# app.include_router(debug_collation_router)  # debug route inclusion removed per request
@app.get("/")
def root():
    return {"message": "Backend do Troca Fácil está a funcionar"}

# ENDPOINT TEMPORÁRIO DE ADMIN – corrige caminhos de foto no BD
@app.get("/admin/fix-foto-paths")
def admin_fix_foto_paths():
    """Chama a função de correção de caminhos de foto."""
    fix_foto_paths()
    return {"status": "caminhos de foto corrigidos"}

@app.get("/admin/organize-categories")
def admin_organize_categories():
    from app.database.connection import engine
    from sqlalchemy import text
    queries = [
        "UPDATE category SET nome = 'Tecnologia e Informática' WHERE id_category = 1;",
        "UPDATE servico SET id_category = 1 WHERE id_category IN (2, 6, 16, 18);",
        "UPDATE category SET nome = 'Reparações e Manutenção' WHERE id_category = 3;",
        "UPDATE servico SET id_category = 3 WHERE id_category IN (4, 5, 9, 11);",
        "UPDATE category SET nome = 'Limpeza e Organização' WHERE id_category = 7;",
        "UPDATE servico SET id_category = 7 WHERE id_category IN (19);",
        "UPDATE category SET nome = 'Educação e Aulas Particulares' WHERE id_category = 8;",
        "UPDATE category SET nome = 'Casa e Jardinagem' WHERE id_category = 12;",
        "UPDATE category SET nome = 'Fotografia e Vídeo' WHERE id_category = 10;",
        "UPDATE category SET nome = 'Cuidados Infantis' WHERE id_category = 17;",
        "UPDATE category SET nome = 'Consultoria e Negócios' WHERE id_category = 15;",
        "UPDATE category SET nome = 'Saúde, Bem-estar e Fitness' WHERE id_category = 14;",
        "UPDATE category SET nome = 'Moda, Beleza e Estética' WHERE id_category = 13;",
        "UPDATE category SET nome = 'Design e Criatividade' WHERE id_category = 2;",
        "UPDATE category SET nome = 'Transporte e Mudanças' WHERE id_category = 4;",
        "UPDATE category SET nome = 'Cuidados a Idosos' WHERE id_category = 5;",
        "UPDATE category SET nome = 'Cuidados com Animais' WHERE id_category = 6;",
        "UPDATE category SET nome = 'Alimentação e Catering' WHERE id_category = 9;",
        "UPDATE category SET nome = 'Música e Entretenimento' WHERE id_category = 11;",
        "UPDATE category SET nome = 'Entregas e Recados' WHERE id_category = 16;",
        "UPDATE category SET nome = 'Escrita, Tradução e Revisão de Textos' WHERE id_category = 18;",
        "DELETE FROM category WHERE id_category IN (19);"
    ]
    try:
        with engine.begin() as conn:
            for q in queries:
                conn.execute(text(q))
        return {"status": "Categorias reorganizadas com sucesso! A base de dados de produção está limpa."}
    except Exception as e:
        return {"error": str(e)}

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

