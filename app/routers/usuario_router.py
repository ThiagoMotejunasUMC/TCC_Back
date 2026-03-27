from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, require_admin
from app.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioUpdateSenha, UsuarioResponse
from app.crud import crud_usuario
from app.models.usuario_model import Usuario
from typing import List

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@router.post("/", response_model=UsuarioResponse)
def criar_usuario(data: UsuarioCreate, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    return crud_usuario.criar_usuario(db, data)

@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    return crud_usuario.listar_usuarios(db, skip, limit)

@router.get("/me", response_model=UsuarioResponse)
def obter_meu_perfil(current_user: Usuario = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UsuarioResponse)
def atualizar_meu_perfil(data: UsuarioUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    data_sem_cargo = data.model_dump(exclude_unset=True)
    data_sem_cargo.pop("cargo", None)
    data_sem_cargo.pop("ativo", None)
    from app.schemas.usuario_schema import UsuarioUpdate
    return crud_usuario.atualizar_usuario(db, current_user.id, UsuarioUpdate(**data_sem_cargo))

@router.put("/me/senha")
def atualizar_minha_senha(data: UsuarioUpdateSenha, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    crud_usuario.atualizar_senha(db, current_user, data)
    return {"mensagem": "Senha atualizada com sucesso"}

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(usuario_id: int, data: UsuarioUpdate, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    return crud_usuario.atualizar_usuario(db, usuario_id, data)

@router.delete("/{usuario_id}", response_model=UsuarioResponse)
def deletar_usuario(usuario_id: int, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    return crud_usuario.deletar_usuario(db, usuario_id)