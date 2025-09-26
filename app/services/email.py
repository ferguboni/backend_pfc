import os
import logging
from email.message import EmailMessage
import aiosmtplib
import httpx

logger = logging.getLogger(__name__)

# SMTP (fallback)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_TLS  = os.getenv("SMTP_TLS", "true").lower() == "true"

# API (primária, se disponível)
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

SENDER_EMAIL = os.getenv("SENDER_EMAIL", "no-reply@example.com")

async def send_email(to: str, subject: str, html: str):
    # 1) Tenta via Resend API (HTTP) se houver chave
    if RESEND_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
                    json={"from": SENDER_EMAIL, "to": to, "subject": subject, "html": html},
                )
            r.raise_for_status()
            logger.info("E-mail enviado via Resend para %s", to)
            return
        except Exception as e:
            logger.exception("Falha Resend: %s — tentando SMTP...", e)
            # cai para SMTP

    # 2) Fallback: SMTP (pode falhar se portas bloqueadas)
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(html, subtype="html")

    try:
        use_ssl = (SMTP_PORT == 465) or (not SMTP_TLS)
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASS,
            start_tls=not use_ssl,   # 587
            use_tls=use_ssl,         # 465
            timeout=25,
        )
        logger.info("E-mail enviado via SMTP para %s", to)
    except Exception as e:
        logger.exception("Falha SMTP: %s", e)
        raise
