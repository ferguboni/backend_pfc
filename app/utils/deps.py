# Dependências comuns (ex.: pegar usuário atual a partir do JWT no header Authorization)

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.database import get_db
from app.db import models

bearer = HTTPBearer(auto_error=False)

# Lê o token JWT do header Authorization (Bearer) e busca o usuário no banco
# Se não encontrar ou token inválido -> 401
def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> models.User:
    if not creds or not creds.credentials:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = decode_token(creds.credentials)
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
