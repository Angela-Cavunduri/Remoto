from sqlalchemy.orm import Session
from fastapi import WebSocket
from app.models.message import Message
from datetime import datetime
from app.models.user import Usuario
import os
import requests


# 📩 Enviar mensagem
def send_message_realtime(db: Session, sender_id: int, receiver_id: int, conteudo: str):
    nova_mensagem = Message(
        id_send=sender_id,
        id_receiver=receiver_id,
        conteudo=conteudo,
        data_message=datetime.now(),
        visualizacao=0,
    )

    db.add(nova_mensagem)
    db.commit()
    db.refresh(nova_mensagem)

    return nova_mensagem


# 📜 Histórico entre dois usuários
def get_conversation(db: Session, user1: int, user2: int):
    return (
        db.query(Message)
        .filter(
            ((Message.id_send == user1) & (Message.id_receiver == user2))
            | ((Message.id_send == user2) & (Message.id_receiver == user1))
        )
        .order_by(Message.data_message)
        .all()
    )


def conversation_exists(db, user1, user2):
    msg = (
        db.query(Message)
        .filter(
            ((Message.id_send == user1) & (Message.id_receiver == user2))
            | ((Message.id_send == user2) & (Message.id_receiver == user1))
        )
        .first()
    )

    return msg is not None


# 📋 LISTA DE CONVERSAS (AGORA COM NOME)
def get_user_conversations(db: Session, user_id: int):
    mensagens = (
        db.query(Message)
        .filter((Message.id_send == user_id) | (Message.id_receiver == user_id))
        .order_by(Message.data_message.desc())
        .all()
    )

    conversas = {}

    for m in mensagens:
        outro_id = m.id_receiver if m.id_send == user_id else m.id_send

        if outro_id not in conversas:
            usuario = db.query(Usuario).filter(Usuario.id_usuario == outro_id).first()

            conversas[outro_id] = {
                "user_id": outro_id,
                "nome": usuario.nome if usuario else f"Usuário {outro_id}",
                "ultima_mensagem": m.conteudo,
            }

    return list(conversas.values())


# ✔️ Marcar como lidas
def mark_as_read(db: Session, sender_id: int, receiver_id: int):
    mensagens = (
        db.query(Message)
        .filter(
            Message.id_send == sender_id,
            Message.id_receiver == receiver_id,
            Message.visualizacao == 0,
        )
        .all()
    )

    for msg in mensagens:
        msg.visualizacao = 1

    db.commit()


# 🔌 WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"Usuário {user_id} conectado")

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)
        print(f"Usuário {user_id} desconectado")

    async def send_personal_message(self, user_id: int, message: dict):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(message)


def send_email(destino, assunto, mensagem):
    remetente = "cavunduriagel@gmail.com"
    api_key = os.getenv("BREVO_API_KEY")
    
    if not api_key:
        print("Erro: A variável BREVO_API_KEY não está definida nas variáveis de ambiente.")
        return

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }
    
    # Converter a mensagem de texto com quebras de linha para HTML simples
    mensagem_html = f"<html><body><p>{mensagem.replace('\n', '<br>')}</p></body></html>"

    payload = {
        "sender": {"name": "Troca Fácil", "email": remetente},
        "to": [{"email": destino}],
        "subject": assunto,
        "htmlContent": mensagem_html
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print(f"E-mail enviado com sucesso para {destino} via Brevo API")
        else:
            print(f"Aviso: Não foi possível entregar o e-mail para {destino}. Código de status Brevo: {response.status_code}. Resposta: {response.text}")
    except Exception as e:
        print(f"Aviso: Erro ao conectar à API do Brevo para {destino}. Erro: {e}")
