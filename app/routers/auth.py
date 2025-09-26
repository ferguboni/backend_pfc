"""
Rotas de autenticação:
- /auth/register
- /auth/login
- /auth/forgot-password
- /auth/reset-password
"""
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User, PasswordReset
from app.db import models
from app.db.schemas import (
    UserCreate,
    UserOut,
    TokenOut,
    ForgotPasswordIn,
    ResetPasswordIn,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    sha256_hex,
)
from app.services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])

# === ENVs ===
FRONTEND_RESET_URL = os.getenv("FRONTEND_RESET_URL", "http://localhost:3000/resetar-senha")
RESET_TOKEN_TTL_MIN = int(os.getenv("RESET_TOKEN_TTL_MIN", "30"))

# Flags de debug (para testes)
DEBUG_RETURN_RESET_LINK = os.getenv("DEBUG_RETURN_RESET_LINK", "false").lower() == "true"
DEBUG_SYNC_EMAIL = os.getenv("DEBUG_SYNC_EMAIL", "false").lower() == "true"


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    exists = db.query(models.User).filter(models.User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    user = models.User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login(payload: UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = create_access_token(str(user.id))
    return {"access_token": token}


@router.post("/forgot-password", summary="Solicitar reset de senha (sempre 200)")
async def forgot_password(payload: ForgotPasswordIn, background: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Idempotente: sempre retorna 200.
    Em DEBUG, devolve debug_reset_link e não deixa a exceção do SMTP virar 500.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        raw_token = secrets.token_urlsafe(32)
        token_hash = sha256_hex(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_TTL_MIN)

        pr = PasswordReset(user_id=user.id, token_hash=token_hash, expires_at=expires_at)
        db.add(pr)
        db.commit()

        link = f"{FRONTEND_RESET_URL}?token={raw_token}"
        html = f"""
        <p>Olá{f", {user.name}" if getattr(user, 'name', None) else ''}!</p>
        <p>Use o link abaixo para redefinir sua senha (válido por {RESET_TOKEN_TTL_MIN} minutos):</p>
        <p><a href="{link}">Redefinir senha</a></p>
        <p>Se você não solicitou, ignore este e-mail.</p>
        """

        # --- DEBUG: retorna link e captura erro de e-mail sem 500 ---
        if DEBUG_RETURN_RESET_LINK:
            if DEBUG_SYNC_EMAIL:
                try:
                    await send_email(to=user.email, subject="Redefinição de senha", html=html)
                    return {"debug_reset_link": link, "email_status": "sent"}
                except Exception as e:
                    return {"debug_reset_link": link, "email_status": "error", "email_error": str(e)}
            else:
                background.add_task(send_email, to=user.email, subject="Redefinição de senha", html=html)
                return {"debug_reset_link": link, "email_status": "queued"}

        # --- PRODUÇÃO: envio em background ---
        background.add_task(send_email, to=user.email, subject="Redefinição de senha", html=html)

    return {"message": "Se o e-mail existir, enviaremos um link de redefinição."}


@router.post("/reset-password", summary="Aplicar nova senha a partir do token")
async def reset_password(payload: ResetPasswordIn, db: Session = Depends(get_db)):
    try:
        now = datetime.now(timezone.utc)
        token_hash = sha256_hex(payload.token)

        pr = (
            db.query(PasswordReset)
            .filter(PasswordReset.token_hash == token_hash)
            .filter(PasswordReset.used_at.is_(None))
            .filter(PasswordReset.expires_at > now)
            .first()
        )
        if not pr:
            raise HTTPException(status_code=400, detail="Token inválido ou expirado")

        user = db.query(User).filter(User.id == pr.user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="Usuário não encontrado")

        # aplica nova senha
        user.password_hash = hash_password(payload.new_password)
        pr.used_at = now

        # invalida outros tokens pendentes
        db.query(PasswordReset).filter(
            PasswordReset.user_id == user.id,
            PasswordReset.used_at.is_(None),
            PasswordReset.id != pr.id,
        ).update(
            {PasswordReset.used_at: now},
            synchronize_session=False,   # <- evita erro no SQLAlchemy 2.0
        )

        db.commit()
        return {"message": "Senha redefinida com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao resetar senha: {str(e)}")
