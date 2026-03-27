from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, require_diretor
from app.schemas.fornecedor_schema import FornecedorCreate, FornecedorUpdate, FornecedorResponse
from app.crud import crud_fornecedor
from app.models.usuario_model import Usuario
from typing import List, Optional

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])

@router.get("/", response_model=List[FornecedorResponse])
def listar_fornecedores(skip: int = 0, limit: int = 100, busca: Optional[str] = None, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_fornecedor.listar_fornecedores(db, skip, limit, busca)

@router.get("/{fornecedor_id}", response_model=FornecedorResponse)
def obter_fornecedor(fornecedor_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_fornecedor.obter_fornecedor(db, fornecedor_id)

@router.post("/", response_model=FornecedorResponse)
def criar_fornecedor(data: FornecedorCreate, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_fornecedor.criar_fornecedor(db, data)

@router.put("/{fornecedor_id}", response_model=FornecedorResponse)
def atualizar_fornecedor(fornecedor_id: int, data: FornecedorUpdate, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_fornecedor.atualizar_fornecedor(db, fornecedor_id, data)

@router.delete("/{fornecedor_id}", response_model=FornecedorResponse)
def deletar_fornecedor(fornecedor_id: int, db: Session = Depends(get_db), _: Usuario = Depends(require_diretor)):
    return crud_fornecedor.deletar_fornecedor(db, fornecedor_id)