from pydantic import BaseModel
from typing import Optional
from app.schemas.category import CategoryResponse

class UserShortResponse(BaseModel):
    nome: str
    rating_media: int

    class Config:
        from_attributes = True

class ServicoCreate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    id_category: Optional[int] = None
    status: Optional[str] = "ativo"


class ServicoResponse(BaseModel):
    id_servico:int
    descricao:Optional[str]
    id_user:int
    nome:str
    category:CategoryResponse
    usuario: UserShortResponse

    class Config:
        from_attributes = True
    
class ServicoUpdate(BaseModel):
    descricao: Optional[str]=None
    id_category: Optional[int]=None
    status: Optional[str]=None
    
    class Config:
        from_attributes = True