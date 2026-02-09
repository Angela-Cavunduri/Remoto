from sqlalchemy import Column,Integer,String,ForeignKey,DateTime
from sqlalchemy.orm import relationship
from app.database.connection import Base


class ExchangeOffer(Base):
    __tablename__ = 'exchangeoffer'

    id_offer = Column(Integer, primary_key=True, autoincrement=True)
    dada_datroca = Column(DateTime, nullable=True)
    destricao = Column(String(500), nullable=True)
    id_user = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=True)

    usuario = relationship('Usuario', back_populates='exchangeoffers')
    transfers = relationship('Transfer', back_populates='exchangeoffer')

