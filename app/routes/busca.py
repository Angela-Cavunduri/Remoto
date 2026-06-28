from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import Usuario
from app.schemas.usuario import UsuarioNomeResponse

router = APIRouter(prefix="/busca", tags=["Busca de usuários"])

@router.get("/", response_model=List[UsuarioNomeResponse])
def buscar_usuarios(db: Session = Depends(get_db)):
    """Retorna todos os usuários cadastrados no banco de dados."""
    return db.query(Usuario).all()
