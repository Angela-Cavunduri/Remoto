from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.schemas.review import ReviewCreate, ReviewResponse
from app.cruds.review import create_review
from app.services.security import get_current_user
from app.models.user import Usuario

router = APIRouter(prefix="/avaliacoes", tags=["Avaliações"])

@router.post("/", response_model=ReviewResponse)
def avaliar_troca(
    dados: ReviewCreate, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    try:
        return create_review(db, dados, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
