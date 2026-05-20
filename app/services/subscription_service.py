import stripe
import os
from fastapi import HTTPException
from dotenv import load_dotenv, set_key

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Caminho do .env para guardar o price_id gerado
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", ".env")


def _obter_ou_criar_price_id() -> str:
    """
    Obtém o Price ID do plano Premium a partir do .env.
    Se não existir, cria automaticamente o produto e o preço na Stripe
    e guarda o price_id no .env para reutilização futura.
    """
    price_id = os.getenv("STRIPE_PRICE_ID", "")
    if price_id:
        return price_id

    # Criar produto "Premium Troca Fácil"
    produto = stripe.Product.create(
        name="Premium Troca Fácil",
        description="Plano premium — sem publicidade, sem limitações",
    )

    # Criar preço recorrente de 5€/mês
    preco = stripe.Price.create(
        product=produto.id,
        unit_amount=500,        # 5,00 € em cêntimos
        currency="eur",
        recurring={"interval": "month"},
    )

    # Guardar no .env para não criar repetidamente
    abs_env = os.path.abspath(ENV_PATH)
    set_key(abs_env, "STRIPE_PRICE_ID", preco.id)
    os.environ["STRIPE_PRICE_ID"] = preco.id

    return preco.id


def criar_ou_obter_customer(email: str, nome: str) -> str:
    """
    Cria um Customer na Stripe ou reutiliza se já existir um com este email.
    Retorna o stripe_customer_id.
    """
    clientes = stripe.Customer.list(email=email, limit=1)
    if clientes.data:
        return clientes.data[0].id

    cliente = stripe.Customer.create(email=email, name=nome)
    return cliente.id


def criar_subscription(customer_id: str) -> dict:
    """
    Cria uma Subscription mensal para o customer dado.
    Retorna o client_secret para o frontend confirmar o pagamento.
    """
    price_id = _obter_ou_criar_price_id()

    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id}],
        payment_behavior="default_incomplete",
        payment_settings={"save_default_payment_method": "on_subscription"},
        expand=["latest_invoice.payment_intent"],
    )

    client_secret = subscription.latest_invoice.payment_intent.client_secret

    return {
        "subscription_id": subscription.id,
        "client_secret": client_secret,
        "status": subscription.status,
    }


def cancelar_subscription(subscription_id: str) -> dict:
    """
    Cancela a subscrição no fim do período atual (não imediatamente).
    O utilizador mantém o acesso premium até premium_ate.
    """
    sub = stripe.Subscription.modify(
        subscription_id,
        cancel_at_period_end=True,
    )
    import datetime
    premium_ate = datetime.datetime.fromtimestamp(sub.current_period_end)
    return {
        "subscription_id": sub.id,
        "cancel_at_period_end": sub.cancel_at_period_end,
        "premium_ate": premium_ate,
    }
