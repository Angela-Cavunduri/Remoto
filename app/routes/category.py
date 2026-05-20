from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.category import CategoryCreate, CategoryResponse
from app.cruds.category import create_category, get_all_categories,delete_category,update_category


router=APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryResponse)
def criar_categoria(category:CategoryCreate, db:Session=Depends(get_db)):
    return create_category(db, category)

@router.get("/", response_model=list[CategoryResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return get_all_categories(db)

@router.put("/{id_category}", response_model=CategoryResponse)
def atualizar_categoria(id_category: int, nome: str, db: Session = Depends(get_db)):
    return update_category(db, id_category, nome)

@router.delete("/categories/{category_id}")
def remover_categoria(category_id: int, db: Session = Depends(get_db)):
    categoria = delete_category(db, category_id)

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    return {"message": "Categoria deletada com sucesso"}