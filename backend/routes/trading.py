"""
Trading routes — currency exchange and user-to-user transfers.

Endpoints:
  POST /exchange  — convert from_currency -> to_currency at live rate
  POST /transfer  — send a fixed currency amount to another user by email
  GET  /history   — all transactions for the current user, enriched with emails
  GET  /rate      — fetch live exchange rate without executing a trade
"""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from models import ExchangeRequest, ExchangeResponse, TransferRequest
from database import get_supabase_admin
from auth import get_current_user
from forex_service import get_rate
from config import settings

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_holding(admin, user_id: str, currency: str) -> float:
    resp = (
        admin.table("portfolio")
        .select("*")
        .eq("id", user_id)
        .eq("currency-ticker-symbol", currency)
        .execute()
    )
    if resp.data:
        return float(resp.data[0]["amount"] or 0)
    return 0.0


def _upsert_holding(admin, user_id: str, currency: str, new_amount: float):
    existing = (
        admin.table("portfolio")
        .select("*")
        .eq("id", user_id)
        .eq("currency-ticker-symbol", currency)
        .execute()
    )
    if existing.data:
        admin.table("portfolio").update({"amount": new_amount}).eq("id", user_id).eq(
            "currency-ticker-symbol", currency
        ).execute()
    else:
        admin.table("portfolio").insert({
            "id": user_id,
            "currency-ticker-symbol": currency,
            "amount": new_amount,
        }).execute()


def _build_email_map(admin, user_ids: set) -> dict:
    """Return {user_id: email} for the given IDs. Falls back to placeholder on any error."""
    email_map = {}
    try:
        resp = admin.auth.admin.list_users()
        users = resp.users if hasattr(resp, "users") else resp
        for u in users:
            uid   = u.id    if hasattr(u, "id")    else u.get("id")
            email = u.email if hasattr(u, "email") else u.get("email")
            if uid in user_ids:
                email_map[uid] = email or "test@example.com"
    except Exception:
        pass
    for uid in user_ids:
        if uid not in email_map:
            email_map[uid] = "test@example.com"
    return email_map


def _find_user_by_email(admin, email: str):
    """Return the Supabase User object for the given email, or None."""
    try:
        resp  = admin.auth.admin.list_users()
        users = resp.users if hasattr(resp, "users") else resp
        return next(
            (u for u in users
             if (u.email if hasattr(u, "email") else u.get("email")) == email),
            None,
        )
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/exchange", response_model=ExchangeResponse)
async def exchange(body: ExchangeRequest, current=Depends(get_current_user)):
    """Convert from_currency -> to_currency at the current live rate."""
    user_id  = current["user"].id
    from_cur = body.from_currency.upper()
    to_cur   = body.to_currency.upper()
    admin    = get_supabase_admin()

    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Exchange amount must be positive.")
    if from_cur == to_cur:
        raise HTTPException(status_code=400, detail="Cannot exchange a currency for itself.")

    balance = _get_holding(admin, user_id, from_cur)
    if balance < body.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds: have {balance} {from_cur}, need {body.amount}.",
        )

    try:
        rate = get_rate(from_cur, to_cur)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    received_amount = round(body.amount * rate, 8)
    now = datetime.now(timezone.utc)

    try:
        _upsert_holding(admin, user_id, from_cur, round(balance - body.amount, 8))
        current_to = _get_holding(admin, user_id, to_cur)
        _upsert_holding(admin, user_id, to_cur, round(current_to + received_amount, 8))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Portfolio update failed: {exc}")

    broker_id = settings.broker_user_id or user_id
    try:
        log_resp = admin.table("transaction-log").insert({
            "sender_id":                      user_id,
            "receiver_id":                    broker_id,
            "sender_currency_ticker_symbol":  from_cur,
            "receiver_currency_ticker_symbol": to_cur,
            "sender-amount":                  body.amount,
            "receiver-amount":                received_amount,
            "timestamp":                      now.isoformat(),
            "type":                           "EXCHANGE",
        }).execute()
        transaction_id = log_resp.data[0]["transaction_id"]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transaction log failed: {exc}")

    return ExchangeResponse(
        transaction_id=transaction_id,
        from_currency=from_cur,
        to_currency=to_cur,
        sent_amount=body.amount,
        received_amount=received_amount,
        rate=rate,
        timestamp=now,
    )


@router.post("/transfer")
async def transfer(body: TransferRequest, current=Depends(get_current_user)):
    """Send a fixed currency amount directly to another user by email."""
    sender_id = current["user"].id
    currency  = body.currency.upper().strip()
    admin     = get_supabase_admin()

    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be positive.")
    if len(currency) != 3:
        raise HTTPException(status_code=400, detail="Currency must be a 3-letter ticker.")

    # Look up receiver
    receiver = _find_user_by_email(admin, body.to_email)
    if not receiver:
        raise HTTPException(status_code=404, detail=f"No user found with email {body.to_email}.")
    receiver_id = receiver.id if hasattr(receiver, "id") else receiver.get("id")
    if receiver_id == sender_id:
        raise HTTPException(status_code=400, detail="Cannot transfer funds to yourself.")

    # Check sender balance
    balance = _get_holding(admin, sender_id, currency)
    if balance < body.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds: have {balance} {currency}, need {body.amount}.",
        )

    now = datetime.now(timezone.utc)

    # Debit sender, credit receiver
    try:
        _upsert_holding(admin, sender_id, currency, round(balance - body.amount, 8))
        receiver_balance = _get_holding(admin, receiver_id, currency)
        _upsert_holding(admin, receiver_id, currency, round(receiver_balance + body.amount, 8))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Portfolio update failed: {exc}")

    # Log the transaction
    try:
        log_resp = admin.table("transaction-log").insert({
            "sender_id":                      sender_id,
            "receiver_id":                    receiver_id,
            "sender_currency_ticker_symbol":  currency,
            "receiver_currency_ticker_symbol": currency,
            "sender-amount":                  body.amount,
            "receiver-amount":                body.amount,
            "timestamp":                      now.isoformat(),
            "type":                           "EXCHANGE",
        }).execute()
        transaction_id = log_resp.data[0]["transaction_id"]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transaction log failed: {exc}")

    return {
        "transaction_id": transaction_id,
        "to_email":       body.to_email,
        "currency":       currency,
        "amount":         body.amount,
        "timestamp":      now,
    }


@router.get("/history")
async def history(current=Depends(get_current_user)):
    """
    Return all transactions for the current user, deduplicated and enriched with emails.
    Combines sent + received into a single list sorted newest-first.
    """
    user_id = current["user"].id
    admin   = get_supabase_admin()

    try:
        sent = (
            admin.table("transaction-log")
            .select("*")
            .eq("sender_id", user_id)
            .order("timestamp", desc=True)
            .execute()
        )
        received = (
            admin.table("transaction-log")
            .select("*")
            .eq("receiver_id", user_id)
            .order("timestamp", desc=True)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # Deduplicate (DEPOSIT/WITHDRAW have sender_id == receiver_id == user_id)
    seen, txs = set(), []
    for tx in sent.data + received.data:
        tid = tx.get("transaction_id")
        if tid not in seen:
            seen.add(tid)
            txs.append(tx)

    # Enrich with emails
    uid_set   = {tx.get("sender_id") for tx in txs} | {tx.get("receiver_id") for tx in txs}
    uid_set.discard(None)
    email_map = _build_email_map(admin, uid_set)

    for tx in txs:
        tx["sender_email"]   = email_map.get(tx.get("sender_id"),   "test@example.com")
        tx["receiver_email"] = email_map.get(tx.get("receiver_id"), "test@example.com")

    txs.sort(key=lambda x: x.get("timestamp") or "", reverse=True)
    return {"transactions": txs}


@router.get("/rate")
async def trade_rate(from_currency: str, to_currency: str):
    """Return the current exchange rate without executing a trade."""
    try:
        rate = get_rate(from_currency.upper(), to_currency.upper())
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return {
        "from_currency": from_currency.upper(),
        "to_currency":   to_currency.upper(),
        "rate":          rate,
    }
