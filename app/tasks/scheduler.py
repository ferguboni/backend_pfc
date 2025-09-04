# Tarefas agendadas com APScheduler.
# Ex: job semanal (placeholder) — recomenda-se usar as automações do MailerLite para disparos reais.

from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.db.database import SessionLocal
from app.db import models

scheduler: Optional[AsyncIOScheduler] = None

# Placeholder: aqui você poderia montar um resumo semanal e acionar uma automação do MailerLite (recomendado).
async def weekly_digest_job():
    if SessionLocal:
        with SessionLocal() as db:
            _ = db.query(models.NewsletterSubscription).count()
    return True

# Inicia o scheduler se ainda não estiver rodando
async def start_scheduler():
    global scheduler
    if scheduler and scheduler.running:
        return
    scheduler = AsyncIOScheduler(timezone="UTC")
    # Toda segunda às 12:00 UTC
    scheduler.add_job(weekly_digest_job, CronTrigger(day_of_week="mon", hour=12, minute=0))
    scheduler.start()

# Para o scheduler no encerramento da aplicação
async def shutdown_scheduler():
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
