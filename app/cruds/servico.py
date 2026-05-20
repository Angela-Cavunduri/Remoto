from sqlalchemy.orm import Session, joinedload
from app.models.servico import Servico
from app.schemas.servico import ServicoCreate, ServicoUpdate
from app.models.category import Category
from app.models.user import Usuario
from app.models.review import Review
from app.models.exchangeOffer import ExchangeOffer
from sqlalchemy import func
from fastapi import HTTPException

def create_servico(db: Session, servico: ServicoCreate, user_id: int):
    # Verificar limitações do plano Freemium
    user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado")

    # Se for utilizador Free, verificar limite de 2 serviços criados hoje
    if user.plano != "premium":
        from datetime import datetime
        inicio_dia = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        quantidade_servicos_hoje = db.query(func.count(Servico.id_servico)).filter(
            Servico.id_user == user_id,
            Servico.data_criacao >= inicio_dia
        ).scalar()
        if quantidade_servicos_hoje >= 2:
            raise HTTPException(
                status_code=403,
                detail="Limite de 2 serviços criados por dia atingido para o plano Free. Faça upgrade para Premium para criar serviços ilimitados!"
            )

    # 1. Obter ou Criar Categoria
    if servico.id_category:
        categoria = db.query(Category).filter(
            Category.id_category == servico.id_category
        ).first()
    elif servico.nome:
        categoria = db.query(Category).filter(Category.nome.ilike(servico.nome)).first()
        if not categoria:
            categoria = Category(nome=servico.nome)
            db.add(categoria)
            db.flush()
    else:
        raise HTTPException(status_code=400, detail="Deve fornecer uma categoria ou um nome para o novo serviço")

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    novo_servico = Servico(
        descricao=servico.descricao,
        id_category=categoria.id_category,
        id_user=user_id,
        nome=categoria.nome
    )

    db.add(novo_servico)
    db.commit()
    db.refresh(novo_servico)
    return novo_servico

def get_servicos(
    db: Session,
    categoria: int = None,
    search: str = None,
    user_id: int = None,
    status: str = None,
    skip: int = 0,
    limit: int = 10
):
    # Query base
    query = db.query(Servico).join(Usuario).options(
        joinedload(Servico.category),
        joinedload(Servico.usuario)
    )

    # Filtrar apenas serviços de utilizadores ativos
    query = query.filter(Usuario.is_active == True)

    if categoria:
        query = query.filter(Servico.id_category == categoria)
        
        # Ranking por Categoria: Calcular a média de estrelas deste utilizador NESTA categoria
        subquery = db.query(
            Review.id_avaliado,
            func.avg(Review.avaliacao).label("media_categoria")
        ).join(ExchangeOffer, Review.id_exchange_offer == ExchangeOffer.id_offer)\
         .filter(ExchangeOffer.id_servico_desejado.has(id_category=categoria))\
         .group_by(Review.id_avaliado).subquery()
        
        query = query.outerjoin(subquery, Usuario.id_usuario == subquery.c.id_avaliado)
        # Ordenar primeiro pela média na categoria, depois pela média geral
        query = query.order_by(subquery.c.media_categoria.desc(), Usuario.rating_media.desc())
    else:
        # Ordenar por Ranking Geral (rating_media) por padrão
        query = query.order_by(Usuario.rating_media.desc())

    if search:
        query = query.filter(
            (Servico.descricao.ilike(f"%{search}%")) | (Servico.nome.ilike(f"%{search}%"))
        )

    if user_id:
        query = query.filter(Servico.id_user == user_id)
    
    if status:
        query = query.filter(Servico.status == status)

    return query.offset(skip).limit(limit).all()

def update_servico(db: Session, id_servico: int, dados: ServicoUpdate, user_id: int):
    servico = db.query(Servico).filter(Servico.id_servico == id_servico).first()

    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    if servico.id_user != user_id:
        raise HTTPException(status_code=403, detail="Não autorizado")

    if dados.descricao is not None:
        servico.descricao = dados.descricao
    if dados.id_category is not None:
        servico.id_category = dados.id_category
    if dados.status is not None:
        servico.status = dados.status

    db.commit()
    db.refresh(servico)
    return servico

def get_servicos_by_user(db: Session, user_id: int):
    return db.query(Servico).filter(Servico.id_user == user_id).all()

def delete_servico(db: Session, id_servico: int, user_id: int):
    servico = db.query(Servico).filter(Servico.id_servico == id_servico).first()

    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    if servico.id_user != user_id:
        raise HTTPException(status_code=403, detail="Não autorizado")

    db.delete(servico)
    db.commit()
    return True