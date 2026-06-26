from pydantic import BaseModel
from typing import Optional

class ExchangeCreate(BaseModel):
    id_servico_oferecido: int
    id_servico_desejado: int
    mensagem: Optional[str] = None

class ServicoSimples(BaseModel):
    id_servico: int
    nome: str
    class Config: from_attributes = True

class UsuarioSimples(BaseModel):
    id_usuario: int
    nome: str
    is_dangerous: bool = False
    rating_media: int = 0
    class Config: from_attributes = True

class ExchangeResponse(BaseModel):
    id_offer: int
    id_user: int
    id_servico_oferecido: int
    id_servico_desejado: int
    id_usuario_solicitante: int
    status: str
    mensagem: Optional[str]

    usuario: Optional[UsuarioSimples] = None
    trocas_solicitadas: Optional[UsuarioSimples] = None
    servico_oferecido: Optional[ServicoSimples] = None
    servico_desejado: Optional[ServicoSimples] = None

    class Config:
        from_attributes = True

class ExchangeUpdate(BaseModel):
    status:str
    
    class Config:
        from_attributes = True