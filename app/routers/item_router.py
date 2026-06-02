from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, require_diretor
from app.schemas.item_schema import ItemCreate, ItemUpdate, ItemResponse, AlertaEstoque
from app.crud import crud_item, crud_espaco
from app.models.usuario_model import Usuario
from typing import List, Optional

router = APIRouter(prefix="/itens", tags=["Itens"])

@router.get("/", response_model=List[ItemResponse])
def listar(
    produto_id: Optional[int] = None,
    espaco_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0, limit: int = 10000,
    db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)
):
    return crud_item.listar_itens(db, produto_id=produto_id, espaco_id=espaco_id, status=status, skip=skip, limit=limit)

@router.get("/alertas", response_model=List[AlertaEstoque])
def alertas(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_item.listar_alertas_estoque(db)

@router.get("/{item_id}", response_model=ItemResponse)
def obter(
    item_id: int,
    db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)
):
    item = crud_item.obter_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def criar(
    data: ItemCreate,
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    if data.espaco_id:
        volume_m3 = 0.0
        if data.altura_cm and data.largura_cm and data.profundidade_cm:
            volume_m3 = (data.altura_cm * data.largura_cm * data.profundidade_cm) / 1_000_000
        peso_kg = data.peso_kg or 0.0
        if volume_m3 > 0 or peso_kg > 0:
            resultado = crud_espaco.verificar_capacidade_item(db, data.espaco_id, volume_m3, peso_kg)
            if not resultado["valido"]:
                raise HTTPException(status_code=400, detail=resultado["erro"])
    return crud_item.criar_item(db, data, usuario_id=current_user.id)

@router.put("/{item_id}", response_model=ItemResponse)
def atualizar(
    item_id: int, data: ItemUpdate,
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    if data.espaco_id:
        item_atual = crud_item.obter_item(db, item_id)
        volume_m3 = 0.0
        if data.altura_cm and data.largura_cm and data.profundidade_cm:
            volume_m3 = (data.altura_cm * data.largura_cm * data.profundidade_cm) / 1_000_000
        elif item_atual:
            volume_m3 = item_atual.volume_m3
        peso_kg = data.peso_kg or (item_atual.peso_kg if item_atual else 0.0) or 0.0
        if volume_m3 > 0 or peso_kg > 0:
            resultado = crud_espaco.verificar_capacidade_item(db, data.espaco_id, volume_m3, peso_kg)
            if not resultado["valido"]:
                raise HTTPException(status_code=400, detail=resultado["erro"])
    item = crud_item.atualizar_item(db, item_id, data, usuario_id=current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item

@router.delete("/{item_id}", response_model=ItemResponse)
def deletar(
    item_id: int,
    db: Session = Depends(get_db), current_user: Usuario = Depends(require_diretor)
):
    item = crud_item.deletar_item(db, item_id, usuario_id=current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item