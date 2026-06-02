from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.notificacao_schema import NotificacaoResponse
from app.crud import crud_notificacao
from typing import List

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])

@router.get("/", response_model=List[NotificacaoResponse])
def listar(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return crud_notificacao.listar_notificacoes(db, usuario.id)

@router.get("/nao-lidas/count")
def contar_nao_lidas(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return {"count": crud_notificacao.contar_nao_lidas(db, usuario.id)}

@router.put("/{notificacao_id}/lida")
def marcar_lida(notificacao_id: int, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    crud_notificacao.marcar_como_lida(db, notificacao_id, usuario.id)
    return {"mensagem": "Notificação marcada como lida"}

@router.put("/todas/lidas")
def marcar_todas_lidas(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    crud_notificacao.marcar_todas_como_lidas(db, usuario.id)
    return {"mensagem": "Todas as notificações marcadas como lidas"}

@router.delete("/lidas")
def limpar_lidas(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    crud_notificacao.limpar_lidas(db, usuario.id)
    return {"mensagem": "Notificações lidas removidas"}