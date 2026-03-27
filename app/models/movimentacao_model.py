from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    variacao_id = Column(Integer, ForeignKey("variacoes.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo = Column(String, nullable=False)  # "entrada" ou "saida"
    motivo = Column(String, nullable=True)  # compra, devolucao, ajuste, descarte
    quantidade = Column(Integer, nullable=False)
    observacao = Column(String, nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    variacao = relationship("Variacao", back_populates="movimentacoes")
    usuario = relationship("Usuario", back_populates="movimentacoes")