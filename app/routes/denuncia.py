from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db
from app.services.security import get_current_user
from app.models.user import Usuario
from app.schemas.denuncia import DenunciaCreate, DenunciaResponse
from app.cruds.denuncia import create_denuncia, get_denuncias_by_user

router = APIRouter(
    prefix="/denuncias",
    tags=["Segurança (Denúncias)"]
)


@router.post("/", response_model=DenunciaResponse, status_code=status.HTTP_201_CREATED)
def denunciar_utilizador(
    dados: DenunciaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Regista uma denúncia contra um utilizador.
    **O comentário detalhado explicando o que aconteceu é obrigatório** (mínimo de 10 caracteres).
    Ao finalizar a denúncia, o utilizador denunciado será imediatamente sinalizado como 'Perigoso' no ranking.
    """
    try:
        return create_denuncia(
            db=db,
            id_denunciante=current_user.id_usuario,
            id_denunciado=dados.id_denunciado,
            comentario=dados.comentario
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registar denúncia: {str(e)}"
        )


@router.get("/utilizador/{id_usuario}", response_model=List[DenunciaResponse])
def ver_motivos_denuncia(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna todos os comentários e denúncias contra o utilizador especificado.
    Qualquer pessoa autenticada pode ver o que aconteceu para se proteger de fraudes.
    """
    # Verificar se o utilizador existe
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilizador não encontrado."
        )

    return get_denuncias_by_user(db, id_usuario)
