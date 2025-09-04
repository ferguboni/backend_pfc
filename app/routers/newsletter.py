# Rota do MailerLite(Newsletter)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import httpx  # para tipar/pegar erros de rede

from app.services.mailerlite import subscribe as ml_subscribe

router = APIRouter(prefix="/api/newsletter", tags=["newsletter"])


class SubscribeIn(BaseModel):
    email: EmailStr
    name: str | None = None

#Inscreve o usuário na MailerLite
@router.post("/subscribe")
async def subscribe(body: SubscribeIn):
    try:
        result = await ml_subscribe(email=body.email, name=body.name)
        return {"message": "ok", "provider": "mailerlite", "result": result}

    except RuntimeError as e:
        # Erros conhecidos (chave ausente, 401, 429, já inscrito, etc.)
        raise HTTPException(status_code=400, detail=str(e))

    except httpx.HTTPError as e:
        # Qualquer erro HTTP não coberto acima
        raise HTTPException(status_code=502, detail=f"Erro HTTP com MailerLite: {e!s}")

    except Exception as e:
        # Fallback: nada de 500 misterioso; devolve detalhe
        raise HTTPException(status_code=502, detail=f"Falha ao inscrever na MailerLite: {e!s}")
