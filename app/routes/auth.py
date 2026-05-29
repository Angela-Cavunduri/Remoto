from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas.usuario import UsuarioUpdate, UsuarioLogin, EsqueciSenhaRequest, RedefinirSenhaRequest
from app.services.security import (verificar_senha,create_access_token)
from app.models.user import Usuario
from app.database.connection import get_db
from app.services.security import get_current_user
from app.cruds.usuario import atualizar_usuario
from app.cruds.usuario import deletar_usuario, buscar_usuario_por_email
from app.services.security import hash_senha
from app.cruds.message import send_email
import random
from datetime import datetime, timedelta

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

@router.post("/esqueci-senha")
def esqueci_senha(
    dados: EsqueciSenhaRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = buscar_usuario_por_email(db, dados.email)
    if not user:
        # Retornamos sucesso mesmo se o e-mail não existir por segurança (não revelar quais e-mails estão registados)
        return {"message": "Se o e-mail existir na nossa base de dados, receberá um código de recuperação."}

    codigo_gerado = str(random.randint(100000, 999999))
    tempo_expiracao = datetime.utcnow() + timedelta(minutes=15)
    
    user.codigo_verificacao = codigo_gerado
    user.codigo_expiracao = tempo_expiracao
    db.commit()

    assunto = "Recuperação de Palavra-Passe - Troca Fácil"
    mensagem = f"Olá {user.nome}!\n\nRecebemos um pedido para repor a sua palavra-passe.\nO seu código de recuperação é:\n\n{codigo_gerado}\n\nEste código expira em 15 minutos. Se não fez este pedido, ignore este e-mail."
    background_tasks.add_task(send_email, user.email, assunto, mensagem)

    return {"message": "Se o e-mail existir na nossa base de dados, receberá um código de recuperação."}

@router.post("/redefinir-senha")
def redefinir_senha(
    dados: RedefinirSenhaRequest,
    db: Session = Depends(get_db)
):
    user = buscar_usuario_por_email(db, dados.email)
    if not user:
        raise HTTPException(status_code=400, detail="Código inválido ou expirado.")

    if not user.codigo_verificacao or user.codigo_verificacao != dados.codigo:
        raise HTTPException(status_code=400, detail="Código de recuperação inválido.")

    if user.codigo_expiracao and datetime.utcnow() > user.codigo_expiracao:
        raise HTTPException(status_code=400, detail="O código de recuperação expirou. Por favor, peça um novo código.")

    import re
    if len(dados.nova_senha) < 8 or len(dados.nova_senha) > 128 or not re.search(r"[A-Z]", dados.nova_senha) or not re.search(r"[a-z]", dados.nova_senha) or not re.search(r"[0-9]", dados.nova_senha):
        raise HTTPException(status_code=400, detail="A palavra-passe deve ter pelo menos 8 caracteres, uma maiúscula, uma minúscula e um número.")

    # Atualizar senha e limpar código
    user.palavra_pass = hash_senha(dados.nova_senha)
    user.codigo_verificacao = None
    user.codigo_expiracao = None
    
    # Se a conta não estava verificada, verificamos agora (pois provou ser dono do e-mail)
    if not user.is_verified:
        user.is_verified = True

    db.commit()

    return {"message": "Palavra-passe alterada com sucesso! Pode agora fazer login."}
