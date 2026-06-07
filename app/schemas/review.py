from pydantic import BaseModel, Field
from typing import Optional, List
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

# Schemas para o histórico de avaliações

class ReviewerInfo(BaseModel):
    id_usuario: int
    nome: str
    foto_perfil: Optional[str] = None
    
    class Config:
        from_attributes = True

class ReviewDetailResponse(BaseModel):
    id_review: int
    avaliacao: int
    conteudo: Optional[str]
    data_avaliacao: datetime
    avaliador: ReviewerInfo
    
    class Config:
        from_attributes = True

class UsuarioReviewsHistoryResponse(BaseModel):
    total_avaliacoes: int
    media: float
    avaliacoes: List[ReviewDetailResponse]

