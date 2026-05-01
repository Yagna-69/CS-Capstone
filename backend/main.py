import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routes import api_router  # routes/ package — replaces the old routes.py

POLL_INTERVAL_SECS  = 3   # check pending orders every N seconds
WARM_INTERVAL_SECS  = 8   # proactively refresh forex cache before TTL expires (TTL=10s)


def _process_pending_orders_sync():
    """
    Synchronous worker — runs in a thread pool so blocking I/O (yfinance + supabase)
    never freezes the async event loop.

    Order fill logic:
      Limit      — fill when rate <= target_price  (buy cheaper)
      Stop       — fill when rate >= target_price  (stop-loss / breakout)
      Stop-Limit — fill when target_price <= rate <= limit_price
    """
    from database import get_supabase_admin
    from forex_service import get_rate
    from config import settings as cfg

    admin = get_supabase_admin()

    try:
        resp = admin.table("pending-orders").select("*").eq("status", "PENDING").execute()
        orders = resp.data or []
    except Exception:
        return

    # Cache rates per pair so we only call yfinance once per pair per cycle
    rate_cache: dict[str, float] = {}

    for order in orders:
        try:
            order_id   = order["order_id"]
            user_id    = order["user_id"]
            from_cur   = order["from_currency"]
            to_cur     = order["to_currency"]
            amount     = float(order["amount"])
            order_type = order["order_type"]
            target     = float(order["target_price"])
            limit_p    = float(order["limit_price"]) if order.get("limit_price") else None

            pair_key = f"{from_cur}{to_cur}"
            if pair_key not in rate_cache:
                try:
                    rate_cache[pair_key] = get_rate(from_cur, to_cur)
                except Exception:
                    continue
            rate = rate_cache[pair_key]

            should_fill = False
            if order_type == "Limit":
                should_fill = rate <= target
            elif order_type == "Stop":
                should_fill = rate >= target
            elif order_type == "Stop-Limit":
                should_fill = (rate >= target) and (limit_p is not None) and (rate <= limit_p)

            if not should_fill:
                continue

            # Verify user still has the balance before executing
            bal_resp = (
                admin.table("portfolio")
                .select("amount")
                .eq("id", user_id)
                .eq("currency-ticker-symbol", from_cur)
                .execute()
            )
            balance = float(bal_resp.data[0]["amount"]) if bal_resp.data else 0.0
            if balance < amount:
                admin.table("pending-orders").update({"status": "CANCELLED"}).eq("order_id", order_id).execute()
                continue

            received = round(amount * rate, 8)
            now = datetime.now(timezone.utc)

            def _upsert(uid, cur, new_amt):
                ex = (admin.table("portfolio").select("*")
                      .eq("id", uid).eq("currency-ticker-symbol", cur).execute())
                if ex.data:
                    admin.table("portfolio").update({"amount": new_amt}).eq("id", uid).eq("currency-ticker-symbol", cur).execute()
                else:
                    admin.table("portfolio").insert({"id": uid, "currency-ticker-symbol": cur, "amount": new_amt}).execute()

            _upsert(user_id, from_cur, round(balance - amount, 8))
            to_bal_resp = (admin.table("portfolio").select("amount")
                           .eq("id", user_id).eq("currency-ticker-symbol", to_cur).execute())
            to_bal = float(to_bal_resp.data[0]["amount"]) if to_bal_resp.data else 0.0
            _upsert(user_id, to_cur, round(to_bal + received, 8))

            broker_id = cfg.broker_user_id or user_id
            admin.table("transaction-log").insert({
                "sender_id":                       user_id,
                "receiver_id":                     broker_id,
                "sender_currency_ticker_symbol":   from_cur,
                "receiver_currency_ticker_symbol": to_cur,
                "sender-amount":                   amount,
                "receiver-amount":                 received,
                "timestamp":                       now.isoformat(),
                "type":                            "EXCHANGE",
            }).execute()

            admin.table("pending-orders").update({
                "status":    "FILLED",
                "filled_at": now.isoformat(),
            }).eq("order_id", order_id).execute()

        except Exception:
            continue


async def _fill_pending_orders():
    """
    Async loop: wakes every POLL_INTERVAL_SECS and offloads the blocking
    sync worker to a thread so the event loop stays responsive.
    """
    while True:
        await asyncio.sleep(POLL_INTERVAL_SECS)
        try:
            await asyncio.to_thread(_process_pending_orders_sync)
        except Exception:
            continue


async def _warm_forex_cache():
    """
    Proactively refresh the forex rate cache every WARM_INTERVAL_SECS so that
    client polls (every 5s) always hit a warm cache entry instead of blocking
    on a yfinance network call.
    """
    from forex_service import warm_active_pairs
    while True:
        await asyncio.sleep(WARM_INTERVAL_SECS)
        try:
            await asyncio.to_thread(warm_active_pairs)
        except Exception:
            continue


@asynccontextmanager
async def lifespan(app: FastAPI):
    pending_task = asyncio.create_task(_fill_pending_orders())
    warmer_task  = asyncio.create_task(_warm_forex_cache())
    yield
    pending_task.cancel()
    warmer_task.cancel()
    for t in (pending_task, warmer_task):
        try:
            await t
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="FXTrade API",
    description="Backend API for the FXTrade forex platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Capstone API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
