from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.connection import get_db
from app.services.security import get_current_user
from app.models.user import Usuario


def verificar_premium_expirado(db: Session, user: Usuario) -> Usuario:
    """
    Verifica se a subscrição Premium do utilizador expirou.
    Se sim, faz downgrade automático para "free".
    Retorna o utilizador (atualizado se necessário).
    """
    if user.plano == "premium" and user.premium_ate:
        if datetime.utcnow() > user.premium_ate:
            user.plano = "free"
            # Stripe subscription field removed
            db.commit()
            db.refresh(user)
    return user


def exigir_premium(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Dependência FastAPI — bloqueia o acesso se o utilizador não for Premium.
    Uso: Depends(exigir_premium)
    """
    user = verificar_premium_expirado(db, current_user)
    if user.plano != "premium":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta funcionalidade é exclusiva do plano Premium. Faz upgrade em /premium/assinar"
        )
    return user


def obter_estado_plano(db: Session, user: Usuario) -> dict:
    """
    Retorna o estado atual do plano do utilizador.
    Também verifica e corrige subscrições expiradas.
    """
    user = verificar_premium_expirado(db, user)
    return {
        "plano": user.plano,
        "mostra_publicidade": user.plano == "free",
        "premium_ate": user.premium_ate,
        # "stripe_subscription_id": user.stripe_subscription_id,
    }
