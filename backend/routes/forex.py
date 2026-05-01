import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from models import RateResponse
from forex_service import (
    get_rate,
    get_rates,
    get_historical_ohlc,
    PERIOD_MAP,
    SUPPORTED_CURRENCIES,
)

router = APIRouter()

# Default pairs shown in the ticker banner
DEFAULT_PAIRS = [
    # Major pairs
    ("EUR", "USD"),
    ("GBP", "USD"),
    ("USD", "JPY"),
    ("AUD", "USD"),
    ("USD", "CAD"),
    ("USD", "CHF"),
    ("NZD", "USD"),
    # Major crosses
    ("EUR", "GBP"),
    ("EUR", "JPY"),
    ("GBP", "JPY"),
    # Popular minors
    ("USD", "SEK"),
    ("USD", "NOK"),
    ("USD", "DKK"),
    ("USD", "SGD"),
    ("USD", "HKD"),
    ("USD", "MXN"),
    ("USD", "ZAR"),
    ("USD", "TRY"),
    ("USD", "BRL"),
    ("USD", "INR"),
    ("USD", "CNY"),
    ("USD", "KRW"),
    ("USD", "PLN"),
    ("USD", "THB"),
]


@router.get("/rate/{from_currency}/{to_currency}", response_model=RateResponse)
async def live_rate(from_currency: str, to_currency: str):
    """Return the live exchange rate for a single currency pair."""
    from_cur = from_currency.upper()
    to_cur   = to_currency.upper()
    try:
        rate = await asyncio.to_thread(get_rate, from_cur, to_cur)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return RateResponse(from_currency=from_cur, to_currency=to_cur, rate=rate, timestamp=datetime.now(timezone.utc))


@router.get("/rates")
async def live_rates(pairs: str = None):
    """
    Return rates for multiple pairs.
    Optional query param `pairs` — comma-separated list like "USDAUD,USDCAD".
    Defaults to the standard dashboard pairs if omitted.
    """
    if pairs:
        try:
            parsed = [(p[:3].upper(), p[3:].upper()) for p in pairs.split(",") if len(p) == 6]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid pairs format. Use 'USDAUD,USDCAD'.")
    else:
        parsed = DEFAULT_PAIRS

    try:
        rates = await asyncio.to_thread(get_rates, parsed)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return {"rates": rates, "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/history/{from_currency}/{to_currency}")
async def pair_ohlc_history(
    from_currency: str,
    to_currency: str,
    period: str = Query(
        "3mo",
        description="One of: " + ", ".join(sorted(PERIOD_MAP.keys())),
    ),
):
    """OHLC time series for a pair (yfinance), for TradingView-style charts."""
    if period not in PERIOD_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period. Use one of: {list(PERIOD_MAP)}",
        )
    try:
        candles = await asyncio.to_thread(get_historical_ohlc, from_currency.upper(), to_currency.upper(), period)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return {
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "period": period,
        "interval": PERIOD_MAP[period][1],
        "candles": candles,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/currencies")
async def list_currencies():
    """Return all supported currency tickers with their full names."""
    return {
        "currencies": [
            {"code": code, "name": name}
            for code, name in SUPPORTED_CURRENCIES.items()
        ]
    }
