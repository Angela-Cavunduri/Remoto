from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.connection import get_db
from app.schemas.payment import (
    PaymentIntentCreate,
    PaymentIntentResponse,
    PaymentResponse,
    WebhookResponse,
)
from app.cruds.payment_exchange import (
    create_payment,
    get_payment_by_intent_id,
    get_payments_by_user,
    update_payment_status,
)
from app.services.stripe_service import criar_payment_intent, verificar_webhook
from app.services.security import get_current_user
from app.models.user import Usuario

router = APIRouter(
    prefix="/pagamento",
    tags=["Pagamento (Stripe)"]
)


@router.post("/criar-intencao", response_model=PaymentIntentResponse)
def criar_intencao_de_pagamento(
    dados: PaymentIntentCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cria um PaymentIntent na Stripe para uma oferta de troca aceite.
    Retorna o client_secret que o frontend usa para confirmar o pagamento.
    
    Cartões de teste:
    - Sucesso:            4242 4242 4242 4242
    - Recusado:           4000 0000 0000 0002
    - Fundos insuficientes: 4000 0000 0000 9995
    (qualquer data futura, qualquer CVC)
    """
    # Criar o PaymentIntent na Stripe
    resultado = criar_payment_intent(
        valor=dados.valor,
        moeda="eur",
        metadata={
            "id_user": str(current_user.id_usuario),
            "id_exchange_offer": str(dados.id_exchange_offer),
        }
    )

    # Guardar o pagamento na base de dados com status "pendente"
    create_payment(
        db=db,
        exchange_offer_id=dados.id_exchange_offer,
        amount=dados.valor,
        stripe_payment_intent_id=resultado["payment_intent_id"],
        id_user=current_user.id_usuario,
    )

    return PaymentIntentResponse(
        client_secret=resultado["client_secret"],
        payment_intent_id=resultado["payment_intent_id"],
        valor=dados.valor,
        moeda="eur",
        status=resultado["status"],
    )


@router.post("/webhook", response_model=WebhookResponse)
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    """
    Endpoint que a Stripe chama automaticamente quando o estado do pagamento muda.
    Verifica a assinatura e atualiza o estado na base de dados.
    
    Para testar localmente, usa a Stripe CLI:
    stripe listen --forward-to localhost:8000/pagamento/webhook
    """
    payload = await request.body()

    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Cabeçalho stripe-signature em falta")

    # Verificar que o evento vem mesmo da Stripe
    event = verificar_webhook(payload, stripe_signature)
    event_type = event.get("type", "")

    # Pagamento confirmado com sucesso
    if event_type == "payment_intent.succeeded":
        intent = event["data"]["object"]
        payment_intent_id = intent["id"]

        pagamento = get_payment_by_intent_id(db, payment_intent_id)
        if pagamento:
            update_payment_status(db, pagamento.id_payment, "pago")

    # Pagamento falhou
    elif event_type == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        payment_intent_id = intent["id"]

        pagamento = get_payment_by_intent_id(db, payment_intent_id)
        if pagamento:
            update_payment_status(db, pagamento.id_payment, "falhou")

    # Pagamento cancelado
    elif event_type == "payment_intent.canceled":
        intent = event["data"]["object"]
        payment_intent_id = intent["id"]

        pagamento = get_payment_by_intent_id(db, payment_intent_id)
        if pagamento:
            update_payment_status(db, pagamento.id_payment, "cancelado")

    return WebhookResponse(received=True, event_type=event_type)


@router.get("/historico", response_model=List[PaymentResponse])
def historico_de_pagamentos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todos os pagamentos do utilizador autenticado.
    """
    return get_payments_by_user(db, current_user.id_usuario)


@router.get("/{payment_intent_id}/estado")
def estado_do_pagamento(
    payment_intent_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Consulta o estado atual de um pagamento pelo ID do PaymentIntent.
    """
    pagamento = get_payment_by_intent_id(db, payment_intent_id)
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return {
        "payment_intent_id": payment_intent_id,
        "status_pagamento": pagamento.status_pagamento,
        "valor": pagamento.valor,
        "data_pagamento": pagamento.data_pagamento,
    }
