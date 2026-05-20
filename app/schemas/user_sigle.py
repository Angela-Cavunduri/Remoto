from pydantic import BaseModel

class UserSingleCreate(BaseModel):
    numero_bi: int
    usuario_id: int

class UserSingleResponse(BaseModel):
    id_user: int
    numero_bi: int
    usuario_id: int

    class Config:
        from_attributes = True