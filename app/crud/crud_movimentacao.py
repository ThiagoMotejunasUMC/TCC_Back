from sqlalchemy.orm import Session
from app.models.movimentacao_model import Movimentacao
from app.models.item_model import Item
from app.schemas.movimentacao_schema import MovimentacaoCreate
from app.crud.crud_audit import registrar_log
from app.crud.crud_item import verificar_e_notificar_estoque
from fastapi import HTTPException, status

STATUS_ENTRADA = "disponivel"
MOTIVOS_STATUS = {
    "venda": "vendido",
    "descarte": "danificado",
    "manutencao": "em_manutencao",
    "devolucao": "disponivel",
    "ajuste": "disponivel",
    "ajuste de inventário": "disponivel",
    "compra": "disponivel",
}

def registrar_movimentacao(db: Session, data: MovimentacaoCreate, usuario_id: int):
    item = db.query(Item).filter(Item.id == data.item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    if not item.ativo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item inativo")

    status_anterior = item.status

    if data.tipo == "entrada":
        item.status = "disponivel"
    elif data.tipo == "saida":
        if item.status != "disponivel":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item não está disponível. Status atual: {item.status}"
            )
        motivo_normalizado = (data.motivo or "").lower()
        item.status = MOTIVOS_STATUS.get(motivo_normalizado, "vendido")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo deve ser 'entrada' ou 'saida'"
        )

    movimentacao = Movimentacao(
        item_id=data.item_id,
        usuario_id=usuario_id,
        tipo=data.tipo,
        motivo=data.motivo,
        status_anterior=status_anterior,
        status_novo=item.status,
        observacao=data.observacao
    )
    db.add(movimentacao)
    db.commit()
    db.refresh(movimentacao)

    registrar_log(
        db, usuario_id, "CREATE", "movimentacao", movimentacao.id,
        f"Movimentação {data.tipo} — Item: {item.numero_serie} — Motivo: {data.motivo} — Status: {status_anterior} → {item.status}"
    )

    verificar_e_notificar_estoque(db, item.produto_id)

    return movimentacao

def atualizar_movimentacao(db: Session, movimentacao_id: int, observacao: str, usuario_id: int):
    movimentacao = db.query(Movimentacao).filter(Movimentacao.id == movimentacao_id).first()
    if not movimentacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimentação não encontrada")

    observacao_anterior = movimentacao.observacao
    movimentacao.observacao = observacao
    db.commit()
    db.refresh(movimentacao)

    registrar_log(
        db, usuario_id, "UPDATE", "movimentacao", movimentacao.id,
        f"Observação alterada de '{observacao_anterior}' para '{observacao}'"
    )

    return movimentacao

def deletar_movimentacao(db: Session, movimentacao_id: int, usuario_id: int):
    movimentacao = db.query(Movimentacao).filter(Movimentacao.id == movimentacao_id).first()
    if not movimentacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimentação não encontrada")

    item = db.query(Item).filter(Item.id == movimentacao.item_id).first()
    numero_serie = item.numero_serie if item else f"item_id={movimentacao.item_id}"

    registrar_log(
        db, usuario_id, "DELETE", "movimentacao", movimentacao.id,
        f"Movimentação removida — Tipo: {movimentacao.tipo} — Item: {numero_serie} — Motivo: {movimentacao.motivo}"
    )

    db.delete(movimentacao)
    db.commit()
    return movimentacao

def listar_movimentacoes(db: Session, skip: int = 0, limit: int = 100000, tipo: str = None, item_id: int = None):
    query = db.query(Movimentacao)
    if tipo:
        query = query.filter(Movimentacao.tipo == tipo)
    if item_id:
        query = query.filter(Movimentacao.item_id == item_id)
    return query.order_by(Movimentacao.criado_em.desc()).offset(skip).limit(limit).all()