from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
import enum
from sqlalchemy.orm import relationship
from app.database.connection import Base
from app.models.user_sigle import UserSigle
from app.models.company import Company
from app.models.transfer import Transfer
from app.models.servico import Servico
from app.models.review import Review
from app.models.message import Message
from app.models.exchangeOffer import ExchangeOffer
from app.models.category import Category

from app.models.denuncia import Denuncia
from app.models.service_booking import ServiceBooking

class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(100), nullable=False,unique=True)
    palavra_pass = Column(String(255),nullable=False)
    endereco = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    codigo_verificacao = Column(String(10), nullable=True)
    codigo_expiracao = Column(DateTime, nullable=True)
    foto_perfil = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    rating_media = Column(Integer, default=0)

    plano = Column(String(10), default="free", nullable=False)
    premium_ate = Column(DateTime, nullable=True)


    user_single = relationship("UserSigle", back_populates="user", uselist=False)
    company = relationship("Company", back_populates="owner", uselist=False)
    
    exchangeoffers = relationship('ExchangeOffer', foreign_keys="ExchangeOffer.id_user", back_populates='usuario', cascade="all, delete")
    solicitacoes_feitas = relationship('ExchangeOffer', foreign_keys="ExchangeOffer.id_usuario_solicitante", back_populates='trocas_solicitadas', cascade="all, delete")
    transfers = relationship('Transfer', foreign_keys="Transfer.id_user", back_populates='usuario', cascade="all, delete")
    transfers_solicitados = relationship('Transfer', foreign_keys="Transfer.id_usuario_solicitante", back_populates='solicitante', cascade="all, delete")

    messages_received = relationship("Message",foreign_keys="Message.id_receiver",back_populates="receiver")


    is_dangerous = Column(Boolean, default=False, nullable=False)
    denuncias_feitas = relationship("Denuncia", foreign_keys="Denuncia.id_denunciante", back_populates="denunciante", cascade="all, delete")
    denuncias_recebidas = relationship("Denuncia", foreign_keys="Denuncia.id_denunciado", back_populates="denunciado", cascade="all, delete")

    pedidos_feitos = relationship('ServiceBooking', foreign_keys='ServiceBooking.id_cliente', back_populates='cliente')
    trabalhos_recebidos = relationship('ServiceBooking', foreign_keys='ServiceBooking.id_prestador', back_populates='prestador')
    servicos = relationship('Servico', back_populates='usuario', cascade="all, delete")
    reviews_avaliado = relationship('Review', foreign_keys='Review.id_avaliado', back_populates='avaliado', cascade="all, delete")
    reviews_avaliador = relationship('Review', foreign_keys='Review.id_avaliador', back_populates='avaliador', cascade="all, delete")
    messages_sent = relationship("Message", foreign_keys="Message.id_send", back_populates="sender", cascade="all, delete")
