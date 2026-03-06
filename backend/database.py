from supabase import create_client, Client
from config import settings

# Anon client — used for auth operations (respects RLS)
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

# Admin client — uses service role key, bypasses RLS for trusted server-side operations
supabase_admin: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)


def get_supabase() -> Client:
    return supabase


def get_supabase_admin() -> Client:
    return supabase_admin
