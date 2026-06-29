from sqlalchemy.orm import Session
from app.models.transfer import Transfer
from app.schemas.transfer import TransferCreate
from datetime import datetime

def get_user_transfers(db: Session, user_id: int):
    return db.query(Transfer).filter(Transfer.id_user == user_id).order_by(Transfer.data_datroca.desc()).all()


def get_transfer_by_id(db: Session, transfer_id: int):
    return db.query(Transfer).filter(Transfer.id_transfer == transfer_id).first()

# No create, update or delete functions – transfers are managed automatically by the exchange flow.
