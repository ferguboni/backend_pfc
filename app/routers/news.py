# Notícias via NewsAPI. Público, mas com rate limit.

from fastapi import APIRouter, Depends
from typing import List
from app.services.news_service import fetch_news
from app.db.schemas import NewsItem
from app.core.rate_limit import rate_limiter

router = APIRouter(prefix="/news", tags=["news"])

# Obtém uma lista de notícias recentes (títulos e links)
@router.get("/", response_model=List[NewsItem], dependencies=[Depends(rate_limiter())])
async def list_news():
    return await fetch_news()
