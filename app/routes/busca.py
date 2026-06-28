from fastapi import APIRouter, Depends
from typing import List, Optional, Union
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.cruds.busca import buscar_trabalhadores_servicos
from app.schemas.busca import BuscaResponse

router = APIRouter(prefix="/busca", tags=["Busca geral de serviços e trabalhadores"])

@router.get("/", response_model=List[BuscaResponse])
def buscar(
    nome_trabalhador: Optional[str] = None,
    nome_servico: Optional[str] = None,
    categoria: Optional[Union[int, str]] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """Retorna trabalhadores (usuários) que oferecem serviços que satisfazem os filtros.
    
    Os filtros são opcionais e são combinados com **AND**.
    """
    # Normaliza parâmetros vazios ("", None) para None
    categoria = categoria if (categoria is not None and str(categoria).strip() != "") else None
    nome_trabalhador = nome_trabalhador if (nome_trabalhador is not None and str(nome_trabalhador).strip() != "") else None
    nome_servico = nome_servico if (nome_servico is not None and str(nome_servico).strip() != "") else None
    return buscar_trabalhadores_servicos(
        db,
        nome_trabalhador=nome_trabalhador,
        nome_servico=nome_servico,
        categoria=categoria,
        skip=skip,
        limit=limit,
    )
