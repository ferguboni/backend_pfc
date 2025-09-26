# app/core/security.py
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
import hashlib
from app.core.config import settings

# Contexto com truncate_error=False
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False,  # evita lançar erro >72 bytes
)

def _bcrypt_safe(password: str) -> str:
    """
    Normaliza senha para <=72 bytes UTF-8 antes do bcrypt.
    """
    if not isinstance(password, str):
        password = str(password)
    b = password.encode("utf-8")
    if len(b) > 72:
        b = b[:72]
        password = b.decode("utf-8", errors="ignore")
    return password

def hash_password(password: str) -> str:
    """Gera hash bcrypt com truncamento seguro."""
    return pwd_context.hash(_bcrypt_safe(password))

def verify_password(password: str, password_hash: str) -> bool:
    """Verifica senha vs hash com truncamento seguro."""
    return pwd_context.verify(_bcrypt_safe(password), password_hash)

def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRES_MIN
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
