from sqlalchemy.orm import Session
from app.models.produto_model import Produto
from app.schemas.produto_schema import ProdutoCreate, ProdutoUpdate
from app.crud.crud_audit import registrar_log
from fastapi import HTTPException, status

def criar_produto(db: Session, data: ProdutoCreate, usuario_id: int = None):
    produto = Produto(**data.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    if usuario_id:
        registrar_log(db, usuario_id, "CREATE", "produto", produto.id, f"Produto criado: {produto.nome}")
    return produto

def listar_produtos(db: Session, skip: int = 0, limit: int = 10000, busca: str = None, categoria_id: int = None, apenas_ativos: bool = True):
    query = db.query(Produto)
    if apenas_ativos:
        query = query.filter(Produto.ativo == True)
    if busca:
        query = query.filter(Produto.nome.ilike(f"%{busca}%"))
    if categoria_id:
        query = query.filter(Produto.categoria_id == categoria_id)
    return query.offset(skip).limit(limit).all()

def obter_produto(db: Session, produto_id: int):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return produto

def atualizar_produto(db: Session, produto_id: int, data: ProdutoUpdate, usuario_id: int = None):
    produto = obter_produto(db, produto_id)
    campos = data.model_dump(exclude_unset=True)
    for field, value in campos.items():
        setattr(produto, field, value)
    db.commit()
    db.refresh(produto)
    if usuario_id:
        registrar_log(db, usuario_id, "UPDATE", "produto", produto.id, f"Campos atualizados: {list(campos.keys())}")
    return produto

def deletar_produto(db: Session, produto_id: int, usuario_id: int = None):
    produto = obter_produto(db, produto_id)
    produto.ativo = False
    db.commit()
    db.refresh(produto)
    if usuario_id:
        registrar_log(db, usuario_id, "DELETE", "produto", produto.id, f"Produto desativado: {produto.nome}")
    return produto