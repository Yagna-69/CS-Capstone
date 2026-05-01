/**
 * Reddit data via the backend proxy (/api/news/reddit/*).
 *
 * Primary thumbnails are resolved server-side from Reddit's JSON.
 * For posts where the server found no image but there IS an outbound article
 * URL, we progressively enhance with Microlink OG images — cached in
 * localStorage so each URL is only fetched once (7-day TTL).
 */
import { useNewsStore } from '@/stores/news'

// ---------------------------------------------------------------------------
// Microlink OG image cache (localStorage + in-memory, same as original)
// ---------------------------------------------------------------------------
const _ogMemory  = new Map()
const _ogFlight  = new Map()
const LS_PREFIX  = 'capstone:redditOgThumb:v1:'
const TTL_HIT    = 7  * 24 * 60 * 60 * 1000   // 7 days for real images
const TTL_MISS   = 1  * 60 * 60 * 1000         // 1 hour for "no image" result

function _lsRead(url) {
  try {
    const raw = localStorage.getItem(LS_PREFIX + encodeURIComponent(url))
    if (!raw) return undefined
    const row = JSON.parse(raw)
    const ttl = row.fail ? TTL_MISS : TTL_HIT
    if (Date.now() - row.t > ttl) { localStorage.removeItem(LS_PREFIX + encodeURIComponent(url)); return undefined }
    return row.img   // null = confirmed miss, string = URL
  } catch { return undefined }
}

function _lsWrite(url, img) {
  try {
    localStorage.setItem(
      LS_PREFIX + encodeURIComponent(url),
      JSON.stringify({ img, fail: img === null, t: Date.now() })
    )
  } catch { /* quota / private mode — in-memory still works */ }
}

async function _fetchOg(articleUrl) {
  if (_ogMemory.has(articleUrl)) return _ogMemory.get(articleUrl)
  if (_ogFlight.has(articleUrl)) return _ogFlight.get(articleUrl)

  const persisted = _lsRead(articleUrl)
  if (persisted !== undefined) { _ogMemory.set(articleUrl, persisted); return persisted }

  const pending = (async () => {
    try {
      const res  = await fetch(`https://api.microlink.io/?url=${encodeURIComponent(articleUrl)}`)
      const json = await res.json()
      const img  = json.status === 'success' && json.data?.image?.url ? json.data.image.url : null
      _ogMemory.set(articleUrl, img)
      _lsWrite(articleUrl, img)
      return img
    } catch {
      _ogMemory.set(articleUrl, null)
      _lsWrite(articleUrl, null)
      return null
    } finally { _ogFlight.delete(articleUrl) }
  })()

  _ogFlight.set(articleUrl, pending)
  return pending
}

// ---------------------------------------------------------------------------
// Public helpers
// ---------------------------------------------------------------------------

function _normalise(p) {
  return {
    id:           p.id,
    title:        p.title,
    author:       p.author,
    score:        p.score,
    num_comments: p.num_comments,
    time:         p.time,
    url:          p.url,
    thumbnail:    p.thumbnail    || null,
    outboundUrl:  p.outbound_url || null,
    flair:        p.flair        || '',
    selftext:     p.selftext     || '',
  }
}

/**
 * Progressively enrich posts that have no thumbnail but do have an outbound
 * article URL using Microlink.  Batched 4 at a time; results are cached so
 * repeat renders don't re-fetch.
 */
export async function enrichRedditPostThumbnails(posts) {
  const need = posts.filter(p => !p.thumbnail && p.outboundUrl)
  if (!need.length) return posts

  const unique = [...new Set(need.map(p => p.outboundUrl))]
  for (let i = 0; i < unique.length; i += 4) {
    await Promise.all(unique.slice(i, i + 4).map(_fetchOg))
  }
  for (const p of posts) {
    if (!p.thumbnail && p.outboundUrl) {
      const img = _ogMemory.get(p.outboundUrl)
      if (img) p.thumbnail = img
    }
  }
  return posts
}

export async function fetchWallstreetbetsPosts(limit = 12) {
  const store = useNewsStore()
  const posts = await store.fetchRedditPosts('wsb', limit)
  return enrichRedditPostThumbnails(posts.map(_normalise))
}

export async function fetchEconomicsPosts(limit = 12) {
  const store = useNewsStore()
  const posts = await store.fetchRedditPosts('economics', limit)
  return enrichRedditPostThumbnails(posts.map(_normalise))
}
