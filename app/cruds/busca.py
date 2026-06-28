# app/cruds/busca.py
# --------------------------------------------------------------
# CRUD simplificado para a rota de busca de usuários.
# Mantém apenas a função que devolve a lista de usuários.
# --------------------------------------------------------------

import logging
from sqlalchemy.orm import Session
from typing import List

# Modelo de usuário da aplicação
from app.models.user import Usuario
from app.models.servico import Servico

# Schema de resposta que a rota /busca utiliza
from app.schemas.usuario import UsuarioNomeResponse
from sqlalchemy import func, or_


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

    

# Busca usuários por nome (case‑insensitive, parcial)
def buscar_por_nome(db: Session, nome: str, skip: int = 0, limit: int = 100) -> List[UsuarioNomeResponse]:
    # Split the search term into individual words (e.g., first and last name)
    tokens = [t.strip().lower() for t in nome.split() if t.strip()]
    # Build a query that matches all tokens either in user name or service name (case‑insensitive)
    query = db.query(Usuario).outerjoin(Servico, Servico.id_user == Usuario.id_usuario)
    for token in tokens:
        user_cond = func.lower(Usuario.nome).like(f"%{token}%")
        serv_cond = func.lower(Servico.nome).like(f"%{token}%")
        query = query.filter(or_(user_cond, serv_cond))
    # Group by user to avoid duplicates when multiple services match
    query = query.group_by(Usuario.id_usuario)
    # Order by rating (higher rating first) to prioritize higher‑ranked users
    query = query.order_by(Usuario.rating_media.desc())
    logging.info(f"buscar_por_nome query built with tokens={tokens}")
    results = query.offset(skip).limit(limit).all()
    logging.info(f"buscar_por_nome results count: {len(results)}")
    return results
