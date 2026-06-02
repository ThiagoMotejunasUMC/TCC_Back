from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, require_diretor
from app.schemas.movimentacao_schema import MovimentacaoCreate, MovimentacaoResponse
from app.crud import crud_movimentacao
from app.models.usuario_model import Usuario
from pydantic import BaseModel
from typing import List, Optional
import csv
import io
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/movimentacoes", tags=["Movimentações"])

class MovimentacaoUpdateRequest(BaseModel):
    observacao: str

@router.get("/", response_model=List[MovimentacaoResponse])
def listar_movimentacoes(
    skip: int = 0, limit: int = 100000,
    tipo: Optional[str] = None, item_id: Optional[int] = None,
    db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)
):
    return crud_movimentacao.listar_movimentacoes(db, skip, limit, tipo, item_id)

@router.post("/", response_model=MovimentacaoResponse)
def registrar_movimentacao(
    data: MovimentacaoCreate,
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    return crud_movimentacao.registrar_movimentacao(db, data, current_user.id)

@router.put("/{movimentacao_id}", response_model=MovimentacaoResponse)
def atualizar_movimentacao(
    movimentacao_id: int, data: MovimentacaoUpdateRequest,
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    return crud_movimentacao.atualizar_movimentacao(db, movimentacao_id, data.observacao, current_user.id)

@router.delete("/{movimentacao_id}", response_model=MovimentacaoResponse)
def deletar_movimentacao(
    movimentacao_id: int,
    db: Session = Depends(get_db), current_user: Usuario = Depends(require_diretor)
):
    return crud_movimentacao.deletar_movimentacao(db, movimentacao_id, current_user.id)

@router.get("/exportar/csv")
def exportar_csv(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    if current_user.cargo not in ["admin", "diretor"]:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    from app.models.item_model import Item
    from app.models.produto_model import Produto
    from app.models.usuario_model import Usuario as UsuarioModel

    movimentacoes = crud_movimentacao.listar_movimentacoes(db, skip=0, limit=10000)

    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';')
    writer.writerow([
        "ID", "Produto", "Número de Série", "Tipo", "Motivo",
        "Status Anterior", "Status Novo", "Observação", "Responsável", "Data", "Hora"
    ])

    for m in movimentacoes:
        item = db.query(Item).filter(Item.id == m.item_id).first()
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first() if item else None
        responsavel = db.query(UsuarioModel).filter(UsuarioModel.id == m.usuario_id).first()
        writer.writerow([
            m.id,
            produto.nome if produto else "Produto removido",
            item.numero_serie if item else "Item removido",
            "Entrada" if m.tipo == "entrada" else "Saída",
            m.motivo or "Não informado",
            m.status_anterior or "-",
            m.status_novo or "-",
            m.observacao or "-",
            responsavel.nome if responsavel else f"Usuário #{m.usuario_id}",
            m.criado_em.strftime("%d/%m/%Y"),
            m.criado_em.strftime("%H:%M")
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": "attachment; filename=movimentacoes_sge.csv"}
    )