# app/core/security.py
# Utilitários de segurança:
# - Hash/verify de senha (Passlib/bcrypt) com limite de 72 bytes
# - Criação/validação de JWT (PyJWT)
# - SHA-256 utilitário para tokens

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
import hashlib
from app.core.config import settings

# Contexto de hashing (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _bcrypt_safe(text: str) -> str:
    """
    Garante que a string respeite o limite de 72 bytes do bcrypt.
    Trunca com segurança se necessário.
    """
    if not isinstance(text, str):
        text = str(text)
    data = text.encode("utf-8")
    if len(data) > 72:
        data = data[:72]
        # evita cortar no meio de um caractere multibyte
        text = data.decode("utf-8", errors="ignore")
    return text


# ===== Senhas =====
def hash_password(password: str) -> str:
    """Gera hash bcrypt (com truncamento seguro a 72 bytes)."""
    return pwd_context.hash(_bcrypt_safe(password))


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica senha vs hash (aplica truncamento seguro antes)."""
    return pwd_context.verify(_bcrypt_safe(password), password_hash)


# ===== JWT =====
def create_access_token(subject: str) -> str:
    """Gera um token JWT com expiração em minutos definida no .env."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRES_MIN
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    """Decodifica e valida um token JWT."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])


# ===== Utilitário SHA-256 (para tokens de reset, etc.) =====
def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
