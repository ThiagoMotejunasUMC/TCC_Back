from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("itens.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo = Column(String, nullable=False)  # entrada, saida
    motivo = Column(String, nullable=True)  # compra, venda, devolucao, ajuste, descarte, manutencao
    status_anterior = Column(String, nullable=True)
    status_novo = Column(String, nullable=True)
    observacao = Column(String, nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    item = relationship("Item", back_populates="movimentacoes")
    usuario = relationship("Usuario", back_populates="movimentacoes")