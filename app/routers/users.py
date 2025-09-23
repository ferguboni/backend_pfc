from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.db.schemas import UserListItem

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=List[UserListItem], summary="Listar usuários (name, email)")
def list_users(db: Session = Depends(get_db)):
    # consulta só as colunas necessárias
    rows = db.query(User.name, User.email).all()
    return [UserListItem(name=n, email=e) for (n, e) in rows]
