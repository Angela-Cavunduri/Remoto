from fastapi import FastAPI
from app.routes.usuario import router as usuario_router
from app.models.user import Usuario
from app.models.category import Category
from app.models.company import Company
from app.models.exchangeOffer import ExchangeOffer
from app.models.message import Message
from app.models.review import Review
from app.models.servico import Servico
from app.models.transfer import Transfer
from app.models.user_sigle import UserSigle



app = FastAPI(
    title="Troca Fácil API",
    description="Backend do sistema Troca Fácil",
    version="1.0.0"
)
app.include_router(usuario_router)

@app.get("/")
def root():
    return {"message": "Backend do Troca Fácil está a funcionar"}
