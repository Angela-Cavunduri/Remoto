from sqlalchemy.orm import Session
from app.models.transfer import Transfer
from app.schemas.transfer import TransferCreate
from datetime import datetime

def create_transfer(db: Session, transfer: TransferCreate, user_id: int):
    # Verifica se já existe uma transferência para esta oferta
    transfer_existente = db.query(Transfer).filter(Transfer.id_exchangeoffer == transfer.id_exchangeoffer).first()
    if transfer_existente:
        raise ValueError("Já existe um recibo de transferência para esta oferta de troca.")

    nova_transferencia = Transfer(
        id_user=user_id,
        id_exchangeoffer=transfer.id_exchangeoffer,
        estados=transfer.estados,
        data_datroca=datetime.now()
    )
    
    db.add(nova_transferencia)
    db.commit()
    db.refresh(nova_transferencia)
    return nova_transferencia


def get_user_transfers(db: Session, user_id: int):
    return db.query(Transfer).filter(Transfer.id_user == user_id).order_by(Transfer.data_datroca.desc()).all()


def get_transfer_by_id(db: Session, transfer_id: int):
    return db.query(Transfer).filter(Transfer.id_transfer == transfer_id).first()


def update_transfer_status(db: Session, transfer_id: int, novo_estado: str, user_id: int):
    transfer = db.query(Transfer).filter(Transfer.id_transfer == transfer_id).first()
    if not transfer:
        raise ValueError("Transferência não encontrada.")
    
    # Opcional de segurança (Pode retirar se o Admin também quiser mexer)
    if transfer.id_user != user_id:
        raise ValueError("Não tem permissão para alterar o estado deste recibo.")

    transfer.estados = novo_estado
    transfer.data_datroca = datetime.now() # Atualiza a data 
    db.commit()
    db.refresh(transfer)
    return transfer

def deletar_transfer(db: Session, transfer_id: int):
    transfer = db.query(Transfer).filter(Transfer.id_transfer == transfer_id).first()
    if transfer:
        db.delete(transfer)
        db.commit()
        return True
    return False
