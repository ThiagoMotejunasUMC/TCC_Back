from sqlalchemy.orm import Session
from app.models.movimentacao_model import Movimentacao
from app.models.variacao_model import Variacao
from app.schemas.movimentacao_schema import MovimentacaoCreate
from fastapi import HTTPException, status

def registrar_movimentacao(db: Session, data: MovimentacaoCreate, usuario_id: int):
    variacao = db.query(Variacao).filter(Variacao.id == data.variacao_id).first()
    if not variacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variação não encontrada")

    if data.tipo == "saida":
        if variacao.quantidade_estoque < data.quantidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente. Disponível: {variacao.quantidade_estoque}"
            )
        variacao.quantidade_estoque -= data.quantidade
    elif data.tipo == "entrada":
        variacao.quantidade_estoque += data.quantidade
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo deve ser 'entrada' ou 'saida'")

    movimentacao = Movimentacao(
        variacao_id=data.variacao_id,
        usuario_id=usuario_id,
        tipo=data.tipo,
        motivo=data.motivo,
        quantidade=data.quantidade,
        observacao=data.observacao
    )
    db.add(movimentacao)
    db.commit()
    db.refresh(movimentacao)
    return movimentacao

def listar_movimentacoes(db: Session, skip: int = 0, limit: int = 100, tipo: str = None, variacao_id: int = None):
    query = db.query(Movimentacao)
    if tipo:
        query = query.filter(Movimentacao.tipo == tipo)
    if variacao_id:
        query = query.filter(Movimentacao.variacao_id == variacao_id)
    return query.order_by(Movimentacao.criado_em.desc()).offset(skip).limit(limit).all()