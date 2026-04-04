"""
LLM routes — chat endpoint for all users + admin API key management.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from auth import get_current_user
from database import get_supabase_admin
from llm_service import chat_completion, LLMKeyError

router = APIRouter()


# ── Helpers ──────────────────────────────────────────────────────────

def _require_admin(current):
    """Raise 403 if the user does not have is_admin enabled in user-preferences."""
    user_id = current["user"].id
    admin = get_supabase_admin()
    resp = admin.table("user-preferences").select("is_admin").eq("id", user_id).execute()
    if not resp.data or not resp.data[0].get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required.")


# ── Chat ─────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str       # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    reply: str


SYSTEM_PROMPT = (
    "You are ExLLM, a concise forex trading assistant for FXTrade. "
    "Provide brief, actionable insights. Keep responses under 5 sentences unless complex analysis is needed. "
    "Focus on data and facts, not pleasantries. Be direct and professional."
)


@router.post("/chat", response_model=ChatResponse)
async def llm_chat(body: ChatRequest, current=Depends(get_current_user)):
    """Send a message to the LLM and get a response."""
    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    try:
        reply = await chat_completion(messages, system_prompt=SYSTEM_PROMPT)
    except LLMKeyError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {str(e)}")
    return ChatResponse(reply=reply)


# ── Admin: API Key Management ────────────────────────────────────────

class ApiKeyCreate(BaseModel):
    provider: str
    api_key: str
    label: str = ""


class ApiKeyOut(BaseModel):
    id: str
    provider: str
    label: str
    is_active: bool
    created_at: str


@router.get("/keys", response_model=list[ApiKeyOut])
async def list_keys(current=Depends(get_current_user)):
    """List all LLM API keys (admin only). Raw key values are not exposed."""
    _require_admin(current)
    admin = get_supabase_admin()
    resp = (
        admin.table("llm_api_keys")
        .select("id, provider, label, is_active, created_at")
        .order("created_at")
        .execute()
    )
    return resp.data


@router.post("/keys", response_model=ApiKeyOut)
async def create_key(body: ApiKeyCreate, current=Depends(get_current_user)):
    """Add a new LLM API key (admin only)."""
    _require_admin(current)
    admin = get_supabase_admin()
    resp = (
        admin.table("llm_api_keys")
        .insert({
            "provider": body.provider,
            "api_key": body.api_key,
            "label": body.label,
        })
        .execute()
    )
    row = resp.data[0]
    return {k: row[k] for k in ("id", "provider", "label", "is_active", "created_at")}


@router.put("/keys/{key_id}/activate")
async def activate_key(key_id: str, current=Depends(get_current_user)):
    """Set a specific key as the active one, deactivating all others (admin only)."""
    _require_admin(current)
    admin = get_supabase_admin()
    # Deactivate all keys first
    admin.table("llm_api_keys").update({"is_active": False}).neq("id", "").execute()
    # Activate the chosen key
    admin.table("llm_api_keys").update({"is_active": True}).eq("id", key_id).execute()
    return {"status": "ok", "active_key_id": key_id}


@router.delete("/keys/{key_id}")
async def delete_key(key_id: str, current=Depends(get_current_user)):
    """Delete an LLM API key (admin only)."""
    _require_admin(current)
    admin = get_supabase_admin()
    admin.table("llm_api_keys").delete().eq("id", key_id).execute()
    return {"status": "deleted"}
