from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.movimentacao_schema import MovimentacaoCreate, MovimentacaoResponse
from app.crud import crud_movimentacao
from app.models.usuario_model import Usuario
from typing import List, Optional
import csv
import io
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/movimentacoes", tags=["Movimentações"])

@router.get("/", response_model=List[MovimentacaoResponse])
def listar_movimentacoes(skip: int = 0, limit: int = 100, tipo: Optional[str] = None, variacao_id: Optional[int] = None, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return crud_movimentacao.listar_movimentacoes(db, skip, limit, tipo, variacao_id)

@router.post("/", response_model=MovimentacaoResponse)
def registrar_movimentacao(data: MovimentacaoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return crud_movimentacao.registrar_movimentacao(db, data, current_user.id)

@router.get("/exportar/csv")
def exportar_csv(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.cargo not in ["admin", "diretor"]:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    movimentacoes = crud_movimentacao.listar_movimentacoes(db, skip=0, limit=10000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Variação ID", "Usuário ID", "Tipo", "Motivo", "Quantidade", "Observação", "Data"])
    for m in movimentacoes:
        writer.writerow([m.id, m.variacao_id, m.usuario_id, m.tipo, m.motivo, m.quantidade, m.observacao, m.criado_em])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=movimentacoes.csv"}
    )