from sqlalchemy import Integer,Column,DateTime,ForeignKey,String
from sqlalchemy.orm import relationship
from app.database.connection import Base
from datetime import datetime

class Review(Base):
    __tablename__ = 'review'

    id_review = Column(Integer, primary_key=True, autoincrement=True)

    id_exchange_offer = Column(
        Integer,
        ForeignKey("exchangeoffer.id_offer"),
        nullable=False
    )

    id_avaliado = Column(
        Integer,
        ForeignKey('usuario.id_usuario'),
        nullable=False
    )

    id_avaliador = Column(
        Integer,
        ForeignKey('usuario.id_usuario'),
        nullable=False
    )

    avaliacao = Column(Integer, nullable=False)
    conteudo = Column(String(500), nullable=True)
    data_avaliacao = Column(DateTime, default=datetime.utcnow)

    avaliado = relationship(
        'Usuario',
        foreign_keys=[id_avaliado],
        back_populates='reviews_avaliado'
    )

    avaliador = relationship(
        'Usuario',
        foreign_keys=[id_avaliador],
        back_populates='reviews_avaliador'
    )

    exchange_offer = relationship("ExchangeOffer")