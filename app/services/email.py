# app/services/email.py
import os, logging
from email.message import EmailMessage
import aiosmtplib

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_TLS  = os.getenv("SMTP_TLS", "true").lower() == "true"  # STARTTLS se true
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "no-reply@example.com")

async def send_email(to: str, subject: str, html: str):
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
        logger.info("E-mail enviado para %s", to)
    except Exception as e:
        logger.exception("Falha ao enviar e-mail para %s: %s", to, e)
        raise
