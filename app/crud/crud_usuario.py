from sqlalchemy.orm import Session
from app.models.usuario_model import Usuario
from app.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioUpdateSenha
from app.core.security import hash_password, verify_password, validate_password_strength
from fastapi import HTTPException, status

def criar_usuario(db: Session, data: UsuarioCreate):
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
    return usuario

def listar_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Usuario).offset(skip).limit(limit).all()

def obter_usuario_por_id(db: Session, usuario_id: int):
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

def obter_usuario_por_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def atualizar_usuario(db: Session, usuario_id: int, data: UsuarioUpdate):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(usuario, field, value)
    db.commit()
    db.refresh(usuario)
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
    return usuario

def deletar_usuario(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    db.delete(usuario)
    db.commit()
    return usuario