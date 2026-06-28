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
    db: Session = Depends(get_db)
):
    """Retorna usuários cadastrados ou filtra por nome se fornecido."""
    if nome:
        return buscar_por_nome(db, nome)
    return buscar_todos(db)
