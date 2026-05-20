from pydantic import BaseModel, Field
from datetime import datetime


class DenunciaCreate(BaseModel):
    id_denunciado: int
    comentario: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Explique detalhadamente o que aconteceu com esta conta."
    )


class DenunciaResponse(BaseModel):
    id_denuncia: int
    id_denunciante: int
    id_denunciado: int
    comentario: str
    data_denuncia: datetime

    class Config:
        from_attributes = True
