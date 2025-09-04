# infoCripto — Backend (FastAPI + Supabase + Redis)

Backend do PFC :
- Autenticação com JWT (cadastro/login por e-mail/senha)
- Favoritos de moedas
- Preços (CoinGecko)
- Notícias (NewsAPI)
- Newsletter (MailerLite API + APScheduler placeholder)
- Rate limit (Redis) para proteger as rotas

## Passo a passo (Windows PowerShell — forma mais simples)
1. **Entre na pasta do projeto** (onde está este README).
2. Crie e ative um ambiente virtual:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   ```
3. Instale as dependências:
   ```powershell
   python -m pip install -r requirements.txt
   ```
4. Crie o seu arquivo `.env` a partir do exemplo e **preencha os campos marcados**:
   ```powershell
   Copy-Item .env.example .env
   # Abra o .env e edite: SECRET_KEY, DATABASE_URL (Supabase), REDIS_URL (se usar gerenciado), ALLOWED_ORIGINS etc.
   ```
5. Rode a API (modo desenvolvimento):
   ```powershell
   uvicorn app.main:app --reload
   ```
   - Acesse a documentação interativa: http://localhost:8000/docs

## Rodando com Docker
1. **Preencha o `.env`** antes.
2. Suba os serviços:
   ```bash
   docker compose up --build
   ```
   A API ficará em `http://localhost:8000`.

## Dicas rápidas
- **Supabase (Postgres)**: use a URL completa com `sslmode=require` no `DATABASE_URL`.
- **Redis**: pode usar o `docker-compose` local (já incluso) ou um Redis gerenciado (cole a URL em `REDIS_URL`).
- **JWT**: após login, use o token no header `Authorization: Bearer <seu_token>`.
- **SMTP**: é opcional — se não preencher, o envio de e-mails da newsletter é ignorado silenciosamente.

## Endpoints principais
- `POST /api/auth/register` — { email, password, name? }
- `POST /api/auth/login` — retorna `{ access_token }`
- `GET  /api/favorites/` (Bearer)
- `POST /api/favorites/` (Bearer) — { coin_id }
- `DELETE /api/favorites/{coin_id}` (Bearer)
- `GET  /api/prices/markets?vs_currency=usd&per_page=10`
- `GET  /api/news/`
- `POST /api/newsletter/subscribe` — { email }

## Erros comuns
- **requirements.txt não encontrado**: execute os comandos **na pasta do projeto**.
- **fastapi-limiter==0.1.8**: não existe — já corrigimos para **0.1.6**.
- **Redis**: se `REDIS_URL` estiver errado ou indisponível, as rotas com limitador podem falhar (500). Ajuste a URL.


