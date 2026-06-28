from sqlalchemy.orm import Session
import logging
import unicodedata
from sqlalchemy import or_, and_
from typing import List, Optional, Union

from app.models.user import Usuario
from app.models.servico import Servico
from app.models.category import Category
from app.schemas.busca import BuscaResponse

def buscar_trabalhadores_servicos(
    db: Session,
    nome_trabalhador: Optional[str] = None,
    nome_servico: Optional[str] = None,
    categoria: Optional[Union[int, str]] = None,
    skip: int = 0,
    limit: int = 10,
) -> List[BuscaResponse]:
    """Busca trabalhadores (usuários) associados a serviços.

    Cada filtro é aplicado de forma independente; se o parâmetro for ``None``
    ele será ignorado.
    """
    query = (
        db.query(
            Usuario.id_usuario,
            Usuario.nome.label('nome_usuario'),
            Usuario.foto_perfil,
            Servico.id_servico,
            Servico.nome.label('nome_servico'),
            Servico.descricao,
            Servico.id_category,
        )
        .outerjoin(Servico, Servico.id_user == Usuario.id_usuario)
        .outerjoin(Category, Category.id_category == Servico.id_category)
    )

    if categoria is not None:
        if isinstance(categoria, int):
            query = query.filter(Servico.id_category == categoria)
        else:
            # filtro por nome da categoria (texto)
            pattern_cat = f"%{categoria}%"
            query = query.filter(Category.nome.ilike(pattern_cat))

    if nome_trabalhador:
        # Build patterns: raw and accent‑removed to increase match chances
        import unicodedata
        normalized = unicodedata.normalize('NFD', nome_trabalhador)
        normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
        pattern_raw = f"%{nome_trabalhador}%"
        pattern_norm = f"%{normalized}%"
        query = query.filter(
            or_(
                Usuario.nome.ilike(pattern_raw),
                Usuario.nome.ilike(pattern_norm)
            )
        )

    if nome_servico:
        pattern = f"%{nome_servico}%"
        query = query.filter(
            (Servico.nome.ilike(pattern)) |
            (Category.nome.ilike(pattern)) |
            (Servico.descricao.ilike(pattern))
        )
    else:
        # existing logic for nome_servico when not provided
        pass

    logging.info(f"SQL gerado para busca: {str(query)}")
    results = query.offset(skip).limit(limit).all()
    # Converte tuplas para objetos BuscaResponse
    return [
        BuscaResponse(
            id_usuario=row.id_usuario,
            nome_usuario=row.nome_usuario,
            foto_perfil=row.foto_perfil,
            id_servico=row.id_servico,
            nome_servico=row.nome_servico,
            descricao=row.descricao,
            id_categoria=row.id_category,
        )
        for row in results
    ]
