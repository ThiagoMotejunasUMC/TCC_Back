from sqlalchemy.orm import Session
from app.models.variacao_model import Variacao
from app.schemas.variacao_schema import VariacaoCreate, VariacaoUpdate
from fastapi import HTTPException, status

def criar_variacao(db: Session, data: VariacaoCreate):
    if db.query(Variacao).filter(Variacao.sku == data.sku).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU já cadastrado")
    variacao = Variacao(**data.model_dump())
    db.add(variacao)
    db.commit()
    db.refresh(variacao)
    return variacao

def listar_variacoes(db: Session, produto_id: int = None, skip: int = 0, limit: int = 100):
    query = db.query(Variacao)
    if produto_id:
        query = query.filter(Variacao.produto_id == produto_id)
    return query.offset(skip).limit(limit).all()

def obter_variacao(db: Session, variacao_id: int):
    variacao = db.query(Variacao).filter(Variacao.id == variacao_id).first()
    if not variacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variação não encontrada")
    return variacao

def atualizar_variacao(db: Session, variacao_id: int, data: VariacaoUpdate):
    variacao = obter_variacao(db, variacao_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(variacao, field, value)
    db.commit()
    db.refresh(variacao)
    return variacao

def deletar_variacao(db: Session, variacao_id: int):
    variacao = obter_variacao(db, variacao_id)
    db.delete(variacao)
    db.commit()
    return variacao

def listar_alertas_estoque(db: Session):
    return db.query(Variacao).filter(
        Variacao.quantidade_estoque <= Variacao.estoque_minimo,
        Variacao.ativo == True
    ).all()