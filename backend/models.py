from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- Auth ---

class SignupRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str
    email: str


# --- Portfolio ---

class DepositRequest(BaseModel):
    currency: str   # 3-letter ticker, e.g. "USD"
    amount: float


class WithdrawRequest(BaseModel):
    currency: str   # 3-letter ticker, e.g. "USD"
    amount: float


class PortfolioHolding(BaseModel):
    currency: str
    amount: float


# --- Trading ---

class TransferRequest(BaseModel):
    to_email: str   # recipient's email address
    currency: str   # currency to send
    amount: float   # amount to send


class ExchangeRequest(BaseModel):
    from_currency: str  # currency being sold
    to_currency: str    # currency being bought
    amount: float       # amount of from_currency to exchange


class ExchangeResponse(BaseModel):
    transaction_id: str
    from_currency: str
    to_currency: str
    sent_amount: float
    received_amount: float
    rate: float
    timestamp: datetime


# --- Forex ---

class RateResponse(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
    timestamp: datetime


# --- Preferences ---

class PreferencesUpdate(BaseModel):
    enable_notification: Optional[bool] = None
    enable_darkmode: Optional[bool] = None
    device_type: Optional[str] = None   # e.g. "DESKTOP", "MOBILE", "TABLET"
    timezone: Optional[str] = None      # must match the Supabase timezone enum
