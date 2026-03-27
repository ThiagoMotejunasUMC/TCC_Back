from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    cargo: Optional[str] = "operador"

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    cargo: Optional[str] = None
    ativo: Optional[bool] = None

class UsuarioUpdateSenha(BaseModel):
    senha_atual: str
    nova_senha: str

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    cargo: str
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True