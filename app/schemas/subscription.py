from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubscriptionCreate(BaseModel):
    """Corpo do pedido para assinar o plano Premium."""
    # Não precisa de campos — o utilizador autenticado é identificado pelo JWT
    pass


class SubscriptionResponse(BaseModel):
    """Resposta após iniciar a subscrição — devolve o client_secret para o frontend."""
    client_secret: str
    subscription_id: str
    plano: str
    mensagem: str


class PlanoEstado(BaseModel):
    """Estado atual do plano do utilizador."""
    plano: str                          # "free" ou "premium"
    mostra_publicidade: bool            # True se for free
    premium_ate: Optional[datetime]     # None se for free
    stripe_subscription_id: Optional[str]

    class Config:
        from_attributes = True


class CancelSubscriptionResponse(BaseModel):
    mensagem: str
    plano: str
    premium_ate: Optional[datetime]     # Premium mantém-se até esta data
