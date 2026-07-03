from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.exchangeOffer import ExchangeOffer
from app.models.servico import Servico
from app.models.user import Usuario
from app.models.transfer import Transfer
from app.cruds.message import send_email
from datetime import datetime



def create_exchange_offer(
    db: Session,
    id_servico_oferecido: int,
    id_servico_desejado: int,
    user_id: int,
    mensagem: str = None,
    background_tasks: BackgroundTasks = None
):
    # 1. Verificar se o utilizador está ativo
    user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(403, "A sua conta está desativada por não cumprimento das regras da plataforma.")

    if user.nome == "Pendente de Validação":
        raise HTTPException(403, "A sua conta está Pendente de Validação pela administração. Não pode fazer trocas até que os seus dados sejam validados.")

    # 2. Verificar se o utilizador tem trocas pendentes ou aceites que ainda não foram concluídas
    troca_ativa = db.query(ExchangeOffer).filter(
        (ExchangeOffer.id_usuario_solicitante == user_id) | (ExchangeOffer.id_user == user_id),
        ExchangeOffer.status == "aceita"
    ).first()

    if troca_ativa:
        raise HTTPException(400, "Já tem uma troca em andamento. Termine-a antes de iniciar uma nova.")

    if id_servico_oferecido == id_servico_desejado:
        raise HTTPException(400, "Não pode trocar o mesmo serviço")

    servico_oferecido = db.query(Servico).filter(
        Servico.id_servico == id_servico_oferecido
    ).first()

    servico_desejado = db.query(Servico).filter(
        Servico.id_servico == id_servico_desejado
    ).first()

    if not servico_oferecido or not servico_desejado:
        raise HTTPException(404, "Serviço não encontrado")

    if servico_oferecido.id_user != user_id:
        raise HTTPException(403, "Você só pode oferecer seus próprios serviços")

    nova_oferta = ExchangeOffer(
        id_user=servico_desejado.id_user,  # dono do serviço desejado
        id_servico_oferecido=id_servico_oferecido,
        id_servico_desejado=id_servico_desejado,
        id_usuario_solicitante=user_id,
        mensagem=mensagem
    )

    db.add(nova_oferta)
    db.commit()
    db.refresh(nova_oferta)

    if background_tasks:
        dono_servico = db.query(Usuario).filter(Usuario.id_usuario == nova_oferta.id_user).first()
        solicitante = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        
        if dono_servico and solicitante:
            assunto = "Nova solicitação de troca - Troca Fácil!"
            corpo_email = f"Olá {dono_servico.nome},\n\nVocê recebeu uma solicitação de troca de {solicitante.nome} para o seu serviço!\n\nAcesse no aplicativo para ver a oferta e responder no chat.\n\nEquipe Troca Fácil"
            background_tasks.add_task(send_email, dono_servico.email, assunto, corpo_email)

    return nova_oferta


def aceitar_oferta(db: Session, id_offer: int, user_id: int, background_tasks: BackgroundTasks = None):

    oferta = db.query(ExchangeOffer).filter(
        ExchangeOffer.id_offer == id_offer
    ).first()

    if not oferta:
        raise HTTPException(404, "Oferta não encontrada")

    if oferta.id_user != user_id:
        raise HTTPException(403, "Não autorizado")

    if oferta.status != "pendente":
        raise HTTPException(400, "Oferta já processada")

    # Verifica se já existe uma aceita
    oferta_ja_aceita = db.query(ExchangeOffer).filter(
        ExchangeOffer.id_servico_desejado == oferta.id_servico_desejado,
        ExchangeOffer.status == "aceita"
    ).first()

    if oferta_ja_aceita:
        raise HTTPException(400, "Este serviço já possui uma oferta aceita")

    # Aceita
    oferta.status = "aceita"
    oferta.data_resposta = datetime.utcnow()

    # 🔥 Cancela outras ofertas automaticamente
    db.query(ExchangeOffer).filter(
        ExchangeOffer.id_servico_desejado == oferta.id_servico_desejado,
        ExchangeOffer.id_offer != id_offer,
        ExchangeOffer.status == "pendente"
    ).update({"status": "cancelada"})

    # ✅ Cria registo na tabela Transfer com os dois utilizadores
    novo_transfer = Transfer(
        id_user=oferta.id_user,
        id_usuario_solicitante=oferta.id_usuario_solicitante,
        id_exchangeoffer=oferta.id_offer,
        data_datroca=datetime.utcnow(),
        estados="em andamento"
    )
    db.add(novo_transfer)

    try:
        db.commit()
        db.refresh(oferta)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao aceitar a oferta. Detalhes: {str(e)}")

    # 📧 Notificar o solicitante que a proposta foi aceite
    if background_tasks:
        solicitante = db.query(Usuario).filter(Usuario.id_usuario == oferta.id_usuario_solicitante).first()
        aceitante = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if solicitante and aceitante:
            assunto = "A tua proposta de troca foi aceite! - Troca Fácil"
            corpo = f"Olá {solicitante.nome},\n\nBoa notícia! {aceitante.nome} aceitou a tua proposta de troca.\n\nAbre a aplicação para continuar e combinar os detalhes no chat.\n\nEquipa Troca Fácil"
            background_tasks.add_task(send_email, solicitante.email, assunto, corpo)

    return oferta

def recusar_oferta(db: Session, id_offer: int, user_id: int, background_tasks: BackgroundTasks = None):

    oferta = db.query(ExchangeOffer).filter(
        ExchangeOffer.id_offer == id_offer
    ).first()

    if not oferta:
        raise HTTPException(404, "Oferta não encontrada")

    if oferta.id_user != user_id:
        raise HTTPException(403, "Não autorizado")

    if oferta.status != "pendente":
        raise HTTPException(400, "Oferta já processada")

    oferta.status = "recusada"
    oferta.data_resposta = datetime.utcnow()

    db.commit()
    db.refresh(oferta)

    # 📧 Notificar o solicitante que a proposta foi recusada
    if background_tasks:
        solicitante = db.query(Usuario).filter(Usuario.id_usuario == oferta.id_usuario_solicitante).first()
        recusante = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if solicitante and recusante:
            assunto = "A tua proposta de troca não foi aceite - Troca Fácil"
            corpo = f"Olá {solicitante.nome},\n\nInfelizmente {recusante.nome} não aceitou a tua proposta de troca desta vez.\n\nNão desistas! Explora outros serviços disponíveis na aplicação.\n\nEquipa Troca Fácil"
            background_tasks.add_task(send_email, solicitante.email, assunto, corpo)

    return oferta

def concluir_oferta(db: Session, offer_id: int, user_id: int):

    oferta = db.query(ExchangeOffer).filter(
        ExchangeOffer.id_offer == offer_id
    ).first()

    if not oferta:
        raise HTTPException(404, "Oferta não encontrada")

    if oferta.status != "aceita":
        raise HTTPException(400, "Só ofertas aceitas podem ser concluídas")

    if user_id not in [oferta.id_user, oferta.id_usuario_solicitante]:
        raise HTTPException(403, "Não autorizado")

    # Atualiza o estado da oferta para concluída
    oferta.status = "concluida"

    # Cria o recibo (Transfer) automático com estado "concluído"
    from app.models.transfer import Transfer
    novo_recibo = Transfer(
        id_user=oferta.id_user,
        id_usuario_solicitante=oferta.id_usuario_solicitante,
        id_exchangeoffer=oferta.id_offer,
        estados="concluído",
        data_datroca=datetime.utcnow()
    )
    db.add(novo_recibo)

    db.commit()
    db.refresh(oferta)
    # Também refresh do novo recibo (caso o frontend queira usar o objeto retornado)
    db.refresh(novo_recibo)
    return oferta

def get_trocas(db: Session, user_id: int):
    return db.query(ExchangeOffer).filter(
        (ExchangeOffer.id_user == user_id) | (ExchangeOffer.id_usuario_solicitante == user_id),
    ).all()