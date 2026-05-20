from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.company import CompanyCreate, CompanyRead
from app.cruds.company import create_company, get_company, get_all_companies, update_company, delete_company

router = APIRouter(prefix="/companies", tags=["companies"])

@router.post("/", response_model=CompanyRead)
def create_company_route(company: CompanyCreate, db: Session = Depends(get_db)):
    return create_company(db, company)

@router.get("/", response_model=list[CompanyRead])
def read_companies(db: Session = Depends(get_db)):
    return get_all_companies(db)

@router.get("/{company_id}", response_model=CompanyRead)
def read_company(company_id: int, db: Session = Depends(get_db)):
    db_company = get_company(db, company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return db_company

@router.put("/{company_id}", response_model=CompanyRead)
def update_company_route(company_id: int, company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = update_company(db, company_id, company)
    if not db_company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return db_company

@router.delete("/{company_id}")
def delete_company_route(company_id: int, db: Session = Depends(get_db)):
    db_company = delete_company(db, company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return {"detail": "Empresa eliminada com sucesso"}