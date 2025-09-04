# Rotas de validação/parâmetros do CoinGecko 

from fastapi import APIRouter, Query
from app.services.coingecko import fetch_markets, fetch_coin_detail, search_coins

#Cria a rota
router = APIRouter(prefix="/api/prices", tags=["prices"])

# Config de tipo de moeda, quantidade de itens por pagina e numero de pagina
@router.get("/markets")
async def markets(
    vs_currency: str = Query("brl"),
    per_page: int = Query(10, ge=1, le=250),
    page: int = Query(1, ge=1),
):
    return await fetch_markets(vs_currency=vs_currency, per_page=per_page, page=page)

# Busca moedas pelo termo informado como nome, símbolo, slug e etc
@router.get("/coins/search")
async def coins_search(q: str = Query(..., min_length=1)):
    return await search_coins(q=q)

# Obtém dados completos de uma moeda específica, identificada por coin_id.
@router.get("/coins/{coin_id}")
async def coin_detail(coin_id: str):
    return await fetch_coin_detail(coin_id=coin_id)
