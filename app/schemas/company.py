from pydantic import BaseModel


class CompanyBase(BaseModel):
    nif_company: str
    nome_empresa: str
    tipo_empresa: str
    usuario_id: int

class CompanyCreate(CompanyBase):
    pass

class CompanyRead(CompanyBase):
    id_company: int

    class Config:
        from_attributes = True