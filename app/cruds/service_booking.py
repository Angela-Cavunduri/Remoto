from sqlalchemy.orm import Session
from app.models.service_booking import ServiceBooking
from app.models.servico import Servico
from app.schemas.service_booking import ServiceBookingCreate
from fastapi import HTTPException

def criar_pedido(db: Session, pedido: ServiceBookingCreate, id_cliente: int):
    # Verificar se o serviço existe
    servico = db.query(Servico).filter(Servico.id_servico == pedido.id_servico).first()
    if not servico:
        raise ValueError("O serviço solicitado não existe.")
    
    if servico.id_user == id_cliente:
        raise ValueError("Não podes contratar o teu próprio serviço.")

    novo_pedido = ServiceBooking(
        id_servico=pedido.id_servico,
        id_cliente=id_cliente,
        id_prestador=servico.id_user,
        data_agendada=pedido.data_agendada,
        mensagem=pedido.mensagem,
        preco_acordado=pedido.preco_acordado
    )
    
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)
    return novo_pedido

def listar_pedidos_cliente(db: Session, id_cliente: int):
    return db.query(ServiceBooking).filter(ServiceBooking.id_cliente == id_cliente).order_by(ServiceBooking.data_criacao.desc()).all()

def listar_trabalhos_prestador(db: Session, id_prestador: int):
    return db.query(ServiceBooking).filter(ServiceBooking.id_prestador == id_prestador).order_by(ServiceBooking.data_criacao.desc()).all()

def atualizar_status_pedido(db: Session, id_pedido: int, id_prestador: int, novo_status: str):
    pedido = db.query(ServiceBooking).filter(ServiceBooking.id_pedido == id_pedido).first()
    if not pedido:
        raise ValueError("Pedido não encontrado.")
    
    if pedido.id_prestador != id_prestador:
        raise ValueError("Apenas o prestador pode aceitar ou recusar o pedido.")
    
    # Validação simples de status
    status_lower = (novo_status or "").lower()
    if status_lower in ["aceito", "aceitado", "aceite"]:
        status_lower = "aceite"
    elif status_lower in ["recusado", "recusada"]:
        status_lower = "recusado"
    elif status_lower in ["concluido", "concluida"]:
        status_lower = "concluido"
        
    status_validos = ["aceite", "recusado", "concluido"]
    if status_lower not in status_validos:
        raise ValueError("Status inválido.")

    pedido.status = status_lower
    db.commit()
    db.refresh(pedido)
    return pedido
