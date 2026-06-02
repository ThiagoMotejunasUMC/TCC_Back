from sqlalchemy.orm import Session
from app.models.usuario_model import Usuario
from app.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioUpdateSenha
from app.core.security import hash_password, verify_password, validate_password_strength
from app.crud.crud_audit import registrar_log
from fastapi import HTTPException, status

def criar_usuario(db: Session, data: UsuarioCreate, usuario_id: int = None):
    if not validate_password_strength(data.senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha deve ter no mínimo 8 caracteres, letra maiúscula, minúscula, número e caractere especial"
        )
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")
    usuario = Usuario(
        nome=data.nome,
        email=data.email,
        senha=hash_password(data.senha),
        cargo=data.cargo or "operador"
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    if usuario_id:
        registrar_log(db, usuario_id, "CREATE", "usuario", usuario.id, f"Usuário criado: {usuario.email} — cargo: {usuario.cargo}")
    return usuario

def listar_usuarios(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(Usuario).offset(skip).limit(limit).all()

def obter_usuario_por_id(db: Session, usuario_id: int):
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

def obter_usuario_por_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def atualizar_usuario(db: Session, usuario_id: int, data: UsuarioUpdate, executor_id: int = None):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    campos = data.model_dump(exclude_unset=True)
    for field, value in campos.items():
        setattr(usuario, field, value)
    db.commit()
    db.refresh(usuario)
    if executor_id:
        registrar_log(db, executor_id, "UPDATE", "usuario", usuario.id, f"Campos atualizados: {list(campos.keys())}")
    return usuario

def atualizar_senha(db: Session, usuario: Usuario, data: UsuarioUpdateSenha):
    if not verify_password(data.senha_atual, usuario.senha):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta")
    if not validate_password_strength(data.nova_senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha deve ter no mínimo 8 caracteres, letra maiúscula, minúscula, número e caractere especial"
        )
    usuario.senha = hash_password(data.nova_senha)
    db.commit()
    db.refresh(usuario)
    registrar_log(db, usuario.id, "UPDATE", "usuario", usuario.id, "Senha alterada pelo próprio usuário")
    return usuario

def deletar_usuario(db: Session, usuario_id: int, executor_id: int = None):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    usuario.ativo = False
    db.commit()
    db.refresh(usuario)
    if executor_id:
        registrar_log(db, executor_id, "DELETE", "usuario", usuario.id, f"Usuário desativado: {usuario.email}")
    return usuario