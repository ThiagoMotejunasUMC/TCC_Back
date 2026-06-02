from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CategoriaCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None

class CategoriaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None

class CategoriaResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True