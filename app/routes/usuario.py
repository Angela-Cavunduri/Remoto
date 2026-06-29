from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form, UploadFile, File
from pydantic import EmailStr
from sqlalchemy.orm import Session
import re
import os
import shutil
import uuid
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
    from app.models.exchangeOffer import ExchangeOffer
    from app.models.service_booking import ServiceBooking
    from sqlalchemy import func

    # Buscar os top 10 utilizadores ativos ordenados por avaliação
    usuarios = db.query(Usuario).filter(
        Usuario.is_active == True
    ).order_by(Usuario.rating_media.desc()).limit(10).all()

    resultado = []
    for user in usuarios:
        # Contar trocas concluídas (como dono ou solicitante)
        total_trocas = db.query(func.count(ExchangeOffer.id_offer)).filter(
            ((ExchangeOffer.id_user == user.id_usuario) | 
                 (ExchangeOffer.id_usuario_solicitante == user.id_usuario)),
            ExchangeOffer.status == "aceita"
        ).scalar() or 0

        # Contar prestações concluídas (como prestador)
        total_prestacoes = db.query(func.count(ServiceBooking.id_pedido)).filter(
            ServiceBooking.id_prestador == user.id_usuario,
            ServiceBooking.status == "concluido"
        ).scalar() or 0

        resultado.append(UsuarioRankingResponse(
            nome=user.nome,
            foto_perfil=user.foto_perfil,
            rating_media=user.rating_media,
            is_dangerous=user.is_dangerous,
            total_trocas=total_trocas,
            total_prestacoes=total_prestacoes
        ))

    return resultado

# 1. Cadastro Simplificado com NIF (3 campos: email, nif, password + foto)
@router.post("/", response_model=UsuarioResponse)
async def criar_usuario_nif(
    email: EmailStr = Form(...),
    nif: str = Form(...),
    palavra_pass: str = Form(...),
    foto: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    # Validar e obter dados via Serviço de NIF
    nome, endereco, tipo_nif, nif_validado = consultar_nif_externo(nif)

    foto_url = None
    caminho_arquivo = None

    # ── Guardar a foto de perfil no disco (obrigatório) ────────
    if not foto or not foto.filename:
        raise HTTPException(status_code=400, detail="A foto de perfil é obrigatória.")

    ext = os.path.splitext(foto.filename)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png"):
        raise HTTPException(status_code=400, detail="Formato de imagem não suportado. Use .jpg, .jpeg ou .png.")
    nome_ficheiro = f"{uuid.uuid4().hex}{ext}"
    caminho_arquivo = os.path.join("app", "static", "uploads", "perfil", nome_ficheiro)
    os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
    with open(caminho_arquivo, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)
    foto_url = f"/static/uploads/perfil/{nome_ficheiro}"

    # ── Validação da Password ─────────────────────────────────
    if len(palavra_pass) < 8:
        raise HTTPException(status_code=400, detail="A palavra-passe deve ter no mínimo 8 caracteres.")
    if len(palavra_pass) > 128:
        raise HTTPException(status_code=400, detail="A palavra-passe não pode ter mais de 128 caracteres.")
    if not re.search(r"[A-Z]", palavra_pass):
        raise HTTPException(status_code=400, detail="A palavra-passe deve conter pelo menos uma letra maiúscula.")
    if not re.search(r"[a-z]", palavra_pass):
        raise HTTPException(status_code=400, detail="A palavra-passe deve conter pelo menos uma letra minúscula.")
    if not re.search(r"[0-9]", palavra_pass):
        raise HTTPException(status_code=400, detail="A palavra-passe deve conter pelo menos um número.")

    try:
        user = create_usuario_com_nif(
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

        user_dict = {
            "id_usuario": user.id_usuario,
            "nome": user.nome,
            "endereco": user.endereco,
            "email": user.email,
            "foto_perfil": user.foto_perfil,
            "rating_media": user.rating_media,
            "is_dangerous": user.is_dangerous
        }

        if user.nome == "Pendente de Validação":
            user_dict["mensagem_aviso"] = "A API de verificação de NIF parou temporariamente. Foste cadastrado, mas tens de voltar mais tarde para validar o NIF e teres permissões nas trocas ou prestações de serviços."

        return user_dict
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

# 4. Listar Utilizadores da Plataforma (público, sem dados sensíveis)
@router.get("/", response_model=List[UsuarioNomeResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

# 4. Perfil do Usuário Logado
@router.get("/me", response_model=UsuarioResponse)
def ver_perfil(current_user: Usuario = Depends(get_current_user)):
    return current_user






@router.delete("/me")
def deletar_perfil(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    deletar_usuario(db, current_user)
    return {"message": "Conta eliminada com sucesso"}

# Removed photo upload endpoint as per user request.

@router.post("/me/validar-nif", response_model=UsuarioResponse)
def revalidar_nif_pendente(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.nome != "Pendente de Validação":
        raise HTTPException(status_code=400, detail="A sua conta já foi validada.")
        
    # Tentar descobrir o NIF associado (Pessoa Singular ou Empresa)
    nif_para_validar = None
    if current_user.user_single:
        nif_para_validar = current_user.user_single.numero_bi
    elif current_user.company:
        nif_para_validar = current_user.company.nif_company
        
    if not nif_para_validar:
        raise HTTPException(status_code=400, detail="Não foi encontrado um NIF na sua conta.")
        
    # Chamar a API novamente
    nome, endereco, tipo_nif, nif_validado = consultar_nif_externo(nif_para_validar)
    
    # Se continuar pendente, significa que a API ainda está em baixo
    if nome == "Pendente de Validação":
        raise HTTPException(status_code=400, detail="A API do Governo ainda se encontra em baixo. Tente novamente mais tarde.")
        
    # Se obteve sucesso, atualizamos a conta
    current_user.nome = nome
    current_user.endereco = endereco
    db.commit()
    db.refresh(current_user)
    
    return current_user