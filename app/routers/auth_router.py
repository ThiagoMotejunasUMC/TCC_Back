from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.auth_schema import (
    LoginRequest, TokenResponse, RefreshRequest,
    EsqueciSenhaRequest, RedefinirSenhaRequest
)
from app.schemas.usuario_schema import UsuarioUpdatePrimeiroAcesso
from app.crud.crud_usuario import obter_usuario_por_email
from app.core.security import (
    verify_password, create_access_token, create_refresh_token,
    verify_token, validate_password_strength, hash_password
)
from app.core.email import enviar_email_recuperacao
from app.core.config import settings
from app.models.password_reset_model import PasswordResetToken
from datetime import timedelta, datetime, timezone
import secrets

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    usuario = obter_usuario_por_email(db, data.email)
    if not usuario or not verify_password(data.password, usuario.senha):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha incorretos")
    if not usuario.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo")
    access_token = create_access_token(
        data={"sub": str(usuario.id), "cargo": usuario.cargo, "primeiro_acesso": usuario.primeiro_acesso},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(data={"sub": str(usuario.id)})
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        primeiro_acesso=usuario.primeiro_acesso
    )

@router.post("/primeiro-acesso")
def primeiro_acesso(data: UsuarioUpdatePrimeiroAcesso, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    if not usuario.primeiro_acesso:
        raise HTTPException(status_code=400, detail="Usuário já realizou o primeiro acesso")
    if not validate_password_strength(data.nova_senha):
        raise HTTPException(status_code=400, detail="A senha não atende aos requisitos de complexidade")
    usuario.senha = hash_password(data.nova_senha)
    usuario.primeiro_acesso = False
    db.commit()
    return {"mensagem": "Senha definida com sucesso! Faça login novamente."}

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
        data={"sub": str(usuario.id), "cargo": usuario.cargo, "primeiro_acesso": usuario.primeiro_acesso},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(data={"sub": str(usuario.id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, primeiro_acesso=usuario.primeiro_acesso)

@router.post("/esqueci-senha")
def esqueci_senha(data: EsqueciSenhaRequest, db: Session = Depends(get_db)):
    usuario = obter_usuario_por_email(db, data.email)
    if not usuario or not usuario.ativo:
        return {"mensagem": "Se o e-mail estiver cadastrado, você receberá as instruções em breve."}
    db.query(PasswordResetToken).filter(
        PasswordResetToken.usuario_id == usuario.id,
        PasswordResetToken.usado == False
    ).delete()
    db.commit()
    token = secrets.token_urlsafe(32)
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=30)
    reset_token = PasswordResetToken(usuario_id=usuario.id, token=token, expira_em=expira_em)
    db.add(reset_token)
    db.commit()
    enviar_email_recuperacao(usuario.email, usuario.nome, token)
    return {"mensagem": "Se o e-mail estiver cadastrado, você receberá as instruções em breve."}

@router.post("/redefinir-senha")
def redefinir_senha(data: RedefinirSenhaRequest, db: Session = Depends(get_db)):
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == data.token,
        PasswordResetToken.usado == False
    ).first()
    if not reset_token:
        raise HTTPException(status_code=400, detail="Token inválido ou já utilizado")
    expira_em = reset_token.expira_em
    if expira_em.tzinfo is None:
        expira_em = expira_em.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expira_em:
        raise HTTPException(status_code=400, detail="Token expirado. Solicite uma nova recuperação de senha.")
    if not validate_password_strength(data.nova_senha):
        raise HTTPException(status_code=400, detail="A senha não atende aos requisitos de complexidade")
    usuario = reset_token.usuario
    usuario.senha = hash_password(data.nova_senha)
    reset_token.usado = True
    db.commit()
    return {"mensagem": "Senha redefinida com sucesso!"}