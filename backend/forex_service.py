"""
Forex rate service — uses yfinance for live currency pair rates.
Results are cached in-process for CACHE_TTL seconds.
"""

import time
import yfinance as yf

CACHE_TTL = 10  # seconds between live fetches for the same pair

_cache: dict[str, tuple[float, float]] = {}  # key -> (rate, fetched_at)


def get_rate(from_currency: str, to_currency: str) -> float:
    """
    Return the current exchange rate (1 unit of from_currency = X to_currency).
    Results are cached for CACHE_TTL seconds.
    Raises ValueError if the rate cannot be fetched.
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return 1.0

    key = f"{from_currency}{to_currency}"
    now = time.time()

    cached_rate, fetched_at = _cache.get(key, (None, 0))
    if cached_rate is not None and (now - fetched_at) < CACHE_TTL:
        return cached_rate

    try:
        ticker = yf.Ticker(f"{from_currency}{to_currency}=X")
        # Try fast_info first (no network round-trip if cached by yfinance)
        rate = getattr(ticker.fast_info, "last_price", None)
        if not rate or rate <= 0:
            # Fall back to 1-day history which is more reliably populated
            hist = ticker.history(period="1d")
            if hist.empty:
                raise ValueError(f"No rate data returned for {from_currency}/{to_currency}")
            rate = float(hist["Close"].iloc[-1])
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Could not fetch exchange rate for {from_currency}/{to_currency}: {exc}")

    _cache[key] = (float(rate), now)
    return float(rate)


def get_rates(pairs: list[tuple[str, str]]) -> dict[str, float]:
    """
    Fetch multiple pairs at once. Returns {"{FROM}{TO}": rate, ...}.
    Each pair is still individually cached.
    """
    return {f"{f}{t}": get_rate(f, t) for f, t in pairs}
