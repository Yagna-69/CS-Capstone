"""
AI Insight routes — SKELETON.

TODO: Integrate Google Gemini API using the gemini_api_key from config.
      Suggested library: google-generativeai
      Add "google-generativeai" to requirements.txt when ready.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from auth import get_current_user
# from config import settings  # Uncomment when wiring up Gemini

router = APIRouter()


class InsightRequest(BaseModel):
    prompt: str             # e.g. "Should I buy AUD with my USD right now?"
    context_pairs: list[str] = []  # e.g. ["USDAUD", "USDCAD"]


@router.post("/")
async def get_insight(body: InsightRequest, current=Depends(get_current_user)):
    """
    Ask the AI for a market insight or trading suggestion.
    Requires authentication so responses can be personalised to the user's portfolio.
    """
    # TODO: Build prompt with live rates + user portfolio context
    # TODO: Call Gemini API with settings.gemini_api_key
    # TODO: Return structured response

    return {
        "status": "not_implemented",
        "message": "AI insight feature coming soon.",
        "response": None,
    }
