import logging
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.cruds.busca import buscar_todos, buscar_por_nome
from app.schemas.usuario import UsuarioNomeResponse

router = APIRouter(prefix="/busca", tags=["Busca de usuários"])

@router.get("/", response_model=List[UsuarioNomeResponse])
def buscar_usuarios(
    nome: Optional[str] = Query(None, description="Nome do usuário a buscar (case-insensitive)"),
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=500, description="Limite máximo de resultados"),
    db: Session = Depends(get_db)
):
    """Retorna usuários cadastrados ou filtra por nome se fornecido, com paginação."""
    logging.info(f"Busca de usuários chamada com nome={nome}, skip={skip}, limit={limit}")
    if nome:
        return buscar_por_nome(db, nome, skip=skip, limit=limit)
    return buscar_todos(db, skip=skip, limit=limit)
