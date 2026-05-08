"""
LLM service — provider-agnostic chat completion with DB-stored API keys.

Keys are fetched from the `llm_api_keys` Supabase table on every request,
allowing admins to hot-swap keys without restarting the server.
"""

import httpx
from database import get_supabase_admin


class LLMKeyError(Exception):
    """Raised when no active API key is available."""
    pass


# Provider -> OpenAI-compatible chat completions URL
_PROVIDER_URLS = {
    "openai": "https://api.openai.com/v1/chat/completions",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
}

_DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "gemini": "gemini-3.1-flash-lite-preview",
}


def get_active_llm_key() -> dict:
    """
    Fetch the currently active LLM API key from Supabase.
    Returns {"provider": str, "api_key": str}.
    Raises LLMKeyError if none found.
    """
    admin = get_supabase_admin()
    resp = (
        admin.table("llm_api_keys")
        .select("provider, api_key")
        .eq("is_active", True)
        .limit(1)
        .execute()
    )
    if not resp.data:
        raise LLMKeyError("No active LLM API key configured.")
    return resp.data[0]


async def chat_completion(messages: list[dict], system_prompt: str = "") -> str:
    """
    Send messages to the active LLM provider using OpenAI-compatible format.
    Returns the assistant's reply text.
    """
    try:
        key_info = get_active_llm_key()
        provider = key_info["provider"]
        api_key = key_info["api_key"]

        url = _PROVIDER_URLS.get(provider)
        if not url:
            raise LLMKeyError(f"Unsupported provider: {provider}")

        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        payload = {
            "model": _DEFAULT_MODELS.get(provider, "gpt-4o-mini"),
            "messages": all_messages,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except httpx.TimeoutException:
        raise Exception("LLM request timed out. Please try again.")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise Exception("LLM API key is invalid. Please contact administrator.")
        elif e.response.status_code == 429:
            raise Exception("LLM rate limit exceeded. Please try again later.")
        else:
            raise Exception(f"LLM provider returned error: {e.response.status_code}")
