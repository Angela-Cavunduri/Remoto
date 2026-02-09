from sqlalchemy import Column,Integer,ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class UserSigle(Base):
    __tablename__="user_sigle"

    id_user=Column(Integer,primary_key=True,autoincrement=True)
    numero_bi=Column(Integer,nullable=False,unique=True)
    usuario_id=Column(Integer, ForeignKey("usuario.id_usuario"),unique=True)

    user = relationship("Usuario", back_populates="user_single")