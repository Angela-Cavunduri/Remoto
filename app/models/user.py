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
from app.models.paymentExchange import PaymentExchange
from app.models.denuncia import Denuncia

class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False,unique=True)
    palavra_pass = Column(String(255),nullable=False)
    endereco = Column(String(50), nullable=False)
    is_verified = Column(Boolean, default=False)
    codigo_verificacao = Column(String(10), nullable=True)
    codigo_expiracao = Column(DateTime, nullable=True)
    foto_perfil = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    rating_media = Column(Integer, default=0)  # Média simples ou escala de 1 a 5

    # ── Freemium ────────────────────────────────────────────
    plano = Column(String(10), default="free", nullable=False)  # "free" | "premium"
    premium_ate = Column(DateTime, nullable=True)               # Expiração da subscrição
    stripe_customer_id = Column(String(255), nullable=True)     # Customer ID na Stripe
    stripe_subscription_id = Column(String(255), nullable=True) # Subscription ID na Stripe
    # ────────────────────────────────────────────────────────

    user_single = relationship("UserSigle", back_populates="user", uselist=False)

    # Prestação de Serviços (Service Booking)
    pedidos_feitos = relationship(
        "ServiceBooking",
        back_populates="cliente",
        foreign_keys="ServiceBooking.id_cliente"
    )

    trabalhos_recebidos = relationship(
        "ServiceBooking",
        back_populates="prestador",
        foreign_keys="ServiceBooking.id_prestador"
    )
    company = relationship("Company", back_populates="owner", uselist=False)
    exchangeoffers = relationship('ExchangeOffer',foreign_keys="ExchangeOffer.id_user" ,back_populates='usuario',cascade="all, delete")
    reviews_avaliado = relationship('Review', back_populates='avaliado', foreign_keys='Review.id_avaliado')
    reviews_avaliador = relationship('Review', back_populates='avaliador', foreign_keys='Review.id_avaliador')
    servicos = relationship('Servico', back_populates='usuario',cascade="all, delete")
    transfers = relationship('Transfer', foreign_keys='Transfer.id_user', back_populates='usuario')
    transfers_solicitados = relationship('Transfer', foreign_keys='Transfer.id_usuario_solicitante', back_populates='solicitante')
    solicitacoes_feitas = relationship(
    "ExchangeOffer",
    foreign_keys="ExchangeOffer.id_usuario_solicitante",
        back_populates="trocas_solicitadas"
    )
    

    # Relacionamento com mensagens enviadas
    messages_sent = relationship("Message",foreign_keys="Message.id_send",back_populates="sender")

    # Relacionamento com mensagens recebidas
    messages_received = relationship("Message",foreign_keys="Message.id_receiver",back_populates="receiver")

    # Relacionamento com pagamentos Stripe
    payments = relationship("PaymentExchange", back_populates="usuario", foreign_keys="PaymentExchange.id_user")

    # ── Sistema de Denúncias (Segurança) ──────────────────────
    is_dangerous = Column(Boolean, default=False, nullable=False) # Se for denunciado, torna-se True
    
    denuncias_feitas = relationship(
        "Denuncia",
        foreign_keys="Denuncia.id_denunciante",
        back_populates="denunciante",
        cascade="all, delete"
    )
    
    denuncias_recebidas = relationship(
        "Denuncia",
        foreign_keys="Denuncia.id_denunciado",
        back_populates="denunciado",
        cascade="all, delete"
    )
    # ──────────────────────────────────────────────────────────
   

