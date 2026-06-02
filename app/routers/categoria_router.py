from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, require_admin
from app.schemas.categoria_schema import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from app.crud import crud_categoria
from app.models.usuario_model import Usuario
from typing import List

router = APIRouter(prefix="/categorias", tags=["Categorias"])

@router.get("/", response_model=List[CategoriaResponse])
def listar_categorias(
    skip: int = 0, limit: int = 1000, apenas_ativas: bool = False,
    db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)
):
    return crud_categoria.listar_categorias(db, skip, limit, apenas_ativas)

@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obter_categoria(
    categoria_id: int,
    db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)
):
    return crud_categoria.obter_categoria(db, categoria_id)

@router.post("/", response_model=CategoriaResponse)
def criar_categoria(
    data: CategoriaCreate,
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    return crud_categoria.criar_categoria(db, data, usuario_id=current_user.id)

@router.put("/{categoria_id}", response_model=CategoriaResponse)
def atualizar_categoria(
    categoria_id: int, data: CategoriaUpdate,
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    return crud_categoria.atualizar_categoria(db, categoria_id, data, usuario_id=current_user.id)

@router.delete("/{categoria_id}", response_model=CategoriaResponse)
def deletar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)
):
    return crud_categoria.deletar_categoria(db, categoria_id, usuario_id=current_user.id)