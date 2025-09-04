# Rotas de favoritos: listar, adicionar e remover

from typing import List  
from fastapi import APIRouter, Depends, HTTPException, status  
from sqlalchemy.orm import Session  
from app.core.rate_limit import rate_limiter  
from app.db.database import get_db 
from app.db import models  
from app.db.schemas import FavoriteIn, FavoriteOut 
from app.utils.deps import get_current_user  

# Agrupa as rotas sob /favorites 
router = APIRouter(prefix="/favorites", tags=["favorites"])

# Pega a lista de Favoritos
@router.get(
    "/",
    response_model=List[FavoriteOut],  
    dependencies=[Depends(rate_limiter())],  
)
# Lista os favoritos do usuário logado
def list_favorites(
    db: Session = Depends(get_db),  
    user: models.User = Depends(get_current_user),  
):
    # Filtra por usuário e ordena do mais recente para o mais antigo
    return (
        db.query(models.Favorite)
        .filter(models.Favorite.user_id == user.id)
        .order_by(models.Favorite.id.desc())
        .all()
    )
# Avisa se foi criado
@router.post(
    "/",
    response_model=FavoriteOut,  
    status_code=status.HTTP_201_CREATED, 
    dependencies=[Depends(rate_limiter())],  
)
# Adiciona uma moeda aos favoritos do usuário
def add_favorite(
    body: FavoriteIn, 
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # Impede duplicidade 
    exists = (
        db.query(models.Favorite)
        .filter(
            models.Favorite.user_id == user.id,
            models.Favorite.coin_id == body.coin_id,
        )
        .first()
    )
    if exists:
        # Retorna 409: conflito (já existe)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Moeda já está nos favoritos",
        )

    # Cria, persiste e retorna o favorito
    fav = models.Favorite(user_id=user.id, coin_id=body.coin_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav

@router.delete(
    "/{coin_id}",
    status_code=status.HTTP_204_NO_CONTENT,  
    dependencies=[Depends(rate_limiter())],  
)
# Remove a moeda {coin_id} dos favoritos do usuário
def remove_favorite(
    coin_id: str,  
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # Busca o favorito do usuário para o coin_id informado
    fav = (
        db.query(models.Favorite)
        .filter(
            models.Favorite.user_id == user.id,
            models.Favorite.coin_id == coin_id,
        )
        .first()
    )
    if not fav:
        # 404: se não for encontrado
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Não encontrado",
        )

    # Exclui e confirma no banco
    db.delete(fav)
    db.commit()
    return None  # 204 No Content
