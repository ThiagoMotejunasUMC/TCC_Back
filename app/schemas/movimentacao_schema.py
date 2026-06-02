from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MovimentacaoCreate(BaseModel):
    item_id: int
    tipo: str  # entrada, saida
    motivo: Optional[str] = None  # compra, venda, devolucao, ajuste, descarte, manutencao
    observacao: Optional[str] = None

class MovimentacaoResponse(BaseModel):
    id: int
    item_id: int
    usuario_id: int
    tipo: str
    motivo: Optional[str]
    status_anterior: Optional[str]
    status_novo: Optional[str]
    observacao: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True