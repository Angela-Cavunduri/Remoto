from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.connection import Base
from datetime import datetime


class ExchangeOffer(Base):
    __tablename__ = 'exchangeoffer'

    id_offer = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    id_servico_oferecido = Column(Integer, ForeignKey("servico.id_servico"), nullable=False)
    id_servico_desejado = Column(Integer, ForeignKey("servico.id_servico"), nullable=False)
    id_usuario_solicitante = Column(Integer, ForeignKey("usuario.id_usuario"))
    status = Column(String(20), default="pendente")  # pendente, aceita, recusada
    data_criacao = Column(DateTime, default=datetime.utcnow)
    mensagem = Column(String (255), default=True)
    data_resposta = Column(DateTime, nullable=True)

    # Relacionamentos
    usuario = relationship("Usuario",foreign_keys=[id_user] ,back_populates="exchangeoffers")

    servico_oferecido = relationship(
        "Servico",
        foreign_keys=[id_servico_oferecido],
        overlaps="ofertas_enviadas"
    )

    servico_desejado = relationship(
        "Servico",
        foreign_keys=[id_servico_desejado],
        overlaps="ofertas_recebidas"
    )

    payments = relationship(
        "PaymentExchange",
        back_populates="exchange_offer",
        cascade="all, delete"
    )

    transfers = relationship(
        "Transfer",
        back_populates="exchangeoffer",
        cascade="all, delete"
    )

    trocas_solicitadas = relationship(
        "Usuario",
        foreign_keys=[id_usuario_solicitante],  # quem solicitou a troca
        back_populates="solicitacoes_feitas"
    )