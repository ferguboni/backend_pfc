# Le as variáveis do ambiente (.env) para configurar a aplicação.

import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

class Settings:
    # App
    APP_ENV = os.getenv("APP_ENV", "dev")
    API_PREFIX = os.getenv("API_PREFIX", "/api")
    SECRET_KEY = os.getenv("SECRET_KEY", "troque-esta-chave")
    ACCESS_TOKEN_EXPIRES_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRES_MIN", "60"))

    # Banco (Supabase Postgres)
    DATABASE_URL = os.getenv("DATABASE_URL", "")  # Ex.: postgresql://postgres:senha@host:5432/postgres?sslmode=require

    # Redis + Rate limit
    REDIS_URL = os.getenv("REDIS_URL", "")  # Ex.: redis://localhost:6379/0
    RATE_LIMIT = os.getenv("RATE_LIMIT", "20/minute")

    # E-mail (NÃO usado com MailerLite; mantido por compatibilidade)
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "")

    # Google OAuth — opcional
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")

    # CORS
    ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]

    # NewsAPI
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")  # <<< obrigatória para /news
    NEWS_LANGUAGE = os.getenv("NEWS_LANGUAGE", "pt")  # pt, en, es...

    # MailerLite
    MAILERLITE_API_KEY = os.getenv("MAILERLITE_API_KEY", "")  # <<< obrigatória para newsletter
    MAILERLITE_GROUP_ID = os.getenv("MAILERLITE_GROUP_ID", "")  # opcional (lista/grupo)

settings = Settings()
