from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.database.connection import Base
from datetime import datetime

class ServiceBooking(Base):
    __tablename__ = 'service_booking'

    id_pedido = Column(Integer, primary_key=True, autoincrement=True)
    id_servico = Column(Integer, ForeignKey('servico.id_servico'), nullable=False)
    id_cliente = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    id_prestador = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    
    data_agendada = Column(DateTime, nullable=False)
    mensagem = Column(Text, nullable=True)
    preco_acordado = Column(Float, nullable=True)
    status = Column(String(20), default="pendente")  # pendente, aceite, recusado, concluido
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    servico = relationship('Servico')
    cliente = relationship('Usuario', foreign_keys=[id_cliente], back_populates='pedidos_feitos')
    prestador = relationship('Usuario', foreign_keys=[id_prestador], back_populates='trabalhos_recebidos')
