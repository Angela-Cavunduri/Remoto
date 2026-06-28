# app/cruds/busca.py
# --------------------------------------------------------------
# CRUD simplificado para a rota de busca de usuários.
# Mantém apenas a função que devolve a lista de usuários.
# --------------------------------------------------------------

from sqlalchemy.orm import Session
from typing import List

# Modelo de usuário da aplicação
from app.models.user import Usuario

# Schema de resposta que a rota /busca utiliza
from app.schemas.usuario import UsuarioNomeResponse


def buscar_todos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> List[UsuarioNomeResponse]:
    """
    Retorna todos os usuários cadastrados no banco de dados.

    Parâmetros
    ----------
    db : Session
        Sessão SQLAlchemy ativa.
    skip : int, opcional
        Quantidade de registros a pular (paginação). Default = 0.
    limit : int, opcional
        Número máximo de usuários a retornar. Default = 100.

    Returns
    -------
    List[UsuarioNomeResponse]
        Lista de objetos `UsuarioNomeResponse` contendo
        ``id_usuario``, ``nome`` e ``foto_perfil`` (e demais campos
        opcionais do schema).
    """
    # Consulta simples – apenas o modelo de usuário,
    # sem joins nem filtros adicionais.
    return (
        db.query(Usuario)
        .offset(skip)
        .limit(limit)
        .all()
    )
