from sqlalchemy import Column,Integer,String,ForeignKey,DateTime
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Servico(Base):
    __tablename__ = 'servico'

    id_servico = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String(50), nullable=True)
    id_category = Column(Integer, ForeignKey('category.id_category'), nullable=True)
    id_user = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=True)

    category = relationship('Category', back_populates='servicos')
    usuario = relationship('Usuario', back_populates='servicos')
