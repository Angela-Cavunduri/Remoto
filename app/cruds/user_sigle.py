from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.user_sigle import UserSingleCreate,UserSingleResponse
from app.models.user_sigle import UserSigle

def create_user_single(db: Session, user_single: UserSingleCreate):
    
    existing = db.query(UserSigle).filter(
        UserSigle.usuario_id == user_single.usuario_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Usuário não existe"
        )
    db_user_single = UserSigle(**user_single.model_dump())

    db.add(db_user_single)
    db.commit()
    db.refresh(db_user_single)

    return db_user_single
def get_user_single(db: Session, id_user: int):
    return db.query(UserSigle).filter(UserSigle.usuario_id == id_user).first()

def get_by_usuario(db: Session, usuario_id: int):
    return db.query(UserSigle).filter(UserSigle.usuario_id == usuario_id).first()

def update_user_single(db: Session, id_user: int, data: UserSingleCreate):
    db_user = db.query(UserSigle).filter(UserSigle.usuario_id == id_user).first()
    
    if db_user:
        for key, value in data.model_dump().items():
            setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)

    return db_user

def delete_user_single(db: Session, id_user: int):
    db_user = db.query(UserSigle).filter(UserSigle.usuario_id == id_user).first()

    if db_user:
        db.delete(db_user)
        db.commit()

    return db_user