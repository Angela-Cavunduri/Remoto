from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form, UploadFile, File
from pydantic import EmailStr
from sqlalchemy.orm import Session
import re
import os
import shutil
import uuid
import cloudinary.uploader
from typing import List, Optional
from app.services.nif import consultar_nif_externo

from app.database.connection import get_db
from app.models.user import Usuario
from app.schemas.usuario import UsuarioNifCreate, UsuarioResponse, UsuarioUpdate, UsuarioVerificar, UsuarioReenviarCodigo, UsuarioNomeResponse, UsuarioRankingResponse, UsuarioPerfilDetalhado, UsuarioListaDetalhado
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
@router.get("/fix-db")
def fix_database_endereco(db: Session = Depends(get_db)):
    from sqlalchemy import text
    try:
        db.execute(text("ALTER TABLE usuario MODIFY COLUMN endereco VARCHAR(255) NOT NULL;"))
        db.commit()
        return {"message": "Coluna 'endereco' aumentada para 255 caracteres com sucesso!"}
    except Exception as e:
        return {"error": str(e)}

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

    # 1. Buscar top 10 utilizadores activos — 1 query
    usuarios = db.query(Usuario).filter(
        Usuario.is_active == True
    ).order_by(Usuario.rating_media.desc()).limit(10).all()

    if not usuarios:
        return []

    ids = [u.id_usuario for u in usuarios]

    # 2. Contar trocas aceites para todos de uma vez — 1 query
    trocas_por_user: dict[int, int] = {uid: 0 for uid in ids}
    for row in db.query(
        ExchangeOffer.id_user,
        ExchangeOffer.id_usuario_solicitante,
    ).filter(
        ExchangeOffer.status == "aceita",
        (ExchangeOffer.id_user.in_(ids)) | (ExchangeOffer.id_usuario_solicitante.in_(ids))
    ).all():
        if row.id_user in trocas_por_user:
            trocas_por_user[row.id_user] += 1
        if row.id_usuario_solicitante in trocas_por_user:
            trocas_por_user[row.id_usuario_solicitante] += 1

    # 3. Contar prestações concluídas para todos de uma vez — 1 query
    prestacoes_por_user: dict[int, int] = {uid: 0 for uid in ids}
    for row in db.query(
        ServiceBooking.id_prestador,
        func.count(ServiceBooking.id_pedido).label("total")
    ).filter(
        ServiceBooking.id_prestador.in_(ids),
        ServiceBooking.status == "concluido"
    ).group_by(ServiceBooking.id_prestador).all():
        prestacoes_por_user[row.id_prestador] = row.total

    # 4. Montar resultado sem mais queries
    return [
        UsuarioRankingResponse(
            nome=u.nome,
            foto_perfil=u.foto_perfil,
            rating_media=u.rating_media,
            is_dangerous=u.is_dangerous,
            total_trocas=trocas_por_user.get(u.id_usuario, 0),
            total_prestacoes=prestacoes_por_user.get(u.id_usuario, 0)
        )
        for u in usuarios
    ]

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

    # ── Guardar a foto de perfil no Cloudinary (obrigatório) ────────
    if not foto or not foto.filename:
        raise HTTPException(status_code=400, detail="A foto de perfil é obrigatória.")

    ext = os.path.splitext(foto.filename)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png"):
        raise HTTPException(status_code=400, detail="Formato de imagem não suportado. Use .jpg, .jpeg ou .png.")
    
    try:
        # Enviar o arquivo diretamente da memória para o Cloudinary
        upload_result = cloudinary.uploader.upload(foto.file, folder="troca_facil_perfil")
        foto_url = upload_result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer upload da imagem para a nuvem: {str(e)}")

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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro interno ao cadastrar: Verifique os dados ou contacte o suporte. Detalhe técnico: {str(e)}")

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
@router.get("/", response_model=List[UsuarioListaDetalhado])
def listar_usuarios(db: Session = Depends(get_db)):
    from app.models.exchangeOffer import ExchangeOffer
    from app.models.service_booking import ServiceBooking
    from app.models.review import Review
    from sqlalchemy import func, case

    # 1. Buscar todos os utilizadores
    usuarios = db.query(Usuario).all()
    if not usuarios:
        return []

    ids = [u.id_usuario for u in usuarios]

    # 2. Contar trocas aceites por utilizador — 1 query para todos
    trocas_rows = db.query(
        func.coalesce(ExchangeOffer.id_user, ExchangeOffer.id_usuario_solicitante).label("uid"),
        func.count(ExchangeOffer.id_offer).label("total")
    ).filter(
        ExchangeOffer.status == "aceita",
        (ExchangeOffer.id_user.in_(ids)) | (ExchangeOffer.id_usuario_solicitante.in_(ids))
    ).group_by(func.coalesce(ExchangeOffer.id_user, ExchangeOffer.id_usuario_solicitante)).all()

    # Agregar manualmente: cada oferta conta para ambos os lados
    trocas_por_user: dict[int, int] = {uid: 0 for uid in ids}
    for row in db.query(
        ExchangeOffer.id_user,
        ExchangeOffer.id_usuario_solicitante,
    ).filter(
        ExchangeOffer.status == "aceita",
        (ExchangeOffer.id_user.in_(ids)) | (ExchangeOffer.id_usuario_solicitante.in_(ids))
    ).all():
        if row.id_user in trocas_por_user:
            trocas_por_user[row.id_user] = trocas_por_user.get(row.id_user, 0) + 1
        if row.id_usuario_solicitante in trocas_por_user:
            trocas_por_user[row.id_usuario_solicitante] = trocas_por_user.get(row.id_usuario_solicitante, 0) + 1

    # 3. Contar prestações concluídas por utilizador — 1 query para todos
    prestacoes_por_user: dict[int, int] = {uid: 0 for uid in ids}
    for row in db.query(
        ServiceBooking.id_prestador,
        func.count(ServiceBooking.id_pedido).label("total")
    ).filter(
        ServiceBooking.id_prestador.in_(ids),
        ServiceBooking.status == "concluido"
    ).group_by(ServiceBooking.id_prestador).all():
        prestacoes_por_user[row.id_prestador] = row.total

    # 4. Buscar todas as reviews de todos os utilizadores — 1 query para todos
    from sqlalchemy.orm import joinedload
    todas_reviews = db.query(Review).options(
        joinedload(Review.avaliador)
    ).filter(Review.id_avaliado.in_(ids)).all()

    reviews_por_user: dict[int, list] = {uid: [] for uid in ids}
    for r in todas_reviews:
        if r.avaliador:
            reviews_por_user[r.id_avaliado].append({
                "id_review": r.id_review,
                "avaliacao": r.avaliacao,
                "conteudo": r.conteudo,
                "data_avaliacao": r.data_avaliacao,
                "avaliador": {
                    "id_usuario": r.avaliador.id_usuario,
                    "nome": r.avaliador.nome,
                    "foto_perfil": r.avaliador.foto_perfil
                }
            })

    # 5. Montar resultado final sem mais queries
    resultado = []
    for user in usuarios:
        uid = user.id_usuario
        resultado.append({
            "id_usuario": uid,
            "nome": user.nome,
            "foto_perfil": user.foto_perfil,
            "rating_media": user.rating_media,
            "is_dangerous": user.is_dangerous,
            "total_trocas": trocas_por_user.get(uid, 0),
            "total_prestacoes": prestacoes_por_user.get(uid, 0),
            "avaliacoes": reviews_por_user.get(uid, [])
        })

    return resultado

# 4. Perfil do Usuário Logado
@router.get("/me", response_model=UsuarioPerfilDetalhado)
def ver_perfil(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.exchangeOffer import ExchangeOffer
    from app.models.service_booking import ServiceBooking
    from app.models.review import Review
    from sqlalchemy import func
    from sqlalchemy.orm import joinedload

    # Contar trocas concluídas
    total_trocas = db.query(func.count(ExchangeOffer.id_offer)).filter(
        ((ExchangeOffer.id_user == current_user.id_usuario) | 
             (ExchangeOffer.id_usuario_solicitante == current_user.id_usuario)),
        ExchangeOffer.status == "aceita"
    ).scalar() or 0

    # Contar prestações concluídas
    total_prestacoes = db.query(func.count(ServiceBooking.id_pedido)).filter(
        ServiceBooking.id_prestador == current_user.id_usuario,
        ServiceBooking.status == "concluido"
    ).scalar() or 0

    # Obter avaliações detalhadas
    reviews = db.query(Review).options(joinedload(Review.avaliador)).filter(
        Review.id_avaliado == current_user.id_usuario
    ).all()

    avaliacoes_list = []
    for r in reviews:
        avaliacoes_list.append({
            "id_review": r.id_review,
            "avaliacao": r.avaliacao,
            "conteudo": r.conteudo,
            "data_avaliacao": r.data_avaliacao,
            "avaliador": {
                "id_usuario": r.avaliador.id_usuario,
                "nome": r.avaliador.nome,
                "foto_perfil": r.avaliador.foto_perfil
            }
        })

    user_dict = {
        "id_usuario": current_user.id_usuario,
        "nome": current_user.nome,
        "endereco": current_user.endereco,
        "email": current_user.email,
        "foto_perfil": current_user.foto_perfil,
        "rating_media": current_user.rating_media,
        "is_dangerous": current_user.is_dangerous,
        "mensagem_aviso": None,
        "total_trocas": total_trocas,
        "total_prestacoes": total_prestacoes,
        "avaliacoes": avaliacoes_list
    }

    if current_user.nome == "Pendente de Validação":
        user_dict["mensagem_aviso"] = "A API de verificação de NIF parou temporariamente. Foste cadastrado, mas tens de voltar mais tarde para validar o NIF e teres permissões nas trocas ou prestações de serviços."

    return user_dict






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