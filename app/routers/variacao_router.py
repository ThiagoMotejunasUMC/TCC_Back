from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, require_diretor
from app.schemas.variacao_schema import VariacaoCreate, VariacaoUpdate, VariacaoResponse
from app.crud import crud_variacao
from app.models.usuario_model import Usuario
from typing import List, Optional

router = APIRouter(prefix="/variacoes", tags=["Variações"])

@router.get("/alertas", response_model=List[VariacaoResponse])
def listar_alertas(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_variacao.listar_alertas_estoque(db)

@router.get("/", response_model=List[VariacaoResponse])
def listar_variacoes(produto_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_variacao.listar_variacoes(db, produto_id, skip, limit)

@router.get("/{variacao_id}", response_model=VariacaoResponse)
def obter_variacao(variacao_id: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_variacao.obter_variacao(db, variacao_id)

@router.post("/", response_model=VariacaoResponse)
def criar_variacao(data: VariacaoCreate, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_variacao.criar_variacao(db, data)

@router.put("/{variacao_id}", response_model=VariacaoResponse)
def atualizar_variacao(variacao_id: int, data: VariacaoUpdate, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_variacao.atualizar_variacao(db, variacao_id, data)

@router.delete("/{variacao_id}", response_model=VariacaoResponse)
def deletar_variacao(variacao_id: int, db: Session = Depends(get_db), _: Usuario = Depends(require_diretor)):
    return crud_variacao.deletar_variacao(db, variacao_id)