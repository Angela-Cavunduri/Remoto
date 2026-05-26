from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.models.user import Usuario
from app.schemas.service_booking import ServiceBookingCreate, ServiceBookingResponse, ServiceBookingStatusUpdate
from app.cruds.service_booking import criar_pedido, listar_pedidos_cliente, listar_trabalhos_prestador, atualizar_status_pedido
from app.services.security import get_current_user

router = APIRouter(
    prefix="/prestacao",
    tags=["Prestação de Serviços"]
)

@router.post("/", response_model=ServiceBookingResponse)
def contratar_servico(
    pedido: ServiceBookingCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    try:
        return criar_pedido(db, pedido, current_user.id_usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/meus-pedidos", response_model=List[ServiceBookingResponse])
def ver_meus_pedidos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Ver os serviços que EU contratei a outros"""
    return listar_pedidos_cliente(db, current_user.id_usuario)

@router.get("/meus-trabalhos", response_model=List[ServiceBookingResponse])
def ver_meus_trabalhos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Ver os pedidos que outros fizeram aos MEUS serviços"""
    return listar_trabalhos_prestador(db, current_user.id_usuario)

@router.patch("/{id_pedido}/status", response_model=ServiceBookingResponse)
def atualizar_estado_pedido(
    id_pedido: int,
    status_update: ServiceBookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    try:
        return atualizar_status_pedido(db, id_pedido, current_user.id_usuario, status_update.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
