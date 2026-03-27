from sqlalchemy.orm import Session
from app.models.fornecedor_model import Fornecedor
from app.schemas.fornecedor_schema import FornecedorCreate, FornecedorUpdate
from fastapi import HTTPException, status

def criar_fornecedor(db: Session, data: FornecedorCreate):
    fornecedor = Fornecedor(**data.model_dump())
    db.add(fornecedor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor

def listar_fornecedores(db: Session, skip: int = 0, limit: int = 100, busca: str = None):
    query = db.query(Fornecedor)
    if busca:
        query = query.filter(Fornecedor.nome.ilike(f"%{busca}%"))
    return query.offset(skip).limit(limit).all()

def obter_fornecedor(db: Session, fornecedor_id: int):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor não encontrado")
    return fornecedor

def atualizar_fornecedor(db: Session, fornecedor_id: int, data: FornecedorUpdate):
    fornecedor = obter_fornecedor(db, fornecedor_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(fornecedor, field, value)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor

def deletar_fornecedor(db: Session, fornecedor_id: int):
    fornecedor = obter_fornecedor(db, fornecedor_id)
    db.delete(fornecedor)
    db.commit()
    return fornecedor