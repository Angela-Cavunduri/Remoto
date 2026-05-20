from sqlalchemy import Column,Integer,String,ForeignKey,DateTime
from sqlalchemy.orm import relationship
from app.database.connection import Base
from datetime import datetime


class Servico(Base):
    __tablename__ = 'servico'

    id_servico = Column(Integer, primary_key=True, autoincrement=True)
    nome=Column(String(50),nullable=True)
    descricao = Column(String(50), nullable=True)
    id_category = Column(Integer, ForeignKey('category.id_category'), nullable=True)
    id_user = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=True)
    status = Column(String(20), default="ativo")
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)

    category = relationship('Category', back_populates='servicos')
    usuario = relationship('Usuario', back_populates='servicos')
    
    ofertas_enviadas = relationship("ExchangeOffer",
    foreign_keys="ExchangeOffer.id_servico_oferecido")

    ofertas_recebidas = relationship("ExchangeOffer",
    foreign_keys="ExchangeOffer.id_servico_desejado")