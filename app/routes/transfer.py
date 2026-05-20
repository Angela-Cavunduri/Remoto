from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.schemas.transfer import TransferCreate, TransferResponse, TransferUpdate
from app.cruds.transfer import (
    create_transfer,
    get_user_transfers,
    get_transfer_by_id,
    update_transfer_status,
    deletar_transfer
)
from app.services.security import get_current_user
from app.models.user import Usuario

router = APIRouter(
    prefix="/recibos",
    tags=["Recibos"]
)

@router.post("/", response_model=TransferResponse)
def criar_transferencia(
    transfer: TransferCreate, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    try:
        return create_transfer(db, transfer, current_user.id_usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/minhas", response_model=List[TransferResponse])
def listar_minhas_transferencias(
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    return get_user_transfers(db, current_user.id_usuario)

@router.get("/{id}", response_model=TransferResponse)
def obter_transferencia(
    id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    transfer = get_transfer_by_id(db, id)
    if not transfer:
        raise HTTPException(status_code=404, detail="Transferência não encontrada")
    return transfer

@router.patch("/{id}/estado", response_model=TransferResponse)
def alterar_estado_transferencia(
    id: int, 
    dados: TransferUpdate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    try:
        return update_transfer_status(db, id, dados.estados, current_user.id_usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
def apagar_transferencia(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    sucesso = deletar_transfer(db, id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Transferência não encontrada")
    return {"message": "Recibo apagado com sucesso"}
