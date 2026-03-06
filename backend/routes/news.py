"""
News routes — SKELETON.

TODO: Integrate a forex news API (e.g. NewsAPI, Alpha Vantage News, Benzinga).
      Add NEWSAPI_KEY (or equivalent) to config.py and .env when ready.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_news(currency: str = None, limit: int = 10):
    """
    Return forex news articles.
    Optional query params:
      - currency: filter by ticker (e.g. "USD")
      - limit: max number of articles (default 10)
    """
    # TODO: replace stub with real news API call
    return {
        "status": "not_implemented",
        "message": "News feature coming soon.",
        "articles": [],
    }
