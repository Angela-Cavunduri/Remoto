from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Company(Base):
    __tablename__="company"
    id_company=Column(Integer,primary_key=True,autoincrement=True)
    nif_company=Column(Integer)
    nome_empresa=Column(String(50),nullable=False)
    tipo_empresa=Column(String(100),nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuario.id_usuario"), unique=True)

    
    # Relationship: indica que a empresa pertence a um usuário
    owner = relationship("Usuario", back_populates="company")