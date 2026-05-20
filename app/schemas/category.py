from pydantic import BaseModel
from typing import Optional

class CategoryCreate(BaseModel):
    nome:str

class CategoryResponse(BaseModel):
    id_category:int
    nome:str

    class Config:
        from_attributes=True