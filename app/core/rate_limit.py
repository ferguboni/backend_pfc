#limitador do FastApi ( Provavelmente não sera ultilizado )

from typing import Callable, Optional, Awaitable
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from app.core.config import settings

_enabled: bool = False

async def init_rate_limit():
    #Conecta no Redis e inicia o limitador, caso o REDIS_URL não estiver definido, o limitador fica DESLIGADO
    global _enabled
    if not settings.REDIS_URL:
        _enabled = False
        return
    try:
        r = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(r)
        _enabled = True
    except Exception:
        # Não derruba a API se o Redis falhar
        _enabled = False

def _noop_dependency():
    async def _noop():
        return True
    return _noop

def rate_limiter():
    # Aplica X requisições por minuto 
    if not _enabled:
        return _noop_dependency()
    try:
        times = int(settings.RATE_LIMIT.split("/")[0])
    except Exception:
        times = 20
    return RateLimiter(times=times, seconds=60)
