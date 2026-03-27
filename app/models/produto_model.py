from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    categoria = Column(String, nullable=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    fornecedor = relationship("Fornecedor", back_populates="produtos")
    variacoes = relationship("Variacao", back_populates="produto", cascade="all, delete-orphan")