from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.variacao_schema import VariacaoResponse

class ProdutoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    fornecedor_id: Optional[int] = None

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    fornecedor_id: Optional[int] = None

class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    categoria: Optional[str]
    fornecedor_id: Optional[int]
    criado_em: datetime
    variacoes: List[VariacaoResponse] = []

    class Config:
        from_attributes = True