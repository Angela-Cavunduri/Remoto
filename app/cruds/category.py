from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate
from fastapi import HTTPException
from app.models.servico import Servico

def create_category(db: Session, category: CategoryCreate):
    existe = db.query(Category).filter(
        Category.nome == category.nome
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Categoria já existe"
        )

    nova_categoria = Category(nome=category.nome)
    db.add( nova_categoria )
    db.commit()
    db.refresh( nova_categoria )
    return  nova_categoria 


def get_all_categories(db:Session):
    return db.query(Category).all()


def update_category(db: Session, id_category: int, nome: str):
    categoria = db.query(Category).filter(Category.id_category == id_category).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    categoria.nome = nome
    db.commit()
    db.refresh(categoria)
    return categoria



def delete_category(db: Session, id_category: int):
    categoria = db.query(Category).filter(Category.id_category == id_category).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    servicos = db.query(Servico).filter(Servico.id_category == id_category).first()
    if servicos:
        raise HTTPException(status_code=400, detail="Não pode deletar categoria com serviços")

    db.delete(categoria)
    db.commit()

    return {"message": "Categoria deletada com sucesso"}

def seed_categories(db: Session):
    categorias = [
        "Canalização",
        "Electricidade",
        "Carpintaria",
        "Web Design",
        "Limpeza Doméstica",
        "Aulas de Inglês",
        "Mecânica Automóvel",
        "Fotografia",
        "Pintura",
        "Jardinagem",
        "Costura / Alfaiataria",
        "Personal Trainer",
        "Consultoria Jurídica",
        "Reparação de Computadores",
        "Babysitting"
    ]

    for nome in categorias:
        existente = db.query(Category).filter(Category.nome == nome).first()
        if not existente:
            nova = Category(nome=nome)
            db.add(nova)
    
    db.commit()
    return {"message": "Categorias populadas com sucesso"}