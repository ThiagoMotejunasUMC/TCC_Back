from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ItemCreate(BaseModel):
    produto_id: int
    espaco_id: Optional[int] = None
    numero_serie: str
    cor: Optional[str] = None
    voltagem: Optional[str] = None
    condicao: Optional[str] = "novo"
    altura_cm: Optional[float] = None
    largura_cm: Optional[float] = None
    profundidade_cm: Optional[float] = None
    peso_kg: Optional[float] = None
    preco_custo: float
    preco_venda: float
    status: Optional[str] = "disponivel"
    localizacao: Optional[str] = None
    observacao: Optional[str] = None

class ItemUpdate(BaseModel):
    espaco_id: Optional[int] = None
    cor: Optional[str] = None
    voltagem: Optional[str] = None
    condicao: Optional[str] = None
    altura_cm: Optional[float] = None
    largura_cm: Optional[float] = None
    profundidade_cm: Optional[float] = None
    peso_kg: Optional[float] = None
    preco_custo: Optional[float] = None
    preco_venda: Optional[float] = None
    status: Optional[str] = None
    localizacao: Optional[str] = None
    observacao: Optional[str] = None
    ativo: Optional[bool] = None

class ItemResponse(BaseModel):
    id: int
    produto_id: int
    espaco_id: Optional[int] = None
    numero_serie: str
    cor: Optional[str] = None
    voltagem: Optional[str] = None
    condicao: str
    altura_cm: Optional[float] = None
    largura_cm: Optional[float] = None
    profundidade_cm: Optional[float] = None
    peso_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    preco_custo: float
    preco_venda: float
    status: str
    localizacao: Optional[str] = None
    observacao: Optional[str] = None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True

class AlertaEstoque(BaseModel):
    produto_id: int
    produto_nome: str
    quantidade_disponivel: int
    estoque_minimo: int