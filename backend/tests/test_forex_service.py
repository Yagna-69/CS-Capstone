"""Unit tests for forex_service.py — all yfinance + disk I/O is mocked."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import forex_service


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ticker_with_price(price: float):
    """Return a MagicMock that mimics yf.Ticker with fast_info.last_price set."""
    ticker = MagicMock()
    ticker.fast_info.last_price = price
    return ticker


def _make_ticker_with_empty_history():
    """Mimics a yf.Ticker whose fast_info has no price AND empty history."""
    ticker = MagicMock()
    ticker.fast_info.last_price = None
    ticker.history.return_value = pd.DataFrame()  # empty
    return ticker


# ---------------------------------------------------------------------------
# get_rate
# ---------------------------------------------------------------------------

def test_get_rate_identity_returns_one():
    """Same currency in both legs short-circuits to 1.0 with no network call."""
    with patch.object(forex_service.yf, "Ticker") as ticker_cls:
        assert forex_service.get_rate("USD", "USD") == 1.0
        assert ticker_cls.call_count == 0


def test_get_rate_identity_case_insensitive():
    with patch.object(forex_service.yf, "Ticker") as ticker_cls:
        assert forex_service.get_rate("usd", "USD") == 1.0
        assert ticker_cls.call_count == 0


def test_get_rate_cache_hit_prevents_refetch():
    """Second call within CACHE_TTL must NOT hit yfinance again."""
    with patch.object(forex_service.yf, "Ticker") as ticker_cls:
        ticker_cls.return_value = _make_ticker_with_price(1.2345)

        first = forex_service.get_rate("USD", "EUR")
        second = forex_service.get_rate("USD", "EUR")

        assert first == 1.2345
        assert second == 1.2345
        assert ticker_cls.call_count == 1  # cached on second call


def test_get_rate_raises_value_error_on_empty_history():
    """yfinance returning no price AND empty history -> ValueError."""
    with patch.object(forex_service.yf, "Ticker") as ticker_cls:
        ticker_cls.return_value = _make_ticker_with_empty_history()

        with pytest.raises(ValueError, match="No rate data"):
            forex_service.get_rate("USD", "EUR")


def test_get_rate_falls_back_to_history_when_fast_info_missing():
    """If fast_info.last_price is missing, use last close from history()."""
    ticker = MagicMock()
    ticker.fast_info.last_price = None
    ticker.history.return_value = pd.DataFrame({"Close": [1.10, 1.15, 1.20]})

    with patch.object(forex_service.yf, "Ticker", return_value=ticker):
        rate = forex_service.get_rate("USD", "EUR")

    assert rate == pytest.approx(1.20)


# ---------------------------------------------------------------------------
# Disk cache round-trip
# ---------------------------------------------------------------------------

def test_disk_cache_round_trip(tmp_path, monkeypatch):
    """_save_to_disk followed by _load_from_disk returns the same payload."""
    monkeypatch.setattr(forex_service, "CACHE_DIR", tmp_path)

    payload = [{"date": "2025-01-01T00:00:00", "rate": 1.10}]
    forex_service._save_to_disk("hist_USDEUR_1mo", payload, fetched_at=1234567.0)

    cache_file = tmp_path / "hist_USDEUR_1mo.json"
    assert cache_file.exists()

    data, fetched_at = forex_service._load_from_disk("hist_USDEUR_1mo")
    assert data == payload
    assert fetched_at == 1234567.0


def test_disk_cache_load_missing_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(forex_service, "CACHE_DIR", tmp_path)
    assert forex_service._load_from_disk("does-not-exist") is None


# ---------------------------------------------------------------------------
# get_historical_rates / get_historical_ohlc — invalid period
# ---------------------------------------------------------------------------

def test_get_historical_rates_invalid_period():
    with pytest.raises(ValueError, match="Invalid period"):
        forex_service.get_historical_rates("USD", "EUR", "bogus")


def test_get_historical_rates_identity_returns_empty():
    assert forex_service.get_historical_rates("USD", "USD", "1mo") == []
