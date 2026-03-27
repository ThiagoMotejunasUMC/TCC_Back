from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Variacao(Base):
    __tablename__ = "variacoes"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    sku = Column(String, unique=True, nullable=False)
    cor = Column(String, nullable=True)
    atributos = Column(String, nullable=True)  # ex: "256GB"
    preco = Column(Float, nullable=False)
    quantidade_estoque = Column(Integer, default=0)
    estoque_minimo = Column(Integer, default=5)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    produto = relationship("Produto", back_populates="variacoes")
    movimentacoes = relationship("Movimentacao", back_populates="variacao")

    @property
    def alerta_estoque(self):
        return self.quantidade_estoque <= self.estoque_minimo