"""
Trading routes — currency exchange and user-to-user transfers.

Performance notes
-----------------
* Balance fetch, rate fetch, and notification-pref fetch are parallelised with
  asyncio.to_thread so no blocking I/O stalls the event loop.
* _upsert_holding uses a single Postgres UPSERT (one round-trip vs two).
* _find_user_by_email uses get_user_by_email (O(1)) instead of list_users (O(n)).
* transaction-log insert and email notification fire as BackgroundTasks so the
  HTTP response is returned to the client before those writes complete.
* History endpoint fires sent + received queries in parallel.
"""

import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from models import ExchangeRequest, ExchangeResponse, TransferRequest
from database import get_supabase_admin
from auth import get_current_user
from forex_service import get_rate
from config import settings

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers (all synchronous — called via asyncio.to_thread)
# ---------------------------------------------------------------------------

def _get_holding(admin, user_id: str, currency: str) -> float:
    resp = (
        admin.table("portfolio")
        .select("amount")
        .eq("id", user_id)
        .eq("currency-ticker-symbol", currency)
        .execute()
    )
    return float(resp.data[0]["amount"] or 0) if resp.data else 0.0


def _upsert_holding(admin, user_id: str, currency: str, new_amount: float):
    """Single-round-trip upsert using Postgres ON CONFLICT."""
    admin.table("portfolio").upsert(
        {"id": user_id, "currency-ticker-symbol": currency, "amount": new_amount},
        on_conflict="id,currency-ticker-symbol",
    ).execute()


def _find_user_by_email(admin, email: str):
    """O(1) lookup — no full user list scan."""
    try:
        resp = admin.auth.admin.get_user_by_email(email)
        return resp.user if hasattr(resp, "user") else resp
    except Exception:
        return None


def _build_email_map(admin, user_ids: set) -> dict:
    email_map = {}
    try:
        resp  = admin.auth.admin.list_users()
        users = resp.users if hasattr(resp, "users") else resp
        for u in users:
            uid   = u.id    if hasattr(u, "id")    else u.get("id")
            email = u.email if hasattr(u, "email") else u.get("email")
            if uid in user_ids:
                email_map[uid] = email or "unknown@example.com"
    except Exception:
        pass
    for uid in user_ids:
        email_map.setdefault(uid, "unknown@example.com")
    return email_map


def _log_transaction(admin, row: dict):
    """Insert a transaction-log row. Runs as a background task."""
    try:
        admin.table("transaction-log").insert(row).execute()
    except Exception:
        pass


def _send_email(user_email: str, subject: str, body_html: str):
    """Send a transactional email via Resend. No-op if RESEND_API_KEY is not set."""
    from config import settings as cfg
    if not cfg.resend_api_key:
        return
    try:
        import resend
        resend.api_key = cfg.resend_api_key
        resend.Emails.send({
            "from":    cfg.email_from,
            "to":      [user_email],
            "subject": subject,
            "html":    body_html,
        })
    except Exception:
        pass


def _notify_trade(
    admin, user_id: str, user_email: str,
    from_cur: str, to_cur: str,
    sent_amount: float, received_amount: float,
    rate: float, now: datetime,
):
    """Build a rich trade confirmation email and send it if notifications are enabled."""
    from email_builder import build_trade_email
    from forex_service import get_historical_ohlc
    try:
        pref = admin.table("user-preferences").select("enable_notification").eq("id", user_id).execute()
        if not (pref.data and pref.data[0].get("enable_notification")):
            return

        # Fetch 30-day OHLC for the sparkline — already cached so usually instant
        closes: list[float] = []
        try:
            candles = get_historical_ohlc(from_cur, to_cur, "1mo")
            closes  = [c["close"] for c in candles if c.get("close")]
        except Exception:
            pass

        subject, html = build_trade_email(
            from_cur=from_cur, to_cur=to_cur,
            sent_amount=sent_amount, received_amount=received_amount,
            rate=rate, now=now, sparkline_closes=closes,
        )
        _send_email(user_email, subject, html)
    except Exception:
        pass


def _notify_transfer(
    admin, user_id: str, user_email: str,
    currency: str, amount: float, to_email: str, now: datetime,
):
    """Build a transfer confirmation email and send it if notifications are enabled."""
    from email_builder import build_transfer_email
    try:
        pref = admin.table("user-preferences").select("enable_notification").eq("id", user_id).execute()
        if not (pref.data and pref.data[0].get("enable_notification")):
            return
        subject, html = build_transfer_email(
            currency=currency, amount=amount, to_email=to_email, now=now,
        )
        _send_email(user_email, subject, html)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/exchange", response_model=ExchangeResponse)
async def exchange(
    body: ExchangeRequest,
    background_tasks: BackgroundTasks,
    current=Depends(get_current_user),
):
    """Convert from_currency -> to_currency at the current live rate."""
    user_id  = current["user"].id
    from_cur = body.from_currency.upper()
    to_cur   = body.to_currency.upper()
    admin    = get_supabase_admin()

    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Exchange amount must be positive.")
    if from_cur == to_cur:
        raise HTTPException(status_code=400, detail="Cannot exchange a currency for itself.")

    # Fetch from-balance and live rate in parallel
    try:
        balance, rate = await asyncio.gather(
            asyncio.to_thread(_get_holding, admin, user_id, from_cur),
            asyncio.to_thread(get_rate, from_cur, to_cur),
        )
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    if balance < body.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds: have {balance} {from_cur}, need {body.amount}.",
        )

    received_amount = round(body.amount * rate, 8)
    now = datetime.now(timezone.utc)

    # Debit from-currency and fetch to-currency balance in parallel
    _, current_to = await asyncio.gather(
        asyncio.to_thread(_upsert_holding, admin, user_id, from_cur, round(balance - body.amount, 8)),
        asyncio.to_thread(_get_holding, admin, user_id, to_cur),
    )
    await asyncio.to_thread(_upsert_holding, admin, user_id, to_cur, round(current_to + received_amount, 8))

    broker_id = settings.broker_user_id or user_id
    background_tasks.add_task(_log_transaction, admin, {
        "sender_id":                       user_id,
        "receiver_id":                     broker_id,
        "sender_currency_ticker_symbol":   from_cur,
        "receiver_currency_ticker_symbol": to_cur,
        "sender-amount":                   body.amount,
        "receiver-amount":                 received_amount,
        "timestamp":                       now.isoformat(),
        "type":                            "EXCHANGE",
    })
    background_tasks.add_task(
        _notify_trade, admin, user_id, current["user"].email,
        from_cur, to_cur, body.amount, received_amount, rate, now,
    )

    return ExchangeResponse(
        transaction_id="pending",   # log is async; id not needed by client
        from_currency=from_cur,
        to_currency=to_cur,
        sent_amount=body.amount,
        received_amount=received_amount,
        rate=rate,
        timestamp=now,
    )


@router.post("/transfer")
async def transfer(
    body: TransferRequest,
    background_tasks: BackgroundTasks,
    current=Depends(get_current_user),
):
    """Send a fixed currency amount directly to another user by email."""
    sender_id = current["user"].id
    currency  = body.currency.upper().strip()
    admin     = get_supabase_admin()

    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be positive.")
    if len(currency) != 3:
        raise HTTPException(status_code=400, detail="Currency must be a 3-letter ticker.")

    # Find receiver and fetch sender balance in parallel
    receiver, balance = await asyncio.gather(
        asyncio.to_thread(_find_user_by_email, admin, body.to_email),
        asyncio.to_thread(_get_holding, admin, sender_id, currency),
    )

    if not receiver:
        raise HTTPException(status_code=404, detail=f"No user found with email {body.to_email}.")
    receiver_id = receiver.id if hasattr(receiver, "id") else receiver.get("id")
    if receiver_id == sender_id:
        raise HTTPException(status_code=400, detail="Cannot transfer funds to yourself.")
    if balance < body.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds: have {balance} {currency}, need {body.amount}.",
        )

    now = datetime.now(timezone.utc)

    # Debit sender and fetch receiver balance in parallel
    _, receiver_balance = await asyncio.gather(
        asyncio.to_thread(_upsert_holding, admin, sender_id, currency, round(balance - body.amount, 8)),
        asyncio.to_thread(_get_holding, admin, receiver_id, currency),
    )
    await asyncio.to_thread(_upsert_holding, admin, receiver_id, currency, round(receiver_balance + body.amount, 8))

    background_tasks.add_task(_log_transaction, admin, {
        "sender_id":                       sender_id,
        "receiver_id":                     receiver_id,
        "sender_currency_ticker_symbol":   currency,
        "receiver_currency_ticker_symbol": currency,
        "sender-amount":                   body.amount,
        "receiver-amount":                 body.amount,
        "timestamp":                       now.isoformat(),
        "type":                            "EXCHANGE",
    })
    background_tasks.add_task(
        _notify_transfer, admin, sender_id, current["user"].email,
        currency, body.amount, body.to_email, now,
    )

    return {
        "transaction_id": "pending",
        "to_email":       body.to_email,
        "currency":       currency,
        "amount":         body.amount,
        "timestamp":      now,
    }


@router.get("/history")
async def history(current=Depends(get_current_user)):
    """
    Return all transactions for the current user, deduplicated and enriched
    with emails. Sent + received queries fire in parallel.
    """
    user_id = current["user"].id
    admin   = get_supabase_admin()

    # Fire both DB queries simultaneously
    try:
        sent, received = await asyncio.gather(
            asyncio.to_thread(
                lambda: admin.table("transaction-log")
                    .select("*").eq("sender_id", user_id)
                    .order("timestamp", desc=True).execute()
            ),
            asyncio.to_thread(
                lambda: admin.table("transaction-log")
                    .select("*").eq("receiver_id", user_id)
                    .order("timestamp", desc=True).execute()
            ),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    seen, txs = set(), []
    for tx in sent.data + received.data:
        tid = tx.get("transaction_id")
        if tid not in seen:
            seen.add(tid)
            txs.append(tx)

    uid_set = {tx.get("sender_id") for tx in txs} | {tx.get("receiver_id") for tx in txs}
    uid_set.discard(None)
    email_map = await asyncio.to_thread(_build_email_map, admin, uid_set)

    for tx in txs:
        tx["sender_email"]   = email_map.get(tx.get("sender_id"),   "unknown@example.com")
        tx["receiver_email"] = email_map.get(tx.get("receiver_id"), "unknown@example.com")

    txs.sort(key=lambda x: x.get("timestamp") or "", reverse=True)
    return {"transactions": txs}


@router.get("/rate")
async def trade_rate(from_currency: str, to_currency: str):
    """Return the current exchange rate without executing a trade."""
    try:
        rate = await asyncio.to_thread(get_rate, from_currency.upper(), to_currency.upper())
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"from_currency": from_currency.upper(), "to_currency": to_currency.upper(), "rate": rate}
