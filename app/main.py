# Aplicação FastAPI "PRINCIPAL"
# - Inicializa banco e limitador de taxa (Redis)
# - Registra rotas da API
# - Ativa CORS para o seu front-end

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()


from app.core.config import settings
from app.core.rate_limit import init_rate_limit
from app.db.database import create_all
from app.routers import auth, favorites, news, prices, newsletter
from app.tasks.scheduler import start_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_all()                # cria tabelas se DATABASE_URL estiver setado
    await init_rate_limit()     # ativa rate limit se REDIS_URL existir
    await start_scheduler()     # inicia jobs do APScheduler
    yield
    # Shutdown
    await shutdown_scheduler()

app = FastAPI(title="infoCripto API", lifespan=lifespan)

# CORS — permita seu front (Vercel).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas da API (prefixo configurável por API_PREFIX)
app.include_router(auth.router)
app.include_router(favorites.router)
app.include_router(prices.router)
app.include_router(news.router)
app.include_router(newsletter.router)


@app.get("/")
async def root():
    # Endpoint simples para ver se a API está no ar
    return {"ok": True, "message": "infoCripto API rodando"}
