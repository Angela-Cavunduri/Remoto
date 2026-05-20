from fastapi import APIRouter, WebSocket
from app.database.connection import SessionLocal
from app.cruds.message import (
    send_message_realtime,
    get_conversation,
    mark_as_read,
    get_user_conversations,
    ConnectionManager,
)
import json

router = APIRouter()
manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    db = SessionLocal()

    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            tipo = data.get("tipo")

            # LISTA DE CONVERSAS

            if tipo == "lista_conversas":
                conversas = get_user_conversations(db, user_id)

                await websocket.send_json(
                    {"tipo": "lista_conversas", "conversas": conversas}
                )

            # HISTÓRICO

            elif tipo == "historico":
                outro_user = data["outro_user"]

                mensagens = get_conversation(db, user_id, outro_user)

                await websocket.send_json(
                    {
                        "tipo": "historico",
                        "mensagens": [
                            {
                                "id": m.id_message,
                                "from": m.id_send,
                                "to": m.id_receiver,
                                "conteudo": m.conteudo,
                                "lida": m.visualizacao,
                            }
                            for m in mensagens
                        ],
                    }
                )

                mark_as_read(db, sender_id=outro_user, receiver_id=user_id)

            # NOVA MENSAGEM

            elif tipo == "mensagem":
                receiver_id = data["receiver_id"]
                conteudo = data["conteudo"]

                nova_msg = send_message_realtime(
                    db, sender_id=user_id, receiver_id=receiver_id, conteudo=conteudo
                )

                payload = {
                    "tipo": "mensagem",
                    "id": nova_msg.id_message,
                    "from": user_id,
                    "to": receiver_id,
                    "conteudo": conteudo,
                    "lida": 0,
                }

                await manager.send_personal_message(receiver_id, payload)
                await manager.send_personal_message(user_id, payload)

            # DIGITANDO

            elif tipo == "digitando":
                receiver_id = data["receiver_id"]

                await manager.send_personal_message(
                    receiver_id, {"tipo": "digitando", "user_id": user_id}
                )

    except Exception as e:
        print(f"Erro: {e}")

    finally:
        manager.disconnect(user_id)
        db.close()
