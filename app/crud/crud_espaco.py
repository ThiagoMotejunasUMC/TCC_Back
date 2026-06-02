from sqlalchemy.orm import Session
from app.models.espaco_model import Espaco
from app.schemas.espaco_schema import EspacoCreate, EspacoUpdate, EspacoOcupacao
from app.crud.crud_audit import registrar_log
from typing import Optional, List

def criar_espaco(db: Session, data: EspacoCreate, usuario_id: int = None) -> Espaco:
    espaco = Espaco(**data.model_dump())
    db.add(espaco)
    db.commit()
    db.refresh(espaco)
    if usuario_id:
        registrar_log(db, usuario_id, "CREATE", "espaco", espaco.id, f"Espaço criado: {espaco.nome}")
    return espaco

def listar_espacos(db: Session, apenas_ativos: bool = True) -> List[Espaco]:
    query = db.query(Espaco)
    if apenas_ativos:
        query = query.filter(Espaco.ativo == True)
    return query.all()

def obter_espaco(db: Session, espaco_id: int) -> Optional[Espaco]:
    return db.query(Espaco).filter(Espaco.id == espaco_id).first()

def atualizar_espaco(db: Session, espaco_id: int, data: EspacoUpdate, usuario_id: int = None) -> Optional[Espaco]:
    espaco = obter_espaco(db, espaco_id)
    if not espaco:
        return None
    campos = data.model_dump(exclude_unset=True)
    for campo, valor in campos.items():
        setattr(espaco, campo, valor)
    db.commit()
    db.refresh(espaco)
    if usuario_id:
        registrar_log(db, usuario_id, "UPDATE", "espaco", espaco.id, f"Campos atualizados: {list(campos.keys())}")
    return espaco

def deletar_espaco(db: Session, espaco_id: int, usuario_id: int = None) -> Optional[Espaco]:
    espaco = obter_espaco(db, espaco_id)
    if not espaco:
        return None
    espaco.ativo = False
    db.commit()
    db.refresh(espaco)
    if usuario_id:
        registrar_log(db, usuario_id, "DELETE", "espaco", espaco.id, f"Espaço desativado: {espaco.nome}")
    return espaco

def obter_ocupacao(db: Session, espaco_id: int) -> Optional[EspacoOcupacao]:
    espaco = obter_espaco(db, espaco_id)
    if not espaco:
        return None
    return EspacoOcupacao(
        espaco_id=espaco.id,
        espaco_nome=espaco.nome,
        volume_total_m3=round(espaco.volume_total_m3, 6),
        volume_ocupado_m3=round(espaco.volume_ocupado_m3, 6),
        peso_max_kg=espaco.peso_max_kg,
        peso_ocupado_kg=round(espaco.peso_ocupado_kg, 3),
        percentual_volume=round(espaco.percentual_volume, 2),
        percentual_peso=round(espaco.percentual_peso, 2),
        alerta_volume=espaco.percentual_volume >= 80,
        alerta_peso=espaco.percentual_peso >= 80,
        critico_volume=espaco.percentual_volume >= 100,
        critico_peso=espaco.percentual_peso >= 100,
    )

def verificar_capacidade_item(db: Session, espaco_id: int, volume_m3: float, peso_kg: float) -> dict:
    espaco = obter_espaco(db, espaco_id)
    if not espaco:
        return {"valido": False, "erro": "Espaço não encontrado"}
    novo_volume = espaco.volume_ocupado_m3 + volume_m3
    novo_peso = espaco.peso_ocupado_kg + peso_kg
    if novo_volume > espaco.volume_total_m3:
        return {
            "valido": False,
            "erro": f"Volume insuficiente. Disponível: {round((espaco.volume_total_m3 - espaco.volume_ocupado_m3) * 1_000_000, 2)} cm³"
        }
    if novo_peso > espaco.peso_max_kg:
        return {
            "valido": False,
            "erro": f"Peso máximo excedido. Disponível: {round(espaco.peso_max_kg - espaco.peso_ocupado_kg, 3)} kg"
        }
    return {"valido": True}