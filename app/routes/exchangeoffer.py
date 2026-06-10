from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.cruds.exchange_offer import create_exchange_offer, aceitar_oferta, recusar_oferta, concluir_oferta
from app.schemas.exchangeoff import ExchangeCreate, ExchangeResponse
from app.cruds.usuario import get_trocas_usuario
from app.services.security import get_current_user

router = APIRouter(prefix="/trocas", tags=["Trocas"])

@router.get("/", response_model=List[ExchangeResponse])
def listar_trocas(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_trocas_usuario(db, user.id_usuario)

@router.post("/", response_model=ExchangeResponse)
def criar(oferta: ExchangeCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return create_exchange_offer(
        db,
        oferta.id_servico_oferecido,
        oferta.id_servico_desejado,
        user.id_usuario,
        oferta.mensagem,
        background_tasks
    )

@router.put("/{id}/aceitar", response_model=ExchangeResponse)
def aceitar(id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return aceitar_oferta(db, id, user.id_usuario, background_tasks)

@router.put("/{id}/recusar", response_model=ExchangeResponse)
def recusar(id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return recusar_oferta(db, id, user.id_usuario, background_tasks)

@router.put("/{id}/concluir", response_model=ExchangeResponse)
def concluir(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return concluir_oferta(db, id, user.id_usuario)