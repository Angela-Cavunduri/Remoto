from sqlalchemy import Integer,Column,DateTime,ForeignKey,String
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Message(Base):
    __tablename__="message"

    id_message=Column(Integer,primary_key=True,autoincrement=True)
    id_send=Column(Integer,ForeignKey("usuario.id_usuario"),nullable=False)
    id_receiver=Column(Integer,ForeignKey("usuario.id_usuario"),nullable=False)
    conteudo=Column(String(500))
    data_message=Column(DateTime)

    sender = relationship("Usuario", foreign_keys=[id_send],back_populates="messages_sent")
    receiver = relationship("Usuario", foreign_keys=[id_receiver],back_populates="messages_received")
