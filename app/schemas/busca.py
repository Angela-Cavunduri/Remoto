from pydantic import BaseModel
from typing import Optional

class BuscaResponse(BaseModel):
    id_usuario: int
    nome_usuario: str
    foto_perfil: Optional[str] = None
    id_servico: int
    nome_servico: str
    descricao: Optional[str] = None
    id_categoria: Optional[int] = None

    class Config:
        from_attributes = True
