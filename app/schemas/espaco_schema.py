from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EspacoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    largura_cm: float
    altura_cm: float
    profundidade_cm: float
    peso_max_kg: float

class EspacoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    largura_cm: Optional[float] = None
    altura_cm: Optional[float] = None
    profundidade_cm: Optional[float] = None
    peso_max_kg: Optional[float] = None
    ativo: Optional[bool] = None

class EspacoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    largura_cm: float
    altura_cm: float
    profundidade_cm: float
    peso_max_kg: float
    volume_total_m3: float
    volume_ocupado_m3: float
    peso_ocupado_kg: float
    percentual_volume: float
    percentual_peso: float
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True

class EspacoOcupacao(BaseModel):
    espaco_id: int
    espaco_nome: str
    volume_total_m3: float
    volume_ocupado_m3: float
    peso_max_kg: float
    peso_ocupado_kg: float
    percentual_volume: float
    percentual_peso: float
    alerta_volume: bool
    alerta_peso: bool
    critico_volume: bool
    critico_peso: bool