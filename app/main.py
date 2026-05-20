from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Importação direta das rotas
from app.routes import (
    usuario, 
    auth, 
    servico, 
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
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Servir arquivos estáticos (fotos de perfil, etc)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Inclusão das rotas no servidor
app.include_router(usuario.router)
app.include_router(auth.router)
app.include_router(servico.router)
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

@app.get("/download/android", tags=["Download"])
def download_android_app():
    caminho_apk = "app/static/TrocaFacil.apk"
    if os.path.exists(caminho_apk):
        return FileResponse(
            path=caminho_apk, 
            filename="TrocaFacil_Oficial.apk", 
            media_type="application/vnd.android.package-archive"
        )
    else:
        raise HTTPException(
            status_code=404, 
            detail="O ficheiro da App ainda não foi enviado para o servidor."
        )
