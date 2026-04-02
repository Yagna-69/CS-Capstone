"""
News routes — SKELETON.

TODO: Integrate a forex news API (e.g. NewsAPI, Alpha Vantage News, Benzinga).
      Add NEWSAPI_KEY (or equivalent) to config.py and .env when ready.
"""

from fastapi import APIRouter, HTTPException
from config import settings
import httpx
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/")
async def get_news(currency: str = None, limit: int = 10, q: str = None):
    """
    Return forex news articles.
    Optional query params:
      - currency: filter by ticker (e.g. "USD")
      - limit: max number of articles (default 10)
      - q: user search query (free text)
    """
    if not settings.newsapi_key:
        raise HTTPException(500, "NEWSAPI_KEY is not configured")

    limit = max(1, min(limit, 100))  # Allow up to 100 articles per request

    # For NewsAPI, use search for user queries, default gets forex news
    if q:
        query = q
    else:
        query = "forex"  # Default to forex news

    # Fetch more articles - NewsAPI will return available results
    fetch_limit = min(limit * 2, 100)

    params = {
        "apiKey": settings.newsapi_key,
        "language": "en",
        "pageSize": fetch_limit,
        "q": query,
        "sortBy": "publishedAt",
        "page": 1,
        "from": (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z',
    }

    url = "https://newsapi.org/v2/everything"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            payload = resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(exc.response.status_code, f"News API error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(502, f"Failed to fetch news: {str(exc)}")

    if payload.get("status") != "ok":
        raise HTTPException(502, f"NewsAPI bad status: {payload.get('message', 'unknown')}")

    articles = []
    for idx, a in enumerate(payload.get("articles", [])):
        image_url = a.get("urlToImage") or "https://placehold.co/400x300/1a1a1a/FFD700?text=No+Image"
        published_at = a.get("publishedAt") or ""
        articles.append({
            "id": a.get("url") or str(idx),
            "headline": a.get("title") or "Untitled",
            "date": (published_at[:10] if published_at else ""),
            "image": image_url,
            "source": a.get("source", {}).get("name", "Unknown"),
            "url": a.get("url"),
            "description": a.get("description", ""),
        })

    # No additional filtering - rely on NewsAPI's relevance
    articles = articles[:limit]

    # If no results, fallback to broader search
    if not articles and q:
        fallback_params = params.copy()
        fallback_params["q"] = "forex"  # Remove search to get general forex news
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=fallback_params)
                resp.raise_for_status()
                fallback_payload = resp.json()
                if fallback_payload.get("status") == "ok":
                    for idx, a in enumerate(fallback_payload.get("articles", [])):
                        if len(articles) >= limit:
                            break
                        image_url = a.get("urlToImage") or "https://placehold.co/400x300/1a1a1a/FFD700?text=No+Image"
                        published_at = a.get("publishedAt") or ""
                        articles.append({
                            "id": a.get("url") or f"fallback-{idx}",
                            "headline": a.get("title") or "Untitled",
                            "date": (published_at[:10] if published_at else ""),
                            "image": image_url,
                            "source": a.get("source", {}).get("name", "Unknown"),
                            "url": a.get("url"),
                            "description": a.get("description", ""),
                        })
        except Exception:
            pass  # Ignore fallback errors

    if not articles:
        # Safety fallback item so UI has something to display
        articles = [
            {
                "id": "fx-fallback-1",
                "headline": "Forex update: No recent economic headlines, please try again in a few minutes.",
                "date": datetime.utcnow().date().isoformat(),
                "image": "https://placehold.co/400x300/1a1a1a/FFD700?text=FX",
                "source": "FXTrade", 
                "url": "",
            }
        ]

    return {"status": "ok", "articles": articles}
