from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TransferCreate(BaseModel):
    id_exchangeoffer: int
    estados: Optional[str] = "Pendente"

class TransferResponse(BaseModel):
    id_transfer: int
    id_user: int
    id_exchangeoffer: int
    data_datroca: Optional[datetime]
    estados: Optional[str]

    class Config:
        from_attributes = True

class TransferUpdate(BaseModel):
    estados: str

    class Config:
        from_attributes = True
