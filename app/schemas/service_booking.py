from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ServiceBookingCreate(BaseModel):
    id_servico: int
    data_agendada: datetime
    mensagem: Optional[str] = None
    preco_acordado: Optional[float] = None

class ServiceBookingStatusUpdate(BaseModel):
    status: str

class ServiceBookingResponse(BaseModel):
    id_pedido: int
    id_servico: int
    id_cliente: int
    id_prestador: int
    data_agendada: datetime
    mensagem: Optional[str]
    preco_acordado: Optional[float]
    status: str
    data_criacao: datetime

    class Config:
        from_attributes = True
