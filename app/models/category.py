from sqlalchemy import Column,Integer,String,DateTime,ForeignKey,Text
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Category(Base):
    __tablename__="category"

    id_category= Column(Integer,primary_key=True,autoincrement=True)
    nome=Column(String(50), nullable=True)
    servicos=relationship("Servico",back_populates="category")