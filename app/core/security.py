# app/core/security.py
# Segurança:
# - Hash/verify de senha com Passlib bcrypt (truncate_error=False)
# - Truncamento seguro p/ 72 bytes (limite do bcrypt)
# - JWT (PyJWT) e utilitário SHA-256

from datetime import datetime, timedelta, timezone
from passlib.hash import bcrypt as bcrypt_hash
import jwt
import hashlib
from app.core.config import settings


def _bcrypt_safe(password: str) -> str:
    """Normaliza para <= 72 bytes em UTF-8 (limite do bcrypt)."""
    if not isinstance(password, str):
        password = str(password)
    b = password.encode("utf-8")
    if len(b) > 72:
        b = b[:72]
        password = b.decode("utf-8", errors="ignore")
    return password


# ===== Senhas =====
def hash_password(password: str) -> str:
    """Hash com bcrypt (sem lançar erro >72 bytes)."""
    safe = _bcrypt_safe(password)
    return bcrypt_hash.using(ident="2b", rounds=12, truncate_error=False).hash(safe)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify com bcrypt (sem lançar erro >72 bytes)."""
    safe = _bcrypt_safe(password)
    return bcrypt_hash.using(truncate_error=False).verify(safe, password_hash)


# ===== JWT =====
def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRES_MIN
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])


# ===== SHA-256 =====
def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
