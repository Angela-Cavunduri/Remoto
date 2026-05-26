from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioCreate(BaseModel):
    nome:str
    email:EmailStr
    palavra_pass:str
    endereco:str

class UsuarioNomeResponse(BaseModel):
    nome: str

    class Config:
        from_attributes = True

class UsuarioRankingResponse(BaseModel):
    nome: str
    foto_perfil: Optional[str] = None
    rating_media: int
    is_dangerous: bool = False
    total_trocas: int = 0
    total_prestacoes: int = 0

    class Config:
        from_attributes = True

class UsuarioResponse(BaseModel):
    id_usuario:int
    nome:str
    endereco:str
    email:EmailStr
    foto_perfil: Optional[str] = None
    rating_media: int = 0
    is_dangerous: bool = False

    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    palavra_pass:str
    email:EmailStr

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None
    endereco: Optional[str] = None

    class Config:
        from_attributes = True

class UsuarioVerificar(BaseModel):
    email: EmailStr
    codigo: str

class UsuarioNifCreate(BaseModel):
    nif: str
    email: EmailStr
    palavra_pass: str

class UsuarioReenviarCodigo(BaseModel):
    email: EmailStr
