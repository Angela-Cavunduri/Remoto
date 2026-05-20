from sqlalchemy.orm import Session
from app.models.company import Company
from app.schemas.company import CompanyCreate

def create_company(db: Session, company: CompanyCreate):
    db_company = Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_company(db: Session, company_id: int):
    return db.query(Company).filter(Company.id_company == company_id).first()

def get_all_companies(db: Session):
    return db.query(Company).all()

def update_company(db: Session, company_id: int, company_data: CompanyCreate):
    db_company = db.query(Company).filter(Company.id_company == company_id).first()
    if db_company:
        for key, value in company_data.model_dump().items():
            setattr(db_company, key, value)
        db.commit()
        db.refresh(db_company)
    return db_company

def delete_company(db: Session, company_id: int):
    db_company = db.query(Company).filter(Company.id_company == company_id).first()
    if db_company:
        db.delete(db_company)
        db.commit()
    return db_company