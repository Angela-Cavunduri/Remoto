from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Importação direta das rotas
from app.database.connection import engine, Base
from app.models import (
    user, servico, category, company, denuncia, exchangeOffer, 
    message, paymentExchange, review, transfer, user_sigle
)

# Criar todas as tabelas na base de dados se não existirem
Base.metadata.create_all(bind=engine)

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
    denuncia
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
# Servir arquivos estáticos (fotos de perfil, etc)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

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
app.include_router(denuncia.router)

@app.get("/")
def root():
    return {"message": "Backend do Troca Fácil está a funcionar"}
