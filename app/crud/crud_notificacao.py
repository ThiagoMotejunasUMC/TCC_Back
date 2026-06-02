from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.notificacao_model import Notificacao
from typing import List

def listar_notificacoes(db: Session, usuario_id: int, apenas_nao_lidas: bool = False) -> List[Notificacao]:
    query = db.query(Notificacao).filter(Notificacao.usuario_id == usuario_id)
    if apenas_nao_lidas:
        query = query.filter(Notificacao.lida == False)
    return query.order_by(Notificacao.criado_em.desc()).limit(500).all()

def contar_nao_lidas(db: Session, usuario_id: int) -> int:
    return db.query(Notificacao).filter(
        and_(Notificacao.usuario_id == usuario_id, Notificacao.lida == False)
    ).count()

def marcar_como_lida(db: Session, notificacao_id: int, usuario_id: int) -> bool:
    notif = db.query(Notificacao).filter(
        and_(Notificacao.id == notificacao_id, Notificacao.usuario_id == usuario_id)
    ).first()
    if not notif:
        return False
    notif.lida = True
    db.commit()
    return True

def marcar_todas_como_lidas(db: Session, usuario_id: int):
    db.query(Notificacao).filter(
        and_(Notificacao.usuario_id == usuario_id, Notificacao.lida == False)
    ).update({"lida": True})
    db.commit()

def limpar_lidas(db: Session, usuario_id: int):
    db.query(Notificacao).filter(
        and_(Notificacao.usuario_id == usuario_id, Notificacao.lida == True)
    ).delete()
    db.commit()