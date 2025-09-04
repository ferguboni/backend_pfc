# API MAILERLITE
# - Em QUALQUER falha de rede/HTTP, levantamos RuntimeError com uma mensagem legível
# - O router converte isso em 400/502 sem estourar 500

from __future__ import annotations
import os
from typing import Optional, Dict, Any
import httpx

MAILERLITE_BASE_URL = "https://connect.mailerlite.com/api"


def _headers() -> Dict[str, str]:
    api_key = os.getenv("MAILERLITE_API_KEY")
    if not api_key:
        # Falta de config vira RuntimeError -> router devolve 400
        raise RuntimeError(
            "MAILERLITE_API_KEY não configurada. Defina no .env para usar /api/newsletter/subscribe."
        )
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

#  Inscreve um email na MailerLite. Retorna dict com status/ids
async def subscribe(email: str, name: Optional[str] = None, group_id: Optional[str] = None) -> Dict[str, Any]:
    gid = group_id or os.getenv("MAILERLITE_GROUP_ID")

    payload: Dict[str, Any] = {"email": email}
    if name:
        payload["fields"] = {"name": name}
    if gid:
        payload["groups"] = [gid]

    url = f"{MAILERLITE_BASE_URL}/subscribers"

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(url, json=payload, headers=_headers())
    except httpx.RequestError as e:
        # Erro de rede (ex.: DNS, timeout, SSL)
        raise RuntimeError(f"Falha de rede ao contatar MailerLite: {e!s}")

    # Tratamento de códigos comuns da API
    if resp.status_code in (200, 201):
        data = resp.json()
        return {"ok": True, "status": resp.status_code, "id": data.get("id"), "data": data}

    if resp.status_code in (409, 422):
        # Já inscrito / conflito de validação
        return {"ok": True, "status": resp.status_code, "reason": "already_subscribed", "detail": resp.text}

    if resp.status_code == 401:
        raise RuntimeError("MailerLite rejeitou a chave (401). Verifique MAILERLITE_API_KEY.")
    if resp.status_code == 429:
        raise RuntimeError("MailerLite aplicou rate limit (429). Tente novamente em instantes.")

    # Outros erros HTTP (5xx/4xx)
    try:
        detail = resp.json()
    except Exception:
        detail = {"text": resp.text}
    raise RuntimeError(f"MailerLite API error {resp.status_code}: {detail}")
