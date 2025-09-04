# API Coingecko

from __future__ import annotations
import os
from typing import Any, Dict, List
import httpx
from fastapi import HTTPException

PRO_BASE = "https://pro-api.coingecko.com/api/v3"
PUB_BASE = "https://api.coingecko.com/api/v3"

def _want_pro() -> bool:
    return os.getenv("COINGECKO_USE_PRO") == "1" and bool(os.getenv("COINGECKO_API_KEY"))

async def _get(path: str, params: Dict[str, Any] | None = None) -> httpx.Response:
    use_pro = _want_pro()
    headers = {"x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")} if use_pro else {}

    async with httpx.AsyncClient(base_url=(PRO_BASE if use_pro else PUB_BASE), timeout=20) as client:
        r = await client.get(path, params=params, headers=headers)

    # Fallback automático quando key DEMO é usada em PRO (erro 10011)
    if r.status_code == 400 and use_pro:
        try:
            body = r.json()
            if isinstance(body, dict) and body.get("status", {}).get("error_code") == 10011:
                async with httpx.AsyncClient(base_url=PUB_BASE, timeout=20) as client:
                    r = await client.get(path, params=params)
        except Exception:
            pass

    if r.status_code == 429:
        raise HTTPException(502, "CoinGecko rate limit (429). Tente novamente.")
    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        try:
            body = r.json()
        except Exception:
            body = r.text
        raise HTTPException(status_code=r.status_code, detail={"error": str(e), "body": body})
    return r

async def _resolve_coin_id(input_id_or_symbol: str) -> str:
    # 1) tenta como id direto
    try:
        r = await _get(
            f"/coins/{input_id_or_symbol}",
            {
                "localization": "false",
                "tickers": "false",
                "market_data": "false",
                "community_data": "false",
                "developer_data": "false",
                "sparkline": "false",
            },
        )
        return r.json().get("id", input_id_or_symbol)
    except HTTPException as e:
        if e.status_code != 404:
            raise
    # 2) mapeia por /search (símbolo/id)
    sr = await _get("/search", {"query": input_id_or_symbol})
    coins = (sr.json() or {}).get("coins", [])
    for c in coins:
        if (c.get("symbol") or "").lower() == input_id_or_symbol.lower():
            return c.get("id")
    for c in coins:
        if (c.get("id") or "").lower() == input_id_or_symbol.lower():
            return c.get("id")
    raise HTTPException(404, "coin not found")

# ---------------------- FUNÇÕES EXPOSTAS ----------------------

async def fetch_markets(vs_currency: str, per_page: int, page: int) -> List[Dict[str, Any]]:
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
        "sparkline": "false",
        "price_change_percentage": "24h",
    }
    r = await _get("/coins/markets", params)
    return r.json()

async def fetch_coin_detail(coin_id: str) -> Dict[str, Any]:
    real_id = await _resolve_coin_id(coin_id)
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false",
    }
    r = await _get(f"/coins/{real_id}", params)
    return r.json()

#Busca nunca levanta 404; retorna sempre lista (vazia ou não)
async def search_coins(q: str) -> Dict[str, Any]:
    r = await _get("/search", {"query": q})
    data = r.json() if isinstance(r.json(), dict) else {}
    return {"query": q, "coins": data.get("coins", [])}

__all__ = ["fetch_markets", "fetch_coin_detail", "search_coins"]
