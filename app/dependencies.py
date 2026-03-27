from sqlalchemy.orm import Session
from app.database import SessionLocal
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_token
from app.models.usuario_model import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")
    user = db.query(Usuario).filter(Usuario.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
    return user

def require_admin(current_user: Usuario = Depends(get_current_user)):
    if current_user.cargo != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a administradores")
    return current_user

def require_diretor(current_user: Usuario = Depends(get_current_user)):
    if current_user.cargo not in ["admin", "diretor"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a diretores e administradores")
    return current_user