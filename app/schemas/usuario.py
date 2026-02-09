from pydantic import BaseModel, EmailStr

class UsuarioCreate(BaseModel):
    nome:str
    email:EmailStr
    palavra_pass:str
    endereco:str

class UsuarioResponse(BaseModel):
    id_usuario:int
    nome:str
    endereco:str
    email:EmailStr

class UsuarioLogin(BaseModel):
    palavra_pass:str
    email:EmailStr

class Config:
    from_attributes = True
