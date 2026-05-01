"""
Orders routes — place and manage pending limit/stop orders.

Endpoints:
  POST /orders/          — place a new limit, stop, or stop-limit order
  GET  /orders/          — list all pending (and recent) orders for the user
  DELETE /orders/{id}    — cancel a pending order

Orders are stored in the `pending-orders` Supabase table and filled by the
background checker in main.py (runs every POLL_INTERVAL_SECS seconds).

Table schema (pending-orders):
  order_id        uuid PK default gen_random_uuid()
  user_id         uuid  (FK auth.users)
  from_currency   text
  to_currency     text
  amount          numeric
  order_type      text   -- 'Limit' | 'Stop' | 'Stop-Limit'
  target_price    numeric
  limit_price     numeric nullable
  status          text   -- 'PENDING' | 'FILLED' | 'CANCELLED'
  created_at      timestamptz default now()
  filled_at       timestamptz nullable
"""

import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from models import PlaceOrderRequest, OrderResponse
from database import get_supabase_admin
from auth import get_current_user

router = APIRouter()

ALLOWED_TYPES = {"Limit", "Stop", "Stop-Limit"}


@router.post("/", response_model=OrderResponse)
async def place_order(body: PlaceOrderRequest, current=Depends(get_current_user)):
    user_id = current["user"].id
    admin   = get_supabase_admin()

    from_cur = body.from_currency.upper()
    to_cur   = body.to_currency.upper()

    if body.order_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"order_type must be one of {ALLOWED_TYPES}.")
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive.")
    if body.target_price <= 0:
        raise HTTPException(status_code=400, detail="Target price must be positive.")
    if body.order_type == "Stop-Limit":
        if not body.limit_price or body.limit_price <= 0:
            raise HTTPException(status_code=400, detail="Stop-Limit orders require a limit_price.")
        if body.limit_price < body.target_price:
            raise HTTPException(status_code=400, detail="limit_price must be >= target_price (stop price).")

    # Verify the user has enough balance to reserve the funds
    existing = await asyncio.to_thread(
        lambda: admin.table("portfolio").select("amount")
            .eq("id", user_id).eq("currency-ticker-symbol", from_cur).execute()
    )
    balance = float(existing.data[0]["amount"]) if existing.data else 0.0
    if balance < body.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds: have {balance:.4f} {from_cur}, need {body.amount}.",
        )

    now = datetime.now(timezone.utc)
    row = {
        "user_id":        user_id,
        "from_currency":  from_cur,
        "to_currency":    to_cur,
        "amount":         body.amount,
        "order_type":     body.order_type,
        "target_price":   body.target_price,
        "limit_price":    body.limit_price,
        "status":         "PENDING",
        "created_at":     now.isoformat(),
    }
    try:
        resp = await asyncio.to_thread(lambda: admin.table("pending-orders").insert(row).execute())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    created = resp.data[0]
    return OrderResponse(
        order_id=created["order_id"],
        from_currency=created["from_currency"],
        to_currency=created["to_currency"],
        amount=float(created["amount"]),
        order_type=created["order_type"],
        target_price=float(created["target_price"]),
        limit_price=float(created["limit_price"]) if created.get("limit_price") else None,
        status=created["status"],
        created_at=created["created_at"],
    )


@router.get("/")
async def list_orders(current=Depends(get_current_user)):
    user_id = current["user"].id
    admin   = get_supabase_admin()
    try:
        resp = await asyncio.to_thread(
            lambda: admin.table("pending-orders").select("*")
                .eq("user_id", user_id).order("created_at", desc=True).limit(50).execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"orders": resp.data}


@router.delete("/{order_id}")
async def cancel_order(order_id: str, current=Depends(get_current_user)):
    user_id = current["user"].id
    admin   = get_supabase_admin()

    existing = await asyncio.to_thread(
        lambda: admin.table("pending-orders").select("status")
            .eq("order_id", order_id).eq("user_id", user_id).execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Order not found.")
    if existing.data[0]["status"] != "PENDING":
        raise HTTPException(status_code=400, detail="Only PENDING orders can be cancelled.")

    try:
        await asyncio.to_thread(
            lambda: admin.table("pending-orders").update({"status": "CANCELLED"}).eq("order_id", order_id).execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {"message": "Order cancelled."}
