#API Newsapi

from typing import List
import httpx
from app.core.config import settings
from app.db.schemas import NewsItem

NEWSAPI_URL = "https://newsapi.org/v2/everything"

# Busca notícias recentes sobre cripto usando a NewsAPI, esta em pt(Portugues), puxa 20 noticias por vez.
async def fetch_news() -> List[NewsItem]:
    if not settings.NEWSAPI_KEY:
        # Retorna lista vazia se não configurado (não quebra o app)
        return []
    params = {
        "q": "(criptomoeda OR cripto OR bitcoin OR ethereum OR cryptocurrency)",
        "pageSize": 20,
        "sortBy": "publishedAt",
        "language": settings.NEWS_LANGUAGE or "pt",
    }
    headers = {"X-Api-Key": settings.NEWSAPI_KEY}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(NEWSAPI_URL, params=params, headers=headers)
        r.raise_for_status()
        data = r.json()
    articles = data.get("articles", []) or []
    items: List[NewsItem] = []
    for a in articles:
        title = (a.get("title") or "").strip()
        link = a.get("url") or ""
        source = (a.get("source", {}) or {}).get("name") or ""
        if title and link:
            items.append(NewsItem(title=title, link=link, source=source))
    return items
