from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, File, UploadFile, Form
from pydantic import EmailStr
from sqlalchemy.orm import Session
import re
import os
import shutil
from typing import List, Optional
from app.services.nif import consultar_nif_externo

from app.database.connection import get_db
from app.models.user import Usuario
from app.schemas.usuario import UsuarioNifCreate, UsuarioResponse, UsuarioUpdate, UsuarioVerificar, UsuarioReenviarCodigo, UsuarioNomeResponse, UsuarioRankingResponse
from app.cruds.usuario import (
    create_usuario_com_nif,
    atualizar_usuario,
    deletar_usuario,
    verificar_codigo,
    solicitar_novo_codigo
)
from app.services.security import get_current_user, hash_senha

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

# 0. Estatísticas Públicas (Para todos verem o crescimento do site)
@router.get("/estatisticas")
def ver_estatisticas(db: Session = Depends(get_db)):
    from app.models.servico import Servico
    from app.models.exchangeOffer import ExchangeOffer
    
    total_usuarios = db.query(Usuario).count()
    total_servicos = db.query(Servico).count()
    total_trocas = db.query(ExchangeOffer).count()
    
    return {
        "usuarios_registados": total_usuarios,
        "servicos_disponiveis": total_servicos,
        "trocas_realizadas": total_trocas,
        "mensagem": "Crescemos todos os dias!"
    }

# 0.1 Ranking Público de Utilizadores
@router.get("/ranking", response_model=List[UsuarioRankingResponse])
def ver_ranking_publico(db: Session = Depends(get_db)):
    # Retorna os utilizadores ativos ordenados pela melhor média de avaliação
    return db.query(Usuario).filter(Usuario.is_active == True).order_by(Usuario.rating_media.desc()).limit(10).all()

# Rota temporária para limpar o registo corrompido
@router.get("/limpar-nif-preso/{nif}")
def limpar_nif_preso(nif: str, db: Session = Depends(get_db)):
    from app.models.user_sigle import UserSigle
    sigle = db.query(UserSigle).filter(UserSigle.numero_bi == nif).first()
    if sigle:
        user = db.query(Usuario).filter(Usuario.id_usuario == sigle.usuario_id).first()
        db.delete(sigle)
        if user:
            db.delete(user)
        db.commit()
        return {"message": f"NIF {nif} e utilizador apagados com sucesso. Já podes registar-te de novo!"}
    return {"message": "NIF não encontrado na base de dados."}

# 1. Cadastro Simplificado com NIF (3 campos: email, nif, password + foto)
@router.post("/", response_model=UsuarioResponse)
async def criar_usuario_nif(
    email: EmailStr = Form(...),
    nif: str = Form(...),
    palavra_pass: str = Form(...),
    foto: Optional[UploadFile] = File(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    # Validar e obter dados via Serviço de NIF
    nome, endereco, tipo_nif, nif_validado = consultar_nif_externo(nif)

    foto_url = None
    caminho_arquivo = None
    
    if foto and foto.filename:
        # Lógica de Upload da Foto
        upload_dir = "app/static/uploads/perfil"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Criar um nome de arquivo único para evitar colisões
        extensao = os.path.splitext(foto.filename)[1]
        nome_arquivo = f"{email.replace('@', '_').replace('.', '_')}{extensao}"
        caminho_arquivo = os.path.join(upload_dir, nome_arquivo)
        
        # Guardar o arquivo
        with open(caminho_arquivo, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        
        # Caminho relativo para guardar na BD e servir
        foto_url = f"/static/uploads/perfil/{nome_arquivo}"

    try:
        return create_usuario_com_nif(
            db, 
            nome, 
            email, 
            endereco, 
            palavra_pass, 
            nif_validado, 
            tipo_nif, 
            foto_perfil=foto_url,
            background_tasks=background_tasks
        )
    except ValueError as e:
        # Se falhar a criação do usuário, apagamos a foto se existir
        if caminho_arquivo and os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
        raise HTTPException(status_code=400, detail=f"ERRO RENDER: {str(e)}")

# 2. Verificação de Conta
@router.post("/verificar", response_model=dict)
def verificar_conta(dados: UsuarioVerificar, db: Session = Depends(get_db)):
    try:
        verificar_codigo(db, dados.email, dados.codigo)
        return {"message": "Conta verificada com sucesso!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 3. Reenviar Código
@router.post("/reenviar-codigo", response_model=dict)
def reenviar_codigo(dados: UsuarioReenviarCodigo, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        solicitar_novo_codigo(db, dados.email, background_tasks)
        return {"message": "Um novo código foi enviado para o seu e-mail."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 4. Listar Usuários Cadastrados
@router.get("/", response_model=List[UsuarioNomeResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

# 4. Perfil do Usuário Logado
@router.get("/me", response_model=UsuarioResponse)
def ver_perfil(current_user: Usuario = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UsuarioResponse)
def atualizar_perfil(
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if dados.senha:
        current_user.palavra_pass = hash_senha(dados.senha)
    return atualizar_usuario(db, current_user, dados)

@router.delete("/me")
def deletar_perfil(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    deletar_usuario(db, current_user)
    return {"message": "Conta eliminada com sucesso"}