from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MovimentacaoCreate(BaseModel):
    variacao_id: int
    tipo: str  # "entrada" ou "saida"
    motivo: Optional[str] = None  # compra, devolucao, ajuste, descarte
    quantidade: int
    observacao: Optional[str] = None

class MovimentacaoResponse(BaseModel):
    id: int
    variacao_id: int
    usuario_id: int
    tipo: str
    motivo: Optional[str]
    quantidade: int
    observacao: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True