from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Espaco(Base):
    __tablename__ = "espacos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    largura_cm = Column(Float, nullable=False)
    altura_cm = Column(Float, nullable=False)
    profundidade_cm = Column(Float, nullable=False)
    peso_max_kg = Column(Float, nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    itens = relationship("Item", back_populates="espaco")

    @property
    def volume_total_m3(self):
        return (self.largura_cm * self.altura_cm * self.profundidade_cm) / 1000000

    @property
    def volume_ocupado_m3(self):
        return sum(i.volume_m3 for i in self.itens if i.ativo and i.volume_m3)

    @property
    def peso_ocupado_kg(self):
        return sum(i.peso_kg for i in self.itens if i.ativo and i.peso_kg)

    @property
    def percentual_volume(self):
        if self.volume_total_m3 == 0:
            return 0.0
        return min((self.volume_ocupado_m3 / self.volume_total_m3) * 100, 100.0)

    @property
    def percentual_peso(self):
        if self.peso_max_kg == 0:
            return 0.0
        return min((self.peso_ocupado_kg / self.peso_max_kg) * 100, 100.0)