from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificacaoResponse(BaseModel):
    id: int
    usuario_id: int
    titulo: str
    mensagem: str
    tipo: str
    lida: bool
    criado_em: datetime

    class Config:
        from_attributes = True

class NotificacaoUpdate(BaseModel):
    lida: bool = True