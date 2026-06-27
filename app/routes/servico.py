from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.schemas.servico import ServicoCreate, ServicoResponse, ServicoUpdate
from app.cruds.servico import create_servico, get_servicos, get_servico_by_name, update_servico, delete_servico
from app.models.user import Usuario
from app.services.security import get_current_user

router = APIRouter(prefix="/servicos", tags=["Serviços"])

@router.post("/", response_model=ServicoResponse)
def criar_servico(
    servico: ServicoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    servico_criado = create_servico(db, servico, current_user.id_usuario)
    return servico_criado

@router.get("/", response_model=List[ServicoResponse])
def listar_servicos(
    categoria: Optional[int] = None,
    search: Optional[str] = None,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    nome: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    servicos = get_servicos(
        db,
        categoria=categoria,
        search=search,
        user_id=user_id,
        status=status,
        nome=nome,
        skip=skip,
        limit=limit
    )
    return servicos  
@router.get("/nome/{nome}", response_model=ServicoResponse)
def obter_servico_por_nome(
    nome: str,
    db: Session = Depends(get_db)
):
    return get_servico_by_name(db, nome)


@router.put("/{id_servico}", response_model=ServicoResponse)
def atualizar_servico(
    id_servico: int,
    dados: ServicoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    servico_atualizado = update_servico(db, id_servico, dados, current_user.id_usuario)
    return servico_atualizado  

@router.delete("/{id_servico}")
def deletar_servico(
    id_servico: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    success = delete_servico(db, id_servico, current_user.id_usuario)
    return {"success": success}