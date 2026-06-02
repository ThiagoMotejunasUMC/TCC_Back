from sqlalchemy.orm import Session
from app.models.fornecedor_model import Fornecedor
from app.schemas.fornecedor_schema import FornecedorCreate, FornecedorUpdate
from app.crud.crud_audit import registrar_log
from fastapi import HTTPException, status

def criar_fornecedor(db: Session, data: FornecedorCreate, usuario_id: int = None):
    fornecedor = Fornecedor(**data.model_dump())
    db.add(fornecedor)
    db.commit()
    db.refresh(fornecedor)
    if usuario_id:
        registrar_log(db, usuario_id, "CREATE", "fornecedor", fornecedor.id, f"Fornecedor criado: {fornecedor.nome}")
    return fornecedor

def listar_fornecedores(db: Session, skip: int = 0, limit: int = 1000, busca: str = None):
    query = db.query(Fornecedor)
    if busca:
        query = query.filter(Fornecedor.nome.ilike(f"%{busca}%"))
    return query.offset(skip).limit(limit).all()

def obter_fornecedor(db: Session, fornecedor_id: int):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor não encontrado")
    return fornecedor

def atualizar_fornecedor(db: Session, fornecedor_id: int, data: FornecedorUpdate, usuario_id: int = None):
    fornecedor = obter_fornecedor(db, fornecedor_id)
    campos = data.model_dump(exclude_unset=True)
    for field, value in campos.items():
        setattr(fornecedor, field, value)
    db.commit()
    db.refresh(fornecedor)
    if usuario_id:
        registrar_log(db, usuario_id, "UPDATE", "fornecedor", fornecedor.id, f"Campos atualizados: {list(campos.keys())}")
    return fornecedor

def deletar_fornecedor(db: Session, fornecedor_id: int, usuario_id: int = None):
    fornecedor = obter_fornecedor(db, fornecedor_id)
    fornecedor.ativo = False
    db.commit()
    db.refresh(fornecedor)
    if usuario_id:
        registrar_log(db, usuario_id, "DELETE", "fornecedor", fornecedor.id, f"Fornecedor desativado: {fornecedor.nome}")
    return fornecedor