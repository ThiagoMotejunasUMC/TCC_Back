from sqlalchemy.orm import Session
from app.models.audit_model import AuditLog


def registrar_log(
    db: Session,
    usuario_id: int,
    acao: str,
    entidade: str,
    entidade_id: int | None = None,
    detalhe: str | None = None,
):
    log = AuditLog(
        usuario_id=usuario_id,
        acao=acao,
        entidade=entidade,
        entidade_id=entidade_id,
        detalhe=detalhe,
    )
    db.add(log)
    db.commit()
    return log