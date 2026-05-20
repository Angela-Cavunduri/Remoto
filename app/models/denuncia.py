from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base


class Denuncia(Base):
    __tablename__ = "denuncias"

    id_denuncia = Column(Integer, primary_key=True, autoincrement=True)
    id_denunciante = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    id_denunciado = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    comentario = Column(String(500), nullable=False)  # COMENTÁRIO OBRIGATÓRIO
    data_denuncia = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    denunciante = relationship(
        "Usuario",
        foreign_keys=[id_denunciante],
        back_populates="denuncias_feitas"
    )

    denunciado = relationship(
        "Usuario",
        foreign_keys=[id_denunciado],
        back_populates="denuncias_recebidas"
    )
