from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VariacaoCreate(BaseModel):
    produto_id: int
    sku: str
    cor: Optional[str] = None
    atributos: Optional[str] = None
    preco: float
    quantidade_estoque: Optional[int] = 0
    estoque_minimo: Optional[int] = 5

class VariacaoUpdate(BaseModel):
    sku: Optional[str] = None
    cor: Optional[str] = None
    atributos: Optional[str] = None
    preco: Optional[float] = None
    estoque_minimo: Optional[int] = None
    ativo: Optional[bool] = None

class VariacaoResponse(BaseModel):
    id: int
    produto_id: int
    sku: str
    cor: Optional[str]
    atributos: Optional[str]
    preco: float
    quantidade_estoque: int
    estoque_minimo: int
    ativo: bool
    alerta_estoque: bool
    criado_em: datetime

    class Config:
        from_attributes = True