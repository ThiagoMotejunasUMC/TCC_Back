from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FornecedorCreate(BaseModel):
    nome: str
    cnpj: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None

class FornecedorUpdate(BaseModel):
    nome: Optional[str] = None
    cnpj: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None

class FornecedorResponse(BaseModel):
    id: int
    nome: str
    cnpj: Optional[str]
    email: Optional[str]
    telefone: Optional[str]
    cep: Optional[str]
    logradouro: Optional[str]
    numero: Optional[str]
    bairro: Optional[str]
    cidade: Optional[str]
    estado: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True