from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewCreate(BaseModel):
    id_exchange_offer: int
    id_avaliado: int
    avaliacao: int = Field(..., ge=1, le=5)
    conteudo: Optional[str] = None

class ReviewResponse(BaseModel):
    id_review: int
    id_exchange_offer: int
    id_avaliado: int
    id_avaliador: int
    avaliacao: int
    conteudo: Optional[str]
    data_avaliacao: datetime

    class Config:
        from_attributes = True
