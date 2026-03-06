from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from models import RateResponse
from forex_service import get_rate, get_rates

router = APIRouter()

# Default pairs shown in the ticker banner
DEFAULT_PAIRS = [
    ("EUR", "USD"),
    ("GBP", "USD"),
    ("USD", "JPY"),
    ("AUD", "USD"),
    ("USD", "CAD"),
    ("USD", "CHF"),
    ("NZD", "USD"),
    ("EUR", "GBP"),
    ("EUR", "JPY"),
    ("GBP", "JPY"),
]


@router.get("/rate/{from_currency}/{to_currency}", response_model=RateResponse)
async def live_rate(from_currency: str, to_currency: str):
    """Return the live exchange rate for a single currency pair."""
    from_cur = from_currency.upper()
    to_cur = to_currency.upper()

    try:
        rate = get_rate(from_cur, to_cur)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return RateResponse(
        from_currency=from_cur,
        to_currency=to_cur,
        rate=rate,
        timestamp=datetime.now(timezone.utc),
    )


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
        rates = get_rates(parsed)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return {
        "rates": rates,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
