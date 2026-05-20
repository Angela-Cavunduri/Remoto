from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from sqlalchemy.orm import Session
from typing import Optional
import stripe
import os
import datetime

from app.database.connection import get_db
from app.services.security import get_current_user
from app.models.user import Usuario
from app.schemas.subscription import (
    SubscriptionResponse,
    PlanoEstado,
    CancelSubscriptionResponse
)
from app.services.subscription_service import (
    criar_ou_obter_customer,
    criar_subscription,
    cancelar_subscription
)
from app.services.premium import obter_estado_plano, verificar_premium_expirado
from app.services.stripe_service import verificar_webhook

router = APIRouter(
    prefix="/premium",
    tags=["Premium (Subscrições)"]
)


@router.get("/estado", response_model=PlanoEstado)
def consultar_plano(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna o plano atual do utilizador, data de expiração e se mostra publicidade.
    """
    return obter_estado_plano(db, current_user)


@router.post("/assinar", response_model=SubscriptionResponse)
def assinar_premium(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Inicia o processo de subscrição Premium.
    Devolve um `client_secret` para o frontend confirmar o pagamento mensal (5€/mês)
    usando Stripe Card Elements.
    """
    if current_user.plano == "premium":
        # Se já for premium, verificar se está expirado antes de recusar
        verificar_premium_expirado(db, current_user)
        if current_user.plano == "premium":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você já possui o plano Premium ativo!"
            )

    # 1. Obter ou Criar Cliente na Stripe
    stripe_customer_id = current_user.stripe_customer_id
    if not stripe_customer_id:
        stripe_customer_id = criar_ou_obter_customer(
            email=current_user.email,
            nome=current_user.nome
        )
        current_user.stripe_customer_id = stripe_customer_id
        db.commit()

    # 2. Criar a Subscrição
    try:
        resultado = criar_subscription(stripe_customer_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar subscrição na Stripe: {str(e)}"
        )

    # 3. Guardar o ID provisório da subscrição
    current_user.stripe_subscription_id = resultado["subscription_id"]
    db.commit()

    return SubscriptionResponse(
        client_secret=resultado["client_secret"],
        subscription_id=resultado["subscription_id"],
        plano="premium_pendente",
        mensagem="Subscrição iniciada. Confirme o pagamento no frontend."
    )


@router.post("/cancelar", response_model=CancelSubscriptionResponse)
def cancelar_premium(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cancela a subscrição recorrente.
    O plano continuará Premium até ao final do ciclo de faturação já pago (premium_ate).
    """
    if current_user.plano != "premium" or not current_user.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não possui nenhuma subscrição ativa para cancelar."
        )

    try:
        resultado = cancelar_subscription(current_user.stripe_subscription_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cancelar subscrição na Stripe: {str(e)}"
        )

    return CancelSubscriptionResponse(
        mensagem="A sua subscrição foi cancelada. Continuará Premium até ao fim do período pago.",
        plano=current_user.plano,
        premium_ate=resultado["premium_ate"]
    )


@router.post("/webhook")
async def premium_stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    """
    Webhook da Stripe para escutar eventos de faturação.
    Atualiza as datas de acesso ao Premium e faz downgrade se a fatura falhar.
    """
    payload = await request.body()

    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assinatura Stripe inexistente"
        )

    event = verificar_webhook(payload, stripe_signature)
    event_type = event.get("type", "")

    # Caso a fatura seja paga com sucesso (tanto a 1ª como as renovações mensais)
    if event_type == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        subscription_id = invoice.get("subscription")

        if subscription_id:
            # Buscar a subscrição para ver a data de fim do período atual (renovado)
            sub = stripe.Subscription.retrieve(subscription_id)
            premium_ate = datetime.datetime.fromtimestamp(sub.current_period_end)

            # Procurar o utilizador com este subscription_id ou customer_id
            user = db.query(Usuario).filter(
                (Usuario.stripe_subscription_id == subscription_id) |
                (Usuario.stripe_customer_id == invoice.get("customer"))
            ).first()

            if user:
                user.plano = "premium"
                user.stripe_subscription_id = subscription_id
                user.premium_ate = premium_ate
                db.commit()
                print(f"WEBHOOK: Utilizador {user.nome} renovado/ativado até {premium_ate}")

    # Se a subscrição for eliminada na Stripe (ex: cancelada permanentemente ou falha grave de pagamento)
    elif event_type == "customer.subscription.deleted":
        sub = event["data"]["object"]
        subscription_id = sub.get("id")

        user = db.query(Usuario).filter(Usuario.stripe_subscription_id == subscription_id).first()
        if user:
            user.plano = "free"
            user.stripe_subscription_id = None
            user.premium_ate = None
            db.commit()
            print(f"WEBHOOK: Utilizador {user.nome} perdeu acesso Premium (deleted)")

    return {"received": True}
