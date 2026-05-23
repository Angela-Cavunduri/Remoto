from app.models.user import Usuario
from app.schemas.usuario import UsuarioCreate
from app.services.security import hash_senha
import random
from datetime import datetime, timedelta
from fastapi import BackgroundTasks
from app.cruds.message import send_email
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from app.models.user import Usuario
from app.models.user_sigle import UserSigle
from app.models.company import Company
from app.models.servico import Servico
from app.models.exchangeOffer import ExchangeOffer
from app.models.review import Review




def create_usuario(db: Session, usuario: UsuarioCreate, 
foto_perfil: str = None, background_tasks: BackgroundTasks = None):
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        raise ValueError("Email já cadastrado")
    
    codigo_gerado = str(random.randint(100000, 999999))
    tempo_expiracao = datetime.utcnow() + timedelta(minutes=5)
    
    novo_usuario=Usuario(
        nome=usuario.nome,
        email=usuario.email,
        endereco=usuario.endereco,
        palavra_pass=hash_senha(usuario.palavra_pass),
        is_verified=False,
        codigo_verificacao=codigo_gerado,
        codigo_expiracao=tempo_expiracao,
        foto_perfil=foto_perfil
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    if background_tasks:
        assunto = "Verifique a sua conta - Troca Fácil"
        mensagem = f"Olá {novo_usuario.nome}!\n\nBem-vindo ao Troca Fácil. O seu código de segurança é:\n\n{codigo_gerado}\n\nVolte à aplicação e insira este código para poder fazer login."
        background_tasks.add_task(send_email, novo_usuario.email, assunto, mensagem)

    return novo_usuario

def create_usuario_com_nif(db: Session, nome: str, email: str, endereco: str, palavra_pass: str, nif: str, tipo_nif: str, foto_perfil: str = None, background_tasks: BackgroundTasks = None):
    usuario_existente = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario_existente:
        raise ValueError("Email já cadastrado")
    
    codigo_gerado = str(random.randint(100000, 999999))
    tempo_expiracao = datetime.utcnow() + timedelta(minutes=5)
    
    novo_usuario = Usuario(
        nome=nome,
        email=email,
        endereco=endereco,
        palavra_pass=hash_senha(palavra_pass),
        is_verified=False,
        codigo_verificacao=codigo_gerado,
        codigo_expiracao=tempo_expiracao,
        foto_perfil=foto_perfil
    )
    db.add(novo_usuario)
    db.flush() # Para obter o ID sem commitar tudo ainda

    if tipo_nif == "Pessoa Singular":
        nova_pessoa = UserSigle(numero_bi=nif, usuario_id=novo_usuario.id_usuario)
        db.add(nova_pessoa)
    elif tipo_nif == "Empresa / Entidade Coletiva":
        nova_empresa = Company(
            nif_company=nif,
            nome_empresa=nome, # Usando o nome retornado pela API ou fornecido
            tipo_empresa="Entidade Coletiva",
            usuario_id=novo_usuario.id_usuario
        )
        db.add(nova_empresa)
    
    try:
        db.commit()
        db.refresh(novo_usuario)
    except IntegrityError:
        db.rollback()
        raise ValueError("Este NIF já se encontra registado.")

    if background_tasks:
        assunto = "Verifique a sua conta - Troca Fácil"
        mensagem = f"Olá {novo_usuario.nome}!\n\nBem-vindo ao Troca Fácil. O seu código de segurança é:\n\n{codigo_gerado}\n\nVolte à aplicação e insira este código para poder fazer login."
        background_tasks.add_task(send_email, novo_usuario.email, assunto, mensagem)

    return novo_usuario

def atualizar_usuario(db: Session, usuario, dados_update):
    for campo, valor in dados_update.dict(exclude_unset=True).items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario

def deletar_usuario(db: Session, usuario: Usuario):
    db.delete(usuario)
    db.commit()
    return {"mensagem": "Usuário deletado com sucesso"}

def buscar_usuario_por_email(db: Session, email):
    return db.query(Usuario).filter(Usuario.email == email).first()

def verificar_codigo(db: Session, email: str, codigo: str):
    user = buscar_usuario_por_email(db, email)
    if not user:
        raise ValueError("Usuário não encontrado.")
    if user.is_verified:
        raise ValueError("Esta conta já está verificada.")
        
    if user.codigo_expiracao and datetime.utcnow() > user.codigo_expiracao:
        raise ValueError("O código de verificação expirou (passaram mais de 5 minutos). Por favor, registe-se ou peça um novo código.")
        
    if user.codigo_verificacao != codigo:
        raise ValueError("Código de verificação inválido.")
    
    user.is_verified = True
    user.codigo_verificacao = None
    user.codigo_expiracao = None
    db.commit()
    db.refresh(user)
    return user

# Histórico de trocas (como criador ou como dono do serviço desejado)
def get_trocas_usuario(db: Session, user_id: int):
    return db.query(ExchangeOffer).filter(
        or_(
            ExchangeOffer.id_user == user_id,
            ExchangeOffer.servico_desejado.has(id_user=user_id)  
        )
    ).all()


# Lista todos os serviços criados pelo usuário
def get_servicos_usuario(db: Session, user_id: int):
    return db.query(Servico).filter(
        Servico.id_user == user_id  
    ).all()

def solicitar_novo_codigo(db: Session, email: str, background_tasks: BackgroundTasks = None):
    user = buscar_usuario_por_email(db, email)
    if not user:
        raise ValueError("Usuário não encontrado.")
    if user.is_verified:
        raise ValueError("Esta conta já está verificada.")
        
    codigo_gerado = str(random.randint(100000, 999999))
    tempo_expiracao = datetime.utcnow() + timedelta(minutes=5)
    
    user.codigo_verificacao = codigo_gerado
    user.codigo_expiracao = tempo_expiracao
    
    db.commit()
    db.refresh(user)
    
    if background_tasks:
        assunto = "Novo Código de Verificação - Troca Fácil"
        mensagem = f"Olá {user.nome}!\n\nVocê solicitou um novo código de segurança. O seu novo código é:\n\n{codigo_gerado}\n\nEste código expira em 5 minutos."
        background_tasks.add_task(send_email, user.email, assunto, mensagem)
        
    return user