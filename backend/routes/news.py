"""
News routes — integrates NewsAPI for forex news and Reddit for WSB posts.
"""

from fastapi import APIRouter, HTTPException
from config import settings
import httpx
from datetime import datetime, timedelta

router = APIRouter()


async def _get_reddit_oauth_token(client: httpx.AsyncClient) -> str:
    """
    Obtain a Reddit app-only OAuth token via client credentials.
    Requires REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in settings.
    """
    resp = await client.post(
        "https://www.reddit.com/api/v1/access_token",
        data={"grant_type": "client_credentials"},
        auth=(settings.reddit_client_id, settings.reddit_client_secret),
        headers={"User-Agent": "script:fxtrade:v1.0"},
        timeout=10.0,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


@router.get("/reddit/wsb")
async def get_wsb_posts(limit: int = 10):
    """
    Return hot posts from r/wallstreetbets.
    Query params:
      - limit: max number of posts (default 10, max 25)

    Uses Reddit OAuth app-only auth when REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET
    are set in the environment (recommended). Falls back to the public .json
    endpoint when credentials are absent.
    """
    limit = max(1, min(limit, 25))

    # Fetch a few extra to account for filtered stickied posts
    fetch_limit = limit + 5

    use_oauth = bool(settings.reddit_client_id and settings.reddit_client_secret)

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            if use_oauth:
                token = await _get_reddit_oauth_token(client)
                url = f"https://oauth.reddit.com/r/wallstreetbets/hot?limit={fetch_limit}&raw_json=1"
                headers = {
                    "Authorization": f"Bearer {token}",
                    "User-Agent": "script:fxtrade:v1.0",
                }
            else:
                # Public JSON endpoint fallback.
                # Reddit requires a descriptive bot user-agent — browser user-agents
                # are blocked for server-side requests since mid-2023.
                url = f"https://www.reddit.com/r/wallstreetbets/hot.json?limit={fetch_limit}&raw_json=1"
                headers = {
                    "User-Agent": "script:fxtrade:v1.0 (read-only news aggregator)"
                }

            resp = await client.get(url, headers=headers)
            resp.raise_for_status()

            # Guard against Reddit returning HTML (login / error page) instead of JSON
            content_type = resp.headers.get("content-type", "")
            if "json" not in content_type and not resp.text.lstrip().startswith("{"):
                raise HTTPException(
                    502,
                    "Reddit returned a non-JSON response — the public API may be temporarily unavailable. "
                    "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET for reliable access."
                )

            payload = resp.json()

    except httpx.HTTPStatusError as exc:
        raise HTTPException(exc.response.status_code, f"Reddit API error: {exc.response.text[:200]}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(502, f"Failed to fetch Reddit posts: {str(exc)}")
    
    posts = []
    for post_data in payload.get("data", {}).get("children", []):
        post = post_data.get("data", {})
        
        # Skip stickied/pinned posts
        if post.get("stickied"):
            continue
        
        # Try to get high-quality preview image
        thumbnail = None
        preview_images = post.get("preview", {}).get("images", [])
        if preview_images:
            # Get the source image URL (highest quality)
            source = preview_images[0].get("source", {})
            thumbnail = source.get("url", "")
            # Decode HTML entities in URL
            if thumbnail:
                thumbnail = thumbnail.replace("&amp;", "&")
        
        # Fallback to thumbnail if no preview
        if not thumbnail:
            thumbnail = post.get("thumbnail", "")
            if thumbnail in ["self", "default", "nsfw", "spoiler", ""]:
                thumbnail = None
        
        # Format timestamp as relative time
        created = post.get("created_utc", 0)
        now = datetime.utcnow().timestamp()
        hours_ago = int((now - created) / 3600)
        time_str = f"{hours_ago}h ago" if hours_ago < 24 else f"{int(hours_ago / 24)}d ago"
        
        posts.append({
            "id": post.get("id"),
            "title": post.get("title", "Untitled"),
            "author": post.get("author", "Unknown"),
            "score": post.get("score", 0),
            "num_comments": post.get("num_comments", 0),
            "time": time_str,
            "url": f"https://www.reddit.com{post.get('permalink', '')}",
            "thumbnail": thumbnail,
            "flair": post.get("link_flair_text", ""),
            "selftext": post.get("selftext", "")[:200] + "..." if post.get("selftext") else ""
        })
        
        if len(posts) >= limit:
            break
    
    return {"status": "ok", "posts": posts}


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

    # Build more specific query strings for better relevance
    # Use AND operators to ensure all results are forex-related
    if q:
        # User search - add forex context to improve relevance
        query = f'({q}) AND (forex OR "foreign exchange" OR "currency market" OR FX OR "exchange rate")'
    elif currency:
        # Currency-specific - focus on that currency in forex context
        query = f'({currency}) AND (forex OR "foreign exchange" OR "currency market" OR "exchange rate" OR "central bank")'
    else:
        # Default forex news with quality sources
        query = '(forex OR "foreign exchange" OR "currency trading" OR FX) AND ("exchange rate" OR market OR trader OR "central bank")'

    # Only fetch what we need - add small buffer for potential bad articles
    fetch_limit = min(limit + 5, 100)

    params = {
        "apiKey": settings.newsapi_key,
        "language": "en",
        "pageSize": fetch_limit,
        "q": query,
        "sortBy": "publishedAt",
        "page": 1,
        "from": (datetime.utcnow() - timedelta(days=14)).isoformat() + 'Z',  # Last 14 days for more relevant news
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

    # Light filtering - only exclude obvious spam
    articles = []
    spam_keywords = ['recipe', 'fashion show', 'celebrity gossip', 'entertainment awards', 'sports score', 'weather forecast', 'horoscope']
    
    for idx, a in enumerate(payload.get("articles", [])):
        title = (a.get("title") or "").lower()
        
        # Skip obvious spam
        is_spam = any(spam in title for spam in spam_keywords)
        
        if not is_spam:
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
            
            if len(articles) >= limit:
                break

    # If no results after filtering, try simpler fallback (only for custom queries)
    if not articles and q:
        fallback_params = params.copy()
        fallback_params["q"] = "forex market"
        fallback_params["pageSize"] = limit
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=fallback_params)
                resp.raise_for_status()
                fallback_payload = resp.json()
                if fallback_payload.get("status") == "ok":
                    for idx, a in enumerate(fallback_payload.get("articles", [])[:limit]):
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
                "headline": "Forex market update: No recent headlines available. Please check back soon.",
                "date": datetime.utcnow().date().isoformat(),
                "image": "https://placehold.co/400x300/1a1a1a/FFD700?text=FX",
                "source": "FXTrade", 
                "url": "",
            }
        ]

    return {"status": "ok", "articles": articles}
