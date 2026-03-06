from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from models import DepositRequest, WithdrawRequest, PortfolioHolding
from database import get_supabase_admin
from auth import get_current_user

router = APIRouter()


def _normalize_currency(currency: str) -> str:
    c = currency.upper().strip()
    if len(c) != 3:
        raise HTTPException(status_code=400, detail="Currency must be a 3-letter ticker (e.g. USD).")
    return c


@router.get("/", response_model=list[PortfolioHolding])
async def get_portfolio(current=Depends(get_current_user)):
    """Return all currency holdings for the authenticated user."""
    user_id = current["user"].id
    admin = get_supabase_admin()

    try:
        response = admin.table("portfolio").select("*").eq("id", user_id).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    holdings = []
    for row in response.data:
        holdings.append(PortfolioHolding(
            currency=row["currency-ticker-symbol"],
            amount=float(row["amount"] or 0),
        ))
    return holdings


@router.post("/deposit", response_model=PortfolioHolding)
async def deposit(body: DepositRequest, current=Depends(get_current_user)):
    """
    Add funds in a given currency to the user's portfolio.
    If a holding in that currency already exists its amount is increased.
    """
    user_id = current["user"].id
    currency = _normalize_currency(body.currency)
    admin = get_supabase_admin()

    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive.")

    # Fetch existing holding for this user + currency
    try:
        existing = (
            admin.table("portfolio")
            .select("*")
            .eq("id", user_id)
            .eq("currency-ticker-symbol", currency)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if existing.data:
        current_amount = float(existing.data[0]["amount"] or 0)
        new_amount = current_amount + body.amount
        try:
            admin.table("portfolio").update({"amount": new_amount}).eq("id", user_id).eq(
                "currency-ticker-symbol", currency
            ).execute()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))
    else:
        try:
            admin.table("portfolio").insert({
                "id": user_id,
                "currency-ticker-symbol": currency,
                "amount": body.amount,
            }).execute()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

        new_amount = body.amount

    # Log the deposit
    now = datetime.now(timezone.utc)
    try:
        admin.table("transaction-log").insert({
            "sender_id": user_id,
            "receiver_id": user_id,
            "sender_currency_ticker_symbol": currency,
            "receiver_currency_ticker_symbol": currency,
            "sender-amount": body.amount,
            "receiver-amount": body.amount,
            "timestamp": now.isoformat(),
            "type": "DEPOSIT",
        }).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transaction log failed: {exc}")

    return PortfolioHolding(currency=currency, amount=new_amount)


@router.post("/withdraw", response_model=PortfolioHolding)
async def withdraw(body: WithdrawRequest, current=Depends(get_current_user)):
    """
    Withdraw funds in a given currency from the user's portfolio.
    Fails if the user has insufficient balance.
    """
    user_id = current["user"].id
    currency = _normalize_currency(body.currency)
    admin = get_supabase_admin()

    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be positive.")

    # Fetch existing holding
    try:
        existing = (
            admin.table("portfolio")
            .select("*")
            .eq("id", user_id)
            .eq("currency-ticker-symbol", currency)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    current_amount = float(existing.data[0]["amount"] or 0) if existing.data else 0.0
    if current_amount < body.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds: have {current_amount} {currency}, need {body.amount}.",
        )

    new_amount = round(current_amount - body.amount, 8)
    try:
        admin.table("portfolio").update({"amount": new_amount}).eq("id", user_id).eq(
            "currency-ticker-symbol", currency
        ).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # Log the withdrawal (negative amounts indicate outflow)
    now = datetime.now(timezone.utc)
    try:
        admin.table("transaction-log").insert({
            "sender_id": user_id,
            "receiver_id": user_id,
            "sender_currency_ticker_symbol": currency,
            "receiver_currency_ticker_symbol": currency,
            "sender-amount": -body.amount,
            "receiver-amount": -body.amount,
            "timestamp": now.isoformat(),
            "type": "WITHDRAW",
        }).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transaction log failed: {exc}")

    return PortfolioHolding(currency=currency, amount=new_amount)
