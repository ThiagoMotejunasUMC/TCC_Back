from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.item_schema import ItemResponse

class ProdutoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    modelo: Optional[str] = None
    marca: Optional[str] = None
    categoria_id: Optional[int] = None
    fornecedor_id: Optional[int] = None
    estoque_minimo: Optional[int] = 5
    garantia_meses: Optional[int] = None

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    modelo: Optional[str] = None
    marca: Optional[str] = None
    categoria_id: Optional[int] = None
    fornecedor_id: Optional[int] = None
    estoque_minimo: Optional[int] = None
    garantia_meses: Optional[int] = None
    ativo: Optional[bool] = None

class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    modelo: Optional[str]
    marca: Optional[str]
    categoria_id: Optional[int]
    fornecedor_id: Optional[int]
    estoque_minimo: int
    garantia_meses: Optional[int]
    ativo: bool
    criado_em: datetime
    itens: List[ItemResponse] = []

    class Config:
        from_attributes = True