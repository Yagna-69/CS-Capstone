from pathlib import Path
from pydantic_settings import BaseSettings

# Resolve paths relative to this file so the app works regardless of cwd.
_BACKEND_DIR = Path(__file__).resolve().parent   # .../backend/


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str                  # anon/public key
    supabase_service_role_key: str     # service role key (bypasses RLS for admin ops)
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_url: str = "http://localhost:5173"
    additional_origins: str = ""       # comma-separated additional CORS origins
    # Broker account: a dedicated Supabase auth user whose UUID acts as the exchange counterparty
    broker_user_id: str = ""
    # Gemini API key — reserved for future AI insight feature
    gemini_api_key: str = ""
    newsapi_key: str = ""
    # Resend API key for transactional emails (trade confirmations etc.)
    resend_api_key: str = ""
    # From address shown on outgoing emails — must be a verified domain in Resend
    # Use onboarding@resend.dev for testing (works without domain verification)
    email_from: str = "FXTrade <onboarding@resend.dev>"

    class Config:
        env_file = str(_BACKEND_DIR / ".env")
        case_sensitive = False


settings = Settings()
