from sqlalchemy.orm import Session
from app.models.produto_model import Produto
from app.schemas.produto_schema import ProdutoCreate, ProdutoUpdate
from fastapi import HTTPException, status

def criar_produto(db: Session, data: ProdutoCreate):
    produto = Produto(**data.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto

def listar_produtos(db: Session, skip: int = 0, limit: int = 100, busca: str = None, categoria: str = None):
    query = db.query(Produto)
    if busca:
        query = query.filter(Produto.nome.ilike(f"%{busca}%"))
    if categoria:
        query = query.filter(Produto.categoria == categoria)
    return query.offset(skip).limit(limit).all()

def obter_produto(db: Session, produto_id: int):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return produto

def atualizar_produto(db: Session, produto_id: int, data: ProdutoUpdate):
    produto = obter_produto(db, produto_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(produto, field, value)
    db.commit()
    db.refresh(produto)
    return produto

def deletar_produto(db: Session, produto_id: int):
    produto = obter_produto(db, produto_id)
    db.delete(produto)
    db.commit()
    return produto