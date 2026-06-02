from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, require_diretor
from app.schemas.espaco_schema import EspacoCreate, EspacoUpdate, EspacoResponse, EspacoOcupacao
from app.crud import crud_espaco
from app.models.usuario_model import Usuario
from typing import List

router = APIRouter(prefix="/espacos", tags=["Espaços"])

@router.get("/", response_model=List[EspacoResponse])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_espaco.listar_espacos(db)

@router.get("/{espaco_id}", response_model=EspacoResponse)
def obter(
    espaco_id: int,
    db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)
):
    espaco = crud_espaco.obter_espaco(db, espaco_id)
    if not espaco:
        raise HTTPException(status_code=404, detail="Espaço não encontrado")
    return espaco

@router.get("/{espaco_id}/ocupacao", response_model=EspacoOcupacao)
def ocupacao(
    espaco_id: int,
    db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)
):
    result = crud_espaco.obter_ocupacao(db, espaco_id)
    if not result:
        raise HTTPException(status_code=404, detail="Espaço não encontrado")
    return result

@router.post("/", response_model=EspacoResponse, status_code=status.HTTP_201_CREATED)
def criar(
    data: EspacoCreate,
    db: Session = Depends(get_db), current_user: Usuario = Depends(require_diretor)
):
    return crud_espaco.criar_espaco(db, data, usuario_id=current_user.id)

@router.put("/{espaco_id}", response_model=EspacoResponse)
def atualizar(
    espaco_id: int, data: EspacoUpdate,
    db: Session = Depends(get_db), current_user: Usuario = Depends(require_diretor)
):
    espaco = crud_espaco.atualizar_espaco(db, espaco_id, data, usuario_id=current_user.id)
    if not espaco:
        raise HTTPException(status_code=404, detail="Espaço não encontrado")
    return espaco

@router.delete("/{espaco_id}", response_model=EspacoResponse)
def deletar(
    espaco_id: int,
    db: Session = Depends(get_db), current_user: Usuario = Depends(require_diretor)
):
    espaco = crud_espaco.deletar_espaco(db, espaco_id, usuario_id=current_user.id)
    if not espaco:
        raise HTTPException(status_code=404, detail="Espaço não encontrado")
    return espaco