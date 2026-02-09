from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.cruds.usuario import create_usuario as create_usuario_db

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)

@router.post("/", response_model=UsuarioResponse)
def create_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return create_usuario_db(db, usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    pass

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def get_usuario(usuario_id: int, db: Session = Depends(get_db)):
    # aqui vai a lógica de buscar usuário
    pass
