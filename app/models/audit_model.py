from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    acao = Column(String, nullable=False)       # ex: "criar_produto"
    entidade = Column(String, nullable=False)   # ex: "produto"
    entidade_id = Column(Integer, nullable=True)
    detalhe = Column(String, nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    usuario = relationship("Usuario", back_populates="audit_logs")