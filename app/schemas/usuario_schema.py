from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re

def validar_senha(senha: str) -> str:
    if len(senha) < 8:
        raise ValueError("Senha deve ter no mínimo 8 caracteres")
    if not re.search(r"[A-Z]", senha):
        raise ValueError("Senha deve ter pelo menos uma letra maiúscula")
    if not re.search(r"[a-z]", senha):
        raise ValueError("Senha deve ter pelo menos uma letra minúscula")
    if not re.search(r"\d", senha):
        raise ValueError("Senha deve ter pelo menos um número")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        raise ValueError("Senha deve ter pelo menos um caractere especial")
    return senha

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    cargo: Optional[str] = "operador"

    @field_validator("senha")
    @classmethod
    def senha_forte(cls, v):
        return validar_senha(v)

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    cargo: Optional[str] = None
    ativo: Optional[bool] = None

class UsuarioUpdateSenha(BaseModel):
    senha_atual: str
    nova_senha: str

    @field_validator("nova_senha")
    @classmethod
    def senha_forte(cls, v):
        return validar_senha(v)

class UsuarioUpdatePrimeiroAcesso(BaseModel):
    nova_senha: str

    @field_validator("nova_senha")
    @classmethod
    def senha_forte(cls, v):
        return validar_senha(v)

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    cargo: str
    ativo: bool
    primeiro_acesso: bool
    criado_em: datetime

    class Config:
        from_attributes = True