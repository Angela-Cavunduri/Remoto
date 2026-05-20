from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    id_send: int
    id_receiver: int
    conteudo: str

class MessageResponse(BaseModel):
    id_message: int
    id_send: int
    id_receiver: int
    conteudo: str
    data_message: Optional[datetime]

    class Config:
        from_attributes = True