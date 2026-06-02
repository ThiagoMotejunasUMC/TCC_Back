from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.item_model import Item
from app.models.produto_model import Produto
from app.models.notificacao_model import Notificacao
from app.models.usuario_model import Usuario
from app.schemas.item_schema import ItemCreate, ItemUpdate, AlertaEstoque
from app.core.email import enviar_email_alerta_estoque
from app.crud.crud_audit import registrar_log
from typing import Optional, List
from datetime import datetime, timezone

def criar_item(db: Session, data: ItemCreate, usuario_id: int = None) -> Item:
    item = Item(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    if usuario_id:
        registrar_log(db, usuario_id, "CREATE", "item", item.id, f"Item criado: {item.numero_serie}")
    verificar_e_notificar_estoque(db, item.produto_id)
    return item

def listar_itens(
    db: Session,
    produto_id: Optional[int] = None,
    espaco_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 10000
) -> List[Item]:
    query = db.query(Item).filter(Item.ativo == True)
    if produto_id:
        query = query.filter(Item.produto_id == produto_id)
    if espaco_id:
        query = query.filter(Item.espaco_id == espaco_id)
    if status:
        query = query.filter(Item.status == status)
    return query.offset(skip).limit(limit).all()

def obter_item(db: Session, item_id: int) -> Optional[Item]:
    return db.query(Item).filter(Item.id == item_id).first()

def atualizar_item(db: Session, item_id: int, data: ItemUpdate, usuario_id: int = None) -> Optional[Item]:
    item = obter_item(db, item_id)
    if not item:
        return None
    campos = data.model_dump(exclude_unset=True)
    for campo, valor in campos.items():
        setattr(item, campo, valor)
    item.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    if usuario_id:
        registrar_log(db, usuario_id, "UPDATE", "item", item.id, f"Campos atualizados: {list(campos.keys())}")
    return item

def deletar_item(db: Session, item_id: int, usuario_id: int = None) -> Optional[Item]:
    item = obter_item(db, item_id)
    if not item:
        return None
    item.ativo = False
    item.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    if usuario_id:
        registrar_log(db, usuario_id, "DELETE", "item", item.id, f"Item desativado: {item.numero_serie}")
    return item

def listar_alertas_estoque(db: Session) -> List[AlertaEstoque]:
    produtos = db.query(Produto).filter(Produto.ativo == True).all()
    alertas = []
    for produto in produtos:
        disponiveis = db.query(Item).filter(
            and_(Item.produto_id == produto.id, Item.status == "disponivel", Item.ativo == True)
        ).count()
        if disponiveis <= produto.estoque_minimo:
            alertas.append(AlertaEstoque(
                produto_id=produto.id,
                produto_nome=produto.nome,
                quantidade_disponivel=disponiveis,
                estoque_minimo=produto.estoque_minimo
            ))
    return alertas

def verificar_e_notificar_estoque(db: Session, produto_id: int):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        return
    disponiveis = db.query(Item).filter(
        and_(Item.produto_id == produto_id, Item.status == "disponivel", Item.ativo == True)
    ).count()
    if disponiveis <= produto.estoque_minimo:
        titulo = f"Alerta de estoque: {produto.nome}"
        mensagem = f"O produto '{produto.nome}' possui apenas {disponiveis} unidade(s) disponível(is), abaixo do mínimo configurado de {produto.estoque_minimo}."
        usuarios_notificar = db.query(Usuario).filter(
            and_(Usuario.ativo == True, Usuario.cargo.in_(["admin", "diretor"]))
        ).all()
        for usuario in usuarios_notificar:
            notif_existente = db.query(Notificacao).filter(
                and_(
                    Notificacao.usuario_id == usuario.id,
                    Notificacao.titulo == titulo,
                    Notificacao.lida == False
                )
            ).first()
            if not notif_existente:
                notificacao = Notificacao(
                    usuario_id=usuario.id,
                    titulo=titulo,
                    mensagem=mensagem,
                    tipo="alerta"
                )
                db.add(notificacao)
                try:
                    enviar_email_alerta_estoque(
                        usuario.email, usuario.nome,
                        produto.nome, disponiveis, produto.estoque_minimo
                    )
                except Exception as e:
                    print(f"Erro ao enviar e-mail para {usuario.email}: {e}")
        db.commit()