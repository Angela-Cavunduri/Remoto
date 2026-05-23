from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.usuario import UsuarioUpdate, UsuarioLogin
from app.services.security import (verificar_senha,create_access_token)
from app.models.user import Usuario
from app.database.connection import get_db
from app.services.security import get_current_user
from app.schemas.usuario import UsuarioUpdate
from app.cruds.usuario import atualizar_usuario
from app.cruds.usuario import deletar_usuario, buscar_usuario_por_email
from app.services.security import hash_senha

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(Usuario).filter(
        Usuario.email == form_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    if not verificar_senha(
        form_data.password,
        user.palavra_pass
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
        
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta não verificada. Verifique a caixa de entrada do seu e-mail."
        )

    access_token = create_access_token(
        data={"sub": str(user.id_usuario)}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

