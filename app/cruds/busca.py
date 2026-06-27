from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional

from app.models.user import Usuario
from app.models.servico import Servico
from app.models.category import Category
from app.schemas.busca import BuscaResponse

def buscar_trabalhadores_servicos(
    db: Session,
    nome_trabalhador: Optional[str] = None,
    nome_servico: Optional[str] = None,
    categoria: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
) -> List[BuscaResponse]:
    """Busca trabalhadores (usuários) associados a serviços.

    Cada filtro é aplicado de forma independente; se o parâmetro for ``None``
    ele será ignorado.
    """
    query = db.query(
        Usuario.id_usuario,
        Usuario.nome.label('nome_usuario'),
        Usuario.foto_perfil,
        Servico.id_servico,
        Servico.nome.label('nome_servico'),
        Servico.descricao,
        Servico.id_category,
    ).join(Servico, Servico.id_user == Usuario.id_usuario)

    if categoria is not None:
        query = query.filter(Servico.id_category == categoria)

    if nome_trabalhador:
        pattern = f"%{nome_trabalhador}%"
        query = query.filter(Usuario.nome.ilike(pattern))

    if nome_servico:
        pattern = f"%{nome_servico}%"
        query = query.filter(Servico.nome.ilike(pattern))

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
