from sqlalchemy.orm import Session
from app.models.paymentExchange import PaymentExchange
from app.models.exchangeOffer import ExchangeOffer
from fastapi import HTTPException
from typing import Optional, List


def create_payment(
    db: Session,
    exchange_offer_id: int,
    amount: float,
    stripe_payment_intent_id: Optional[str] = None,
    id_user: Optional[int] = None
) -> PaymentExchange:
    """
    Regista um pagamento na base de dados com estado 'pendente'.
    O estado será atualizado para 'pago' ou 'falhou' via webhook da Stripe.
    """
    oferta = db.query(ExchangeOffer).filter(ExchangeOffer.id_offer == exchange_offer_id).first()
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta de troca não encontrada")
    if oferta.status != "aceita":
        raise HTTPException(
            status_code=400,
            detail="Só é possível criar um pagamento se a troca estiver aceita"
        )

    pagamento = PaymentExchange(
        id_exchange_offer=exchange_offer_id,
        id_user=id_user,
        valor=amount,
        status_pagamento="pendente",
        stripe_payment_intent_id=stripe_payment_intent_id,
    )
    db.add(pagamento)
    db.commit()
    db.refresh(pagamento)
    return pagamento


def update_payment_status(db: Session, payment_id: int, new_status: str) -> PaymentExchange:
    """
    Atualiza o estado do pagamento.
    Estados possíveis: pendente | pago | falhou | cancelado
    """
    pagamento = db.query(PaymentExchange).filter(PaymentExchange.id_payment == payment_id).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")

    pagamento.status_pagamento = new_status
    db.commit()
    db.refresh(pagamento)
    return pagamento


def get_payment_by_intent_id(db: Session, stripe_payment_intent_id: str) -> Optional[PaymentExchange]:
    """
    Encontra um pagamento pelo ID do PaymentIntent da Stripe.
    Usado principalmente no webhook para correlacionar eventos.
    """
    return db.query(PaymentExchange).filter(
        PaymentExchange.stripe_payment_intent_id == stripe_payment_intent_id
    ).first()


def get_payments_by_user(db: Session, user_id: int) -> List[PaymentExchange]:
    """
    Lista todos os pagamentos iniciados por um utilizador específico.
    """
    return db.query(PaymentExchange).filter(
        PaymentExchange.id_user == user_id
    ).all()


def get_payments(db: Session, skip: int = 0, limit: int = 100) -> List[PaymentExchange]:
    """
    Lista todos os pagamentos (uso admin).
    """
    return db.query(PaymentExchange).offset(skip).limit(limit).all()