from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.auth_schema import LoginRequest, TokenResponse, RefreshRequest
from app.crud.crud_usuario import obter_usuario_por_email
from app.core.security import verify_password, create_access_token, create_refresh_token, verify_token
from datetime import timedelta
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    usuario = obter_usuario_por_email(db, data.email)
    if not usuario or not verify_password(data.password, usuario.senha):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha incorretos")
    if not usuario.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo")
    access_token = create_access_token(
        data={"sub": str(usuario.id), "cargo": usuario.cargo},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(data={"sub": str(usuario.id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    payload = verify_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido")
    from app.models.usuario_model import Usuario
    usuario = db.query(Usuario).filter(Usuario.id == int(payload.get("sub"))).first()
    if not usuario or not usuario.ativo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado ou inativo")
    access_token = create_access_token(
        data={"sub": str(usuario.id), "cargo": usuario.cargo},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(data={"sub": str(usuario.id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)