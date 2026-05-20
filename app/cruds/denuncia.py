from sqlalchemy.orm import Session
from app.models.denuncia import Denuncia
from app.models.user import Usuario
from fastapi import HTTPException, status
from typing import List


def create_denuncia(
    db: Session,
    id_denunciante: int,
    id_denunciado: int,
    comentario: str
) -> Denuncia:
    """
    Cria uma denúncia de um utilizador contra outro.
    A denúncia exige obrigatoriamente um comentário explicativo.
    Após a criação, o denunciado é marcado como `is_dangerous = True`.
    """
    if id_denunciante == id_denunciado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não pode denunciar-se a si próprio!"
        )

    # Verificar se o utilizador denunciado existe
    denunciado = db.query(Usuario).filter(Usuario.id_usuario == id_denunciado).first()
    if not denunciado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O utilizador denunciado não existe."
        )

    # Criar a denúncia
    nova_denuncia = Denuncia(
        id_denunciante=id_denunciante,
        id_denunciado=id_denunciado,
        comentario=comentario
    )
    db.add(nova_denuncia)

    # Marcar o denunciado como PERIGOSO
    denunciado.is_dangerous = True

    db.commit()
    db.refresh(nova_denuncia)
    return nova_denuncia


def get_denuncias_by_user(db: Session, user_id: int) -> List[Denuncia]:
    """
    Retorna a lista de denúncias/comentários recebidos por um utilizador.
    """
    return db.query(Denuncia).filter(Denuncia.id_denunciado == user_id).all()
