from sqlalchemy.orm import Session
from app.models.categoria_model import Categoria
from app.schemas.categoria_schema import CategoriaCreate, CategoriaUpdate
from app.crud.crud_audit import registrar_log
from fastapi import HTTPException, status

def criar_categoria(db: Session, data: CategoriaCreate, usuario_id: int = None):
    if db.query(Categoria).filter(Categoria.nome == data.nome).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria já cadastrada")
    categoria = Categoria(**data.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    if usuario_id:
        registrar_log(db, usuario_id, "CREATE", "categoria", categoria.id, f"Categoria criada: {categoria.nome}")
    return categoria

def listar_categorias(db: Session, skip: int = 0, limit: int = 1000, apenas_ativas: bool = False):
    query = db.query(Categoria)
    if apenas_ativas:
        query = query.filter(Categoria.ativo == True)
    return query.offset(skip).limit(limit).all()

def obter_categoria(db: Session, categoria_id: int):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
    return categoria

def atualizar_categoria(db: Session, categoria_id: int, data: CategoriaUpdate, usuario_id: int = None):
    categoria = obter_categoria(db, categoria_id)
    campos = data.model_dump(exclude_unset=True)
    for field, value in campos.items():
        setattr(categoria, field, value)
    db.commit()
    db.refresh(categoria)
    if usuario_id:
        registrar_log(db, usuario_id, "UPDATE", "categoria", categoria.id, f"Campos atualizados: {list(campos.keys())}")
    return categoria

def deletar_categoria(db: Session, categoria_id: int, usuario_id: int = None):
    categoria = obter_categoria(db, categoria_id)
    categoria.ativo = False
    db.commit()
    db.refresh(categoria)
    if usuario_id:
        registrar_log(db, usuario_id, "DELETE", "categoria", categoria.id, f"Categoria desativada: {categoria.nome}")
    return categoria