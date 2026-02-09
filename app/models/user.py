from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False,unique=True)
    palavra_pass = Column(String(255),nullable=False)
    endereco = Column(String(50), nullable=False)

    user_single = relationship("UserSigle", back_populates="user", uselist=False)
    company = relationship("Company", back_populates="owner", uselist=False)
    exchangeoffers = relationship('ExchangeOffer', back_populates='usuario')
    reviews_avaliado = relationship('Review', back_populates='avaliado', foreign_keys='Review.id_avaliado')
    reviews_avaliador = relationship('Review', back_populates='avaliador', foreign_keys='Review.id_avaliador')
    servicos = relationship('Servico', back_populates='usuario')
    transfers = relationship('Transfer', back_populates='usuario')


    # Relacionamento com mensagens enviadas
    messages_sent = relationship("Message",foreign_keys="Message.id_send",back_populates="sender")

    # Relacionamento com mensagens recebidas
    messages_received = relationship("Message",foreign_keys="Message.id_receiver",back_populates="receiver")
   

