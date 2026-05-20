import stripe
import os
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

# Inicializar a chave secreta da Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def criar_payment_intent(valor: float, moeda: str = "eur", metadata: dict = {}) -> dict:
    """
    Cria um PaymentIntent na Stripe.
    - valor: montante em unidade inteira (ex: 500 = 5,00€ porque Stripe usa cêntimos)
    - moeda: código ISO 4217 (eur, usd, etc.)
    - metadata: dados extra para rastrear (id_offer, id_user, etc.)
    
    Retorna: dict com client_secret e payment_intent_id
    """
    if not stripe.api_key or stripe.api_key == "sk_test_COLOCA_AQUI_A_TUA_CHAVE":
        raise HTTPException(
            status_code=503,
            detail="Stripe não configurado. Adiciona a STRIPE_SECRET_KEY no ficheiro .env"
        )

    try:
        # Stripe trabalha em cêntimos (inteiro), então multiplicamos por 100
        valor_centimos = int(round(valor * 100))

        intent = stripe.PaymentIntent.create(
            amount=valor_centimos,
            currency=moeda,
            metadata=metadata,
            automatic_payment_methods={"enabled": True},
        )

        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "status": intent.status,
        }

    except stripe.error.AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Chave Stripe inválida. Verifica a STRIPE_SECRET_KEY no .env"
        )
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro da Stripe: {str(e)}"
        )


def verificar_webhook(payload: bytes, sig_header: str) -> dict:
    """
    Verifica a assinatura do webhook enviado pela Stripe.
    Garante que o evento vem mesmo da Stripe e não de terceiros.
    """
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    if not webhook_secret:
        raise HTTPException(
            status_code=503,
            detail="STRIPE_WEBHOOK_SECRET não configurado no .env"
        )

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        return event
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Assinatura do webhook inválida")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar webhook: {str(e)}")
