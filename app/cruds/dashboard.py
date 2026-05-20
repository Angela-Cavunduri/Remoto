# 📁 app/crud/dashboard.py

from sqlalchemy.orm import Session
from app.models.user import Usuario
from app.models.servico import Servico
from app.models.exchangeOffer import ExchangeOffer


def get_dashboard_stats(db: Session):

    total_usuarios = db.query(Usuario).count()

    total_servicos = db.query(Servico).count()

    total_trocas = db.query(ExchangeOffer).count()

    trocas_pendentes = db.query(ExchangeOffer).filter(
        ExchangeOffer.status == "pendente"
    ).count()

    trocas_aceitas = db.query(ExchangeOffer).filter(
        ExchangeOffer.status == "aceita"
    ).count()

    trocas_concluidas = db.query(ExchangeOffer).filter(
        ExchangeOffer.status == "concluida"
    ).count()

    return {
        "usuarios": total_usuarios,
        "servicos": total_servicos,
        "trocas": total_trocas,
        "trocas_pendentes": trocas_pendentes,
        "trocas_aceitas": trocas_aceitas,
        "trocas_concluidas": trocas_concluidas
    }