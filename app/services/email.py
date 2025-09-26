import os
import logging
from email.message import EmailMessage
import aiosmtplib

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_TLS  = os.getenv("SMTP_TLS", "true").lower() == "true"
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "no-reply@example.com")

async def send_email(to: str, subject: str, html: str):
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL              # ex.: "InfoCripto <ferguboni@gmail.com>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(html, subtype="html")

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASS,
            start_tls=SMTP_TLS,  # Gmail: 587 + STARTTLS
            timeout=20,
        )
        logger.info("E-mail enviado para %s", to)
    except Exception as e:
        logger.exception("Falha ao enviar e-mail para %s: %s", to, e)
        raise
