from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Item(Base):
    __tablename__ = "itens"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    espaco_id = Column(Integer, ForeignKey("espacos.id"), nullable=True)
    numero_serie = Column(String, unique=True, nullable=False)
    cor = Column(String, nullable=True)
    voltagem = Column(String, nullable=True)  # 110v, 220v, bivolt
    condicao = Column(String, default="novo")  # novo, seminovo, recondicionado, em_manutencao, danificado, mostruario
    altura_cm = Column(Float, nullable=True)
    largura_cm = Column(Float, nullable=True)
    profundidade_cm = Column(Float, nullable=True)
    peso_kg = Column(Float, nullable=True)
    preco_custo = Column(Float, nullable=False)
    preco_venda = Column(Float, nullable=False)
    status = Column(String, default="disponivel")  # disponivel, vendido, danificado, em_manutencao, mostruario
    localizacao = Column(String, nullable=True)
    observacao = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    produto = relationship("Produto", back_populates="itens")
    espaco = relationship("Espaco", back_populates="itens")
    movimentacoes = relationship("Movimentacao", back_populates="item")

    @property
    def volume_m3(self):
        if self.altura_cm and self.largura_cm and self.profundidade_cm:
            return (self.altura_cm * self.largura_cm * self.profundidade_cm) / 1_000_000
        return 0.0