from sqlalchemy import Integer,Column,DateTime,ForeignKey,String
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Review(Base):
    __tablename__ = 'review'

    id_review = Column(Integer, primary_key=True, autoincrement=True)
    id_avaliado = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=True)
    id_avaliador = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=True)
    avaliacao = Column(Integer, nullable=True)
    conteudo = Column(String(500), nullable=True)
    data_avlicao = Column(DateTime, nullable=True)

    avaliado = relationship('Usuario', foreign_keys=[id_avaliado], back_populates='reviews_avaliado')
    avaliador = relationship('Usuario', foreign_keys=[id_avaliador], back_populates='reviews_avaliador')
