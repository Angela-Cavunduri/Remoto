from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PaymentIntentCreate(BaseModel):
    id_exchange_offer: int
    valor: float  # valor em EUR (ex: 5.00 = taxa de serviço de 5€)


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    valor: float
    moeda: str
    status: str


class PaymentResponse(BaseModel):
    id_payment: int
    id_exchange_offer: int
    valor: float
    status_pagamento: str
    stripe_payment_intent_id: Optional[str]
    data_pagamento: Optional[datetime]

    class Config:
        from_attributes = True


class WebhookResponse(BaseModel):
    received: bool
    event_type: Optional[str] = None
