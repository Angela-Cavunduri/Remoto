from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base


class PaymentExchange(Base):
    __tablename__ = "payment_exchanges"

    id_payment = Column(Integer, primary_key=True, autoincrement=True)

    id_exchange_offer = Column(Integer, ForeignKey("exchangeoffer.id_offer"), nullable=False)

    # FK para o utilizador que iniciou o pagamento
    id_user = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=True)

    valor = Column(Float, nullable=False)

    status_pagamento = Column(String(20), default="pendente")  # pendente, pago, falhou, cancelado

    # ID do PaymentIntent da Stripe — usado para correlacionar webhooks
    stripe_payment_intent_id = Column(String(255), nullable=True, unique=True)

    data_pagamento = Column(DateTime, default=datetime.utcnow)

    exchange_offer = relationship(
        "ExchangeOffer",
        back_populates="payments"
    )

    usuario = relationship(
        "Usuario",
        back_populates="payments",
        foreign_keys=[id_user]
    )