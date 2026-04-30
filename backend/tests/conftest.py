"""
Shared test fixtures.

Order of operations matters: env vars and supabase.create_client must be patched
BEFORE config.py / database.py are imported, otherwise Settings() blows up and
real Supabase clients get instantiated.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# --- 1. Make backend/ importable -------------------------------------------
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# --- 2. Set env vars required by config.Settings ---------------------------
os.environ.setdefault("SUPABASE_URL", "http://test.supabase.local")
os.environ.setdefault("SUPABASE_KEY", "test-anon-key")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
os.environ.setdefault("BROKER_USER_ID", "broker-uuid-0000")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")

# --- 3. Stub supabase.create_client before database.py imports it ----------
import supabase as _supabase_module  # noqa: E402

_fake_anon = MagicMock(name="supabase_anon_client")
_fake_admin = MagicMock(name="supabase_admin_client")
_create_calls = {"n": 0}


def _fake_create_client(url, key):
    _create_calls["n"] += 1
    # First call in database.py is anon, second is admin (see database.py)
    return _fake_anon if _create_calls["n"] == 1 else _fake_admin


_supabase_module.create_client = _fake_create_client

# Now safe to import application modules
import database  # noqa: E402
import forex_service  # noqa: E402
from auth import get_current_user  # noqa: E402
from main import app  # noqa: E402

# Force database module-level singletons to point at our mocks
database.supabase = _fake_anon
database.supabase_admin = _fake_admin


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TEST_USER_ID = "test-user-uuid-1111"
TEST_USER_EMAIL = "tester@example.com"


class _FakeUser:
    def __init__(self, uid: str, email: str):
        self.id = uid
        self.email = email


@pytest.fixture
def test_user():
    return _FakeUser(TEST_USER_ID, TEST_USER_EMAIL)


@pytest.fixture
def supabase_admin(monkeypatch):
    """Fresh admin mock per test; swapped into database.supabase_admin so
    routes that call get_supabase_admin() see it."""
    fresh = MagicMock(name="supabase_admin_client_per_test")
    monkeypatch.setattr(database, "supabase_admin", fresh)
    return fresh


@pytest.fixture
def supabase_anon(monkeypatch):
    fresh = MagicMock(name="supabase_anon_client_per_test")
    monkeypatch.setattr(database, "supabase", fresh)
    return fresh


@pytest.fixture(autouse=True)
def _reset_forex_caches():
    """Forex service uses module-level dicts; clear them between tests."""
    forex_service._cache.clear()
    forex_service._history_cache.clear()
    forex_service._ohlc_cache.clear()
    yield
    forex_service._cache.clear()
    forex_service._history_cache.clear()
    forex_service._ohlc_cache.clear()


@pytest.fixture
def client(test_user):
    """
    FastAPI TestClient with get_current_user overridden to inject `test_user`.
    Each test that needs the admin client should access it via the
    `supabase_admin` fixture and configure return values before calling routes.
    """
    from fastapi.testclient import TestClient

    async def _fake_current_user():
        return {"user": test_user, "access_token": "test-token"}

    app.dependency_overrides[get_current_user] = _fake_current_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
