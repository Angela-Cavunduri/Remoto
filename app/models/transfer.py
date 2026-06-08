from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Transfer(Base):
    __tablename__ = 'transfer'

    id_transfer = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=True)           # Dono do serviço (quem ACEITOU)
    id_usuario_solicitante = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=True)  # Quem FEZ o pedido
    id_exchangeoffer = Column(Integer, ForeignKey('exchangeoffer.id_offer'), nullable=True)
    data_datroca = Column(DateTime, nullable=True)
    estados = Column(String(50), nullable=True)

    # Relacionamentos
    usuario = relationship('Usuario', foreign_keys=[id_user], back_populates='transfers')
    solicitante = relationship('Usuario', foreign_keys=[id_usuario_solicitante], back_populates='transfers_solicitados')
    exchangeoffer = relationship('ExchangeOffer', back_populates='transfers')