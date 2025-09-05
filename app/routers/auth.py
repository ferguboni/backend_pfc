"""
Rotas de autenticação:
- /auth/register: cria usuário com e-mail/senha
- /auth/login: retorna token JWT AAAAAAAAAAAAAAAAAAAA
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.db.schemas import UserCreate, UserOut, TokenOut
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Cria usuário novo com e-mail e senha.
    - Se e-mail já existir, retorna 400.
    """
    exists = db.query(models.User).filter(models.User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    user = models.User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenOut)
def login(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Faz login com e-mail/senha.
    Retorna um token JWT para usar nas rotas protegidas (Authorization: Bearer <token>).
    """
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = create_access_token(str(user.id))
    return {"access_token": token}
