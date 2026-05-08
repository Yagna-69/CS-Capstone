"""
News routes — integrates NewsAPI for forex news and Reddit for WSB posts.

Backend cache (NEWS_CACHE_TTL) is intentionally long (30 min) to stay within
the NewsAPI free tier (100 req/day). All users share the same cache so one
fetch serves everyone until TTL expires.
"""

import time
from fastapi import APIRouter, HTTPException
from config import settings
from database import get_supabase_admin
import httpx
from datetime import datetime, timedelta

router = APIRouter()

# { cache_key: (articles_list, fetched_at) }
_news_cache: dict[str, tuple[list, float]] = {}
NEWS_CACHE_TTL = 30 * 60  # 30 minutes


def _get_newsapi_key() -> str:
    """
    Retrieve the NewsAPI key from Supabase news_api_key table.
    Falls back to settings.newsapi_key if Supabase lookup fails.
    """
    try:
        admin = get_supabase_admin()
        resp = (
            admin.table("news_api_key")
            .select("api_key")
            .limit(1)
            .execute()
        )
        if resp.data and len(resp.data) > 0:
            return resp.data[0]["api_key"]
        
        # Fallback: use .env value
        if settings.newsapi_key:
            return settings.newsapi_key
            
        raise HTTPException(500, "No NewsAPI key configured in Supabase or .env")
        
    except HTTPException:
        raise
    except Exception as e:
        # On any Supabase error, fall back to .env
        if settings.newsapi_key:
            return settings.newsapi_key
        raise HTTPException(500, f"Failed to retrieve NewsAPI key: {str(e)}")


async def _fetch_subreddit_hot(subreddit: str, limit: int) -> dict:
    """Shared helper — proxies a subreddit's hot.json through the backend to avoid CORS."""
    limit = max(1, min(limit, 25))
    fetch_limit = limit + 5
    
    # Try multiple strategies to fetch Reddit data
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/html",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    urls_to_try = [
        f"https://old.reddit.com/r/{subreddit}/hot.json?limit={fetch_limit}",
        f"https://www.reddit.com/r/{subreddit}/hot.json?limit={fetch_limit}",
        f"https://reddit.com/r/{subreddit}/hot.json?limit={fetch_limit}",
    ]
    
    payload = None
    last_error = None
    
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            for url in urls_to_try:
                try:
                    resp = await client.get(url, headers=headers)
                    if resp.status_code == 200:
                        payload = resp.json()
                        break
                    last_error = f"{resp.status_code}: {resp.text[:200]}"
                except httpx.HTTPStatusError as exc:
                    last_error = f"{exc.response.status_code}: {exc.response.text[:200]}"
                    continue
                except Exception as exc:
                    last_error = str(exc)
                    continue
            
            # All URLs failed
            if payload is None:
                raise HTTPException(503, f"Reddit temporarily unavailable. Last error: {last_error}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(502, f"Failed to fetch Reddit posts: {str(exc)}")

    _REDDIT_MEDIA = {
        "external-preview.redd.it", "preview.redd.it", "i.redd.it",
        "external-preview.redditmedia.com", "preview.redditmedia.com",
    }

    def _decode(url: str) -> str:
        return (url or "").replace("&amp;", "&").strip()

    def _pick_thumbnail(post: dict) -> str | None:
        # 1. preview.images[0].source  (highest quality)
        imgs = post.get("preview", {}).get("images", [])
        if imgs:
            src = _decode(imgs[0].get("source", {}).get("url", ""))
            if src:
                return src
            # fall through to resolutions if source is empty
            ress = imgs[0].get("resolutions", [])
            if ress:
                best = _decode(ress[-1].get("url", ""))
                if best:
                    return best

        # 2. oembed thumbnail (video/link previews)
        oembed = (post.get("secure_media") or post.get("media") or {}).get("oembed", {})
        oe_thumb = _decode(oembed.get("thumbnail_url", ""))
        if oe_thumb:
            return oe_thumb

        # 3. submission URL when it's a reddit-hosted image
        sub_url = _decode(post.get("url", ""))
        if sub_url:
            try:
                host = sub_url.split("/")[2].lower().lstrip("www.")
                if host in _REDDIT_MEDIA:
                    return sub_url
            except IndexError:
                pass

        # 4. legacy thumbnail field
        thumb = _decode(post.get("thumbnail", ""))
        if thumb and thumb not in ("self", "default", "nsfw", "spoiler"):
            return thumb

        return None

    def _outbound_url(post: dict) -> str | None:
        """External article URL for link posts — used by Microlink OG fallback on the client."""
        if post.get("is_self"):
            return None
        u = _decode(post.get("url", ""))
        if not u or not u.startswith("http"):
            return None
        try:
            host = u.split("/")[2].lower().lstrip("www.")
        except IndexError:
            return None
        if host in ("reddit.com", "redd.it") or host.endswith(".reddit.com") or host.endswith(".redd.it"):
            return None
        if host in _REDDIT_MEDIA:
            return None
        return u

    posts = []
    for post_data in payload.get("data", {}).get("children", []):
        post = post_data.get("data", {})
        if post.get("stickied"):
            continue
        thumbnail   = _pick_thumbnail(post)
        outbound    = None if thumbnail else _outbound_url(post)
        created     = post.get("created_utc", 0)
        now_ts      = datetime.utcnow().timestamp()
        hours_ago   = int((now_ts - created) / 3600)
        time_str    = f"{hours_ago}h ago" if hours_ago < 24 else f"{int(hours_ago / 24)}d ago"
        posts.append({
            "id":           post.get("id"),
            "title":        post.get("title", "Untitled"),
            "author":       post.get("author", "Unknown"),
            "score":        post.get("score", 0),
            "num_comments": post.get("num_comments", 0),
            "time":         time_str,
            "url":          f"https://www.reddit.com{post.get('permalink', '')}",
            "thumbnail":    thumbnail,
            "outbound_url": outbound,
            "flair":        post.get("link_flair_text", ""),
            "selftext":     post.get("selftext", "")[:200] + "..." if post.get("selftext") else "",
        })
        if len(posts) >= limit:
            break
    return {"status": "ok", "posts": posts}


@router.get("/reddit/wsb")
async def get_wsb_posts(limit: int = 10):
    return await _fetch_subreddit_hot("wallstreetbets", limit)


@router.get("/reddit/economics")
async def get_economics_posts(limit: int = 10):
    return await _fetch_subreddit_hot("economics", limit)


def _build_news_query(currency: str | None, q: str | None) -> str:
    if q:
        return f'({q}) AND (forex OR "foreign exchange" OR "currency market" OR FX OR "exchange rate")'
    if currency:
        return f'({currency}) AND (forex OR "foreign exchange" OR "currency market" OR "exchange rate" OR "central bank")'
    return '(forex OR "foreign exchange" OR "currency trading" OR FX) AND ("exchange rate" OR market OR trader OR "central bank")'


def _parse_articles(raw: list, max_items: int) -> list:
    spam = {'recipe', 'fashion show', 'celebrity gossip', 'entertainment awards',
            'sports score', 'weather forecast', 'horoscope'}
    out = []
    for idx, a in enumerate(raw):
        title = (a.get("title") or "").lower()
        if any(s in title for s in spam):
            continue
        published_at = a.get("publishedAt") or ""
        out.append({
            "id":          a.get("url") or str(idx),
            "headline":    a.get("title") or "Untitled",
            "date":        published_at[:10] if published_at else "",
            "image":       a.get("urlToImage") or "https://placehold.co/400x300/1a1a1a/FFD700?text=No+Image",
            "source":      a.get("source", {}).get("name", "Unknown"),
            "url":         a.get("url"),
            "description": a.get("description") or "",
        })
        if len(out) >= max_items:
            break
    return out


@router.get("/")
async def get_news(currency: str = None, limit: int = 10, q: str = None):
    """
    Return forex news articles.
    Results are cached server-side for NEWS_CACHE_TTL (30 min) so all users
    share a single NewsAPI call per unique query — staying within free tier limits.
    """
    newsapi_key = _get_newsapi_key()

    limit = max(1, min(limit, 100))

    query_str  = _build_news_query(currency, q)
    cache_key  = query_str[:120]  # cap key length
    now        = time.time()

    # Serve from cache if fresh — limit is applied as a slice, not a new API call
    cached_articles, cached_at = _news_cache.get(cache_key, (None, 0))
    if cached_articles is not None and (now - cached_at) < NEWS_CACHE_TTL:
        return {"status": "ok", "articles": cached_articles[:limit]}

    # Fetch a generous page (up to 25) so the cached set covers all callers
    FETCH_SIZE = 25
    params = {
        "apiKey":   newsapi_key,
        "language": "en",
        "pageSize": FETCH_SIZE,
        "q":        query_str,
        "sortBy":   "publishedAt",
        "page":     1,
        "from":     (datetime.utcnow() - timedelta(days=14)).isoformat() + 'Z',
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("https://newsapi.org/v2/everything", params=params)
            resp.raise_for_status()
            payload = resp.json()
    except httpx.HTTPStatusError as exc:
        # On 429 return stale cache if available, else propagate
        if exc.response.status_code == 429 and cached_articles is not None:
            return {"status": "ok", "articles": cached_articles[:limit]}
        raise HTTPException(exc.response.status_code, f"News API error: {exc.response.text}")
    except Exception as exc:
        if cached_articles is not None:
            return {"status": "ok", "articles": cached_articles[:limit]}
        raise HTTPException(502, f"Failed to fetch news: {str(exc)}")

    if payload.get("status") != "ok":
        raise HTTPException(502, f"NewsAPI bad status: {payload.get('message', 'unknown')}")

    articles = _parse_articles(payload.get("articles", []), FETCH_SIZE)

    if not articles:
        articles = [{
            "id":       "fx-fallback-1",
            "headline": "Forex market update: No recent headlines available. Please check back soon.",
            "date":     datetime.utcnow().date().isoformat(),
            "image":    "https://placehold.co/400x300/1a1a1a/FFD700?text=FX",
            "source":   "FXTrade",
            "url":      "",
        }]

    _news_cache[cache_key] = (articles, now)
    return {"status": "ok", "articles": articles[:limit]}
