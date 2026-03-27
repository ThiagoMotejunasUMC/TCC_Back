from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, require_diretor
from app.schemas.produto_schema import ProdutoCreate, ProdutoUpdate, ProdutoResponse
from app.crud import crud_produto
from app.models.usuario_model import Usuario
from typing import List, Optional

router = APIRouter(prefix="/produtos", tags=["Produtos"])

@router.get("/", response_model=List[ProdutoResponse])
def listar_produtos(skip: int = 0, limit: int = 100, busca: Optional[str] = None, categoria: Optional[str] = None, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_produto.listar_produtos(db, skip, limit, busca, categoria)

@router.get("/{produto_id}", response_model=ProdutoResponse)
def obter_produto(produto_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_produto.obter_produto(db, produto_id)

@router.post("/", response_model=ProdutoResponse)
def criar_produto(data: ProdutoCreate, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_produto.criar_produto(db, data)

@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(produto_id: int, data: ProdutoUpdate, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_produto.atualizar_produto(db, produto_id, data)

@router.delete("/{produto_id}", response_model=ProdutoResponse)
def deletar_produto(produto_id: int, db: Session = Depends(get_db), _: Usuario = Depends(require_diretor)):
    return crud_produto.deletar_produto(db, produto_id)