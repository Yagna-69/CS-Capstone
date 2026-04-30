"""Unit tests for routes/trading.py — Supabase, yfinance, and auth all mocked."""

from unittest.mock import MagicMock

import pytest

from tests.conftest import TEST_USER_ID, TEST_USER_EMAIL


# ---------------------------------------------------------------------------
# Fake Supabase table — returns scripted responses for select/insert/update.
# ---------------------------------------------------------------------------

class FakeTable:
    """
    Captures the last verb called (select/insert/update) and returns the
    next scripted response on .execute(). Methods like .eq/.order/.limit/.or_
    return self so chained calls work.
    """

    def __init__(self, select_responses=None, insert_responses=None, update_responses=None):
        self._select = list(select_responses or [])
        self._insert = list(insert_responses or [])
        self._update = list(update_responses or [])
        self._verb = None
        self.last_insert_payload = None
        self.last_update_payload = None
        self.insert_calls = []
        self.update_calls = []

    def select(self, *_, **__):
        self._verb = "select"
        return self

    def insert(self, payload):
        self._verb = "insert"
        self.last_insert_payload = payload
        self.insert_calls.append(payload)
        return self

    def update(self, payload):
        self._verb = "update"
        self.last_update_payload = payload
        self.update_calls.append(payload)
        return self

    def eq(self, *_, **__):
        return self

    def or_(self, *_, **__):
        return self

    def order(self, *_, **__):
        return self

    def limit(self, *_, **__):
        return self

    def execute(self):
        if self._verb == "select":
            if self._select:
                return self._select.pop(0)
            return MagicMock(data=[])
        if self._verb == "insert":
            if self._insert:
                return self._insert.pop(0)
            return MagicMock(data=[{}])
        if self._verb == "update":
            if self._update:
                return self._update.pop(0)
            return MagicMock(data=[{}])
        return MagicMock(data=[])


def _wire_admin(admin, tables: dict):
    """Make admin.table(name) return tables[name]."""
    admin.table.side_effect = lambda name: tables[name]


def _resp(data):
    """Shorthand: build an object with a .data attribute for execute() returns."""
    r = MagicMock()
    r.data = data
    return r


# ---------------------------------------------------------------------------
# /exchange — validation
# ---------------------------------------------------------------------------

def test_exchange_rejects_negative_amount(client):
    resp = client.post(
        "/api/trade/exchange",
        json={"from_currency": "USD", "to_currency": "EUR", "amount": -10},
    )
    assert resp.status_code == 400
    assert "positive" in resp.json()["detail"].lower()


def test_exchange_rejects_zero_amount(client):
    resp = client.post(
        "/api/trade/exchange",
        json={"from_currency": "USD", "to_currency": "EUR", "amount": 0},
    )
    assert resp.status_code == 400


def test_exchange_rejects_same_currency(client):
    resp = client.post(
        "/api/trade/exchange",
        json={"from_currency": "USD", "to_currency": "USD", "amount": 10},
    )
    assert resp.status_code == 400
    assert "itself" in resp.json()["detail"].lower()


def test_exchange_rejects_insufficient_balance(client, supabase_admin):
    """Balance is 50 USD; user tries to exchange 100 USD -> 400."""
    portfolio = FakeTable(select_responses=[_resp([{"amount": 50}])])
    _wire_admin(supabase_admin, {"portfolio": portfolio})

    resp = client.post(
        "/api/trade/exchange",
        json={"from_currency": "USD", "to_currency": "EUR", "amount": 100},
    )
    assert resp.status_code == 400
    assert "insufficient" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# /exchange — happy path
# ---------------------------------------------------------------------------

def test_exchange_happy_path_debits_sender_credits_target(
    client, supabase_admin, monkeypatch
):
    """100 USD -> EUR at rate 0.9 should debit USD by 100 and credit EUR by 90."""
    # Mock get_rate where it's looked up: in routes.trading
    import routes.trading as trading_mod
    monkeypatch.setattr(trading_mod, "get_rate", lambda f, t: 0.9)

    portfolio = FakeTable(
        select_responses=[
            _resp([{"amount": 1000}]),  # _get_holding USD: balance check
            _resp([{"amount": 1000}]),  # _upsert_holding USD: existing select
            _resp([]),                  # _get_holding EUR: nothing
            _resp([]),                  # _upsert_holding EUR: existing select -> insert path
        ],
    )
    txlog = FakeTable(
        insert_responses=[_resp([{"transaction_id": "tx-happy-001"}])],
    )
    _wire_admin(supabase_admin, {"portfolio": portfolio, "transaction-log": txlog})

    resp = client.post(
        "/api/trade/exchange",
        json={"from_currency": "USD", "to_currency": "EUR", "amount": 100},
    )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["transaction_id"] == "tx-happy-001"
    assert body["from_currency"] == "USD"
    assert body["to_currency"] == "EUR"
    assert body["sent_amount"] == 100
    assert body["received_amount"] == pytest.approx(90.0)
    assert body["rate"] == 0.9

    # Sender debited: USD update payload {"amount": 900}
    usd_updates = [p for p in portfolio.update_calls if p.get("amount") == 900]
    assert len(usd_updates) == 1, f"expected USD debit to 900, got {portfolio.update_calls}"

    # Target credited: EUR insert with amount=90
    eur_inserts = [
        p for p in portfolio.insert_calls
        if p.get("currency-ticker-symbol") == "EUR" and p.get("amount") == pytest.approx(90.0)
    ]
    assert len(eur_inserts) == 1, f"expected EUR credit insert, got {portfolio.insert_calls}"

    # Transaction log was written with type EXCHANGE
    assert len(txlog.insert_calls) == 1
    log = txlog.insert_calls[0]
    assert log["type"] == "EXCHANGE"
    assert log["sender_id"] == TEST_USER_ID
    assert log["sender_currency_ticker_symbol"] == "USD"
    assert log["receiver_currency_ticker_symbol"] == "EUR"
    assert log["sender-amount"] == 100
    assert log["receiver-amount"] == pytest.approx(90.0)


# ---------------------------------------------------------------------------
# /transfer
# ---------------------------------------------------------------------------

def _user_obj(uid, email):
    u = MagicMock()
    u.id = uid
    u.email = email
    return u


def test_transfer_rejects_self_transfer(client, supabase_admin):
    """list_users returns the same user as the sender -> 400."""
    list_users_resp = MagicMock()
    list_users_resp.users = [_user_obj(TEST_USER_ID, TEST_USER_EMAIL)]
    supabase_admin.auth.admin.list_users.return_value = list_users_resp

    resp = client.post(
        "/api/trade/transfer",
        json={"to_email": TEST_USER_EMAIL, "currency": "USD", "amount": 10},
    )
    assert resp.status_code == 400
    assert "yourself" in resp.json()["detail"].lower()


def test_transfer_rejects_unknown_email(client, supabase_admin):
    """list_users returns no matching user -> 404."""
    list_users_resp = MagicMock()
    list_users_resp.users = []  # nobody
    supabase_admin.auth.admin.list_users.return_value = list_users_resp

    resp = client.post(
        "/api/trade/transfer",
        json={"to_email": "ghost@example.com", "currency": "USD", "amount": 10},
    )
    assert resp.status_code == 404
    assert "no user found" in resp.json()["detail"].lower()
