from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.schemas.transfer import TransferResponse
from app.cruds.transfer import (
    get_user_transfers,
)
from app.services.security import get_current_user
from app.models.user import Usuario

router = APIRouter(
    prefix="/recibos",
    tags=["Recibos"]
)

@router.get("/minhas", response_model=List[TransferResponse])
def listar_meus_recibos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista todos os recibos do utilizador autenticado (criados automaticamente ao concluir trocas)."""
    return get_user_transfers(db, current_user.id_usuario)


