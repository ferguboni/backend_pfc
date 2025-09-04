
# Segurança:
# Hash e verificação de senha (Passlib)
# Criação e validação de JWT (PyJWT)

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from app.core.config import settings

# Configura o contexto de hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Gera o hash da senha para salvar no banco 
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verfica se a senha digitada é a mesma que ta no banco
def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

# Gera um token JWT de (60 min) estabelecido no .env 
def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MIN)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> dict:
    "Decodifica e valida um token JWT."
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
