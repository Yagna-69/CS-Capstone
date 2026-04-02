"""
Forex rate service — uses yfinance for live currency pair rates.
Results are cached in-process for CACHE_TTL seconds.
Historical rates are also persisted to disk for cross-user efficiency.
"""

import time
import json
import os
from pathlib import Path
import yfinance as yf

CACHE_TTL = 5  # seconds between live rate fetches (per-pair spot quotes)
HISTORY_CACHE_TTL = 300  # seconds for historical data (OHLC, historical rates)

# Persistent cache directory
CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

# All currencies supported by yfinance forex feeds.
# Dict maps 3-letter ISO code -> full name.
SUPPORTED_CURRENCIES: dict[str, str] = {
    # G7 / Majors
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "CHF": "Swiss Franc",
    "AUD": "Australian Dollar",
    "CAD": "Canadian Dollar",
    "NZD": "New Zealand Dollar",
    # Scandinavia
    "SEK": "Swedish Krona",
    "NOK": "Norwegian Krone",
    "DKK": "Danish Krone",
    # Asia-Pacific
    "SGD": "Singapore Dollar",
    "HKD": "Hong Kong Dollar",
    "TWD": "Taiwan Dollar",
    "KRW": "South Korean Won",
    "THB": "Thai Baht",
    "MYR": "Malaysian Ringgit",
    "PHP": "Philippine Peso",
    "IDR": "Indonesian Rupiah",
    "INR": "Indian Rupee",
    "CNY": "Chinese Yuan",
    # Latin America
    "MXN": "Mexican Peso",
    "BRL": "Brazilian Real",
    "CLP": "Chilean Peso",
    "COP": "Colombian Peso",
    "PEN": "Peruvian Sol",
    "ARS": "Argentine Peso",
    # Africa
    "ZAR": "South African Rand",
    "NGN": "Nigerian Naira",
    "KES": "Kenyan Shilling",
    "EGP": "Egyptian Pound",
    # Middle East
    "TRY": "Turkish Lira",
    "ILS": "Israeli Shekel",
    "SAR": "Saudi Riyal",
    "AED": "UAE Dirham",
    "QAR": "Qatari Riyal",
    "KWD": "Kuwaiti Dinar",
    "BHD": "Bahraini Dinar",
    "OMR": "Omani Rial",
    "JOD": "Jordanian Dinar",
    # Europe (emerging)
    "PLN": "Polish Zloty",
    "CZK": "Czech Koruna",
    "HUF": "Hungarian Forint",
    "RON": "Romanian Leu",
    "RUB": "Russian Ruble",
}

_cache: dict[str, tuple[float, float]] = {}  # key -> (rate, fetched_at)
_history_cache: dict[str, tuple[list[dict], float]] = {}  # key -> (data, fetched_at)


def _load_from_disk(cache_key: str) -> tuple[any, float] | None:
    """Load cached data from disk if it exists and is valid."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if not cache_file.exists():
        return None
    try:
        with open(cache_file, 'r') as f:
            cached = json.load(f)
        return cached['data'], cached['fetched_at']
    except Exception:
        return None


def _save_to_disk(cache_key: str, data: any, fetched_at: float):
    """Persist cached data to disk for cross-user sharing."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    try:
        with open(cache_file, 'w') as f:
            json.dump({'data': data, 'fetched_at': fetched_at}, f)
    except Exception as e:
        print(f"Warning: Could not write cache to disk: {e}")


# Map UI period labels to yfinance (period, interval) pairs
PERIOD_MAP: dict[str, tuple[str, str]] = {
    "1d":  ("1d",  "5m"),
    "1wk": ("5d",  "1h"),
    "1mo": ("1mo", "1d"),
    "3mo": ("3mo", "1d"),
    "6mo": ("6mo", "1d"),
    "ytd": ("ytd", "1d"),
    "1y":  ("1y",  "1d"),
    "3y":  ("3y",  "1wk"),
    "5y":  ("5y",  "1wk"),
}


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


def get_historical_rates(
    from_currency: str, to_currency: str, period: str
) -> list[dict]:
    """
    Return historical exchange rates as [{"date": ISO str, "rate": float}, ...].
    ``period`` must be a key in PERIOD_MAP (e.g. "1mo", "3mo", "1y").
    Results are cached in-memory and on disk for cross-user efficiency.
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return []

    if period not in PERIOD_MAP:
        raise ValueError(f"Invalid period '{period}'. Must be one of {list(PERIOD_MAP)}")

    yf_period, yf_interval = PERIOD_MAP[period]
    key = f"{from_currency}{to_currency}:{period}"
    now = time.time()

    # Check in-memory cache first
    cached_data, fetched_at = _history_cache.get(key, (None, 0))
    if cached_data is not None and (now - fetched_at) < HISTORY_CACHE_TTL:
        return cached_data

    # Check disk cache
    disk_cache = _load_from_disk(f"hist_{key}")
    if disk_cache:
        cached_data, fetched_at = disk_cache
        if (now - fetched_at) < HISTORY_CACHE_TTL:
            _history_cache[key] = (cached_data, fetched_at)
            return cached_data

    try:
        ticker = yf.Ticker(f"{from_currency}{to_currency}=X")
        hist = ticker.history(period=yf_period, interval=yf_interval)
        if hist.empty:
            raise ValueError(
                f"No historical data for {from_currency}/{to_currency} period={period}"
            )
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(
            f"Could not fetch historical rates for {from_currency}/{to_currency}: {exc}"
        )

    data = []
    for ts, row in hist.iterrows():
        rate = float(row["Close"])
        if rate > 0:
            data.append({"date": ts.isoformat(), "rate": rate})

    _history_cache[key] = (data, now)
    _save_to_disk(f"hist_{key}", data, now)
    return data


_ohlc_cache: dict[str, tuple[list[dict], float]] = {}


def get_historical_ohlc(
    from_currency: str, to_currency: str, period: str
) -> list[dict]:
    """
    OHLC bars for charting: [{"time": unix_secs, "open", "high", "low", "close"}, ...].
    Results are cached in-memory and on disk for cross-user efficiency.
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return []

    if period not in PERIOD_MAP:
        raise ValueError(f"Invalid period '{period}'. Must be one of {list(PERIOD_MAP)}")

    key = f"ohlc:{from_currency}{to_currency}:{period}"
    now = time.time()
    
    # Check in-memory cache
    cached, fetched_at = _ohlc_cache.get(key, (None, 0))
    if cached is not None and (now - fetched_at) < HISTORY_CACHE_TTL:
        return cached

    # Check disk cache
    disk_cache = _load_from_disk(key)
    if disk_cache:
        cached, fetched_at = disk_cache
        if (now - fetched_at) < HISTORY_CACHE_TTL:
            _ohlc_cache[key] = (cached, fetched_at)
            return cached

    yf_period, yf_interval = PERIOD_MAP[period]

    try:
        ticker = yf.Ticker(f"{from_currency}{to_currency}=X")
        hist = ticker.history(period=yf_period, interval=yf_interval)
        if hist.empty:
            raise ValueError(
                f"No OHLC data for {from_currency}/{to_currency} period={period}"
            )
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(
            f"Could not fetch OHLC for {from_currency}/{to_currency}: {exc}"
        )

    out: list[dict] = []
    for ts, row in hist.iterrows():
        close = float(row["Close"])
        if close <= 0 or close != close:  # NaN
            continue
        o = float(row["Open"]) if row["Open"] == row["Open"] else close
        h = float(row["High"]) if row["High"] == row["High"] else close
        lo = float(row["Low"]) if row["Low"] == row["Low"] else close
        t = int(ts.timestamp())
        out.append(
            {
                "time": t,
                "open": o,
                "high": max(h, o, lo, close),
                "low": min(lo, o, h, close),
                "close": close,
            }
        )

    _ohlc_cache[key] = (out, now)
    _save_to_disk(key, out, now)
    return out
