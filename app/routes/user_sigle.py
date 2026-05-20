from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.user_sigle import UserSingleCreate,UserSingleResponse
from app.cruds.user_sigle import create_user_single,get_user_single,get_by_usuario,update_user_single,delete_user_single

router = APIRouter(prefix="/user-single", tags=["UserSingle"])

@router.post("/", response_model=UserSingleResponse)
def create(user_single: UserSingleCreate, db: Session = Depends(get_db)):
    return create_user_single(db, user_single)

@router.get("/{id_user}", response_model=UserSingleResponse)
def get_one(id_user: int, db: Session = Depends(get_db)):
    user = get_user_single(db, id_user)
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return user

@router.get("/usuario/{usuario_id}", response_model=UserSingleResponse)
def get_by_user(usuario_id: int, db: Session = Depends(get_db)):
    user = get_by_usuario(db, usuario_id)

    if not user:
        raise HTTPException(status_code=404, detail="Não encontrado")

    return user

@router.put("/{id_user}", response_model=UserSingleResponse)
def update(id_user: int, data: UserSingleCreate, db: Session = Depends(get_db)):
    user = update_user_single(db, id_user, data)

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return user

@router.delete("/{id_user}")
def delete(id_user: int, db: Session = Depends(get_db)):
    user = delete_user_single(db, id_user)

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return {"message": "Usuário deletado com sucesso"}