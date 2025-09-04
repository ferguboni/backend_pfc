##Conexão com o banco (SQLAlchemy) e criação de tabelas.

from __future__ import annotations
from typing import Generator, Optional
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

# Faz a criptografia, precisa colocar no final da URL do Postgres (sslmode=require)
def _ensure_ssl(url: str) -> str:
    if not url:
        return url
    lower = url.lower()
    if "sslmode=" in lower:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}sslmode=require"

# Cria o engine SQLAlchemy com configurações seguras:
   # - pool_pre_ping: evita conexões mortas
   # - pool_size / max_overflow: pool moderado 
def _make_engine(db_url: str):

    db_url = _ensure_ssl(db_url)

    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=5,       
        max_overflow=5,    
        future=True,       
    )
    return engine



# Requer DATABASE_URL definido no .env antes de usar rotas com banco
_engine = _make_engine(settings.DATABASE_URL) if settings.DATABASE_URL else None

SessionLocal: Optional[sessionmaker[Session]] = (
    sessionmaker(bind=_engine, autocommit=False, autoflush=False, expire_on_commit=False)
    if _engine
    else None
)


class Base(DeclarativeBase):
    """Base declarativa para todos os modelos ORM."""
    pass

# Dependencia do FastAPI que fornece uma sessão de banco, ele lança um erro se DATABASE_URL não estiver configurado e faz o fechamento da sessão.
def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL não configurado. Preencha no .env.")
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Cria as tabelas definidas nos modelos registrados
# Faz import tardio de app.db.models para garantir o registro e loga o resultado
def create_all() -> None:
    if _engine is None:
        logger.warning("create_all() ignorado: DATABASE_URL não configurado.")
        return
    from app.db import models
    Base.metadata.create_all(bind=_engine)
    logger.info("Tabelas verificadas/criadas com sucesso.")
