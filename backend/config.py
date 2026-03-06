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
    # Broker account: a dedicated Supabase auth user whose UUID acts as the exchange counterparty
    broker_user_id: str = ""
    # Gemini API key — reserved for future AI insight feature
    gemini_api_key: str = ""

    class Config:
        env_file = str(_BACKEND_DIR / ".env")
        case_sensitive = False


settings = Settings()
