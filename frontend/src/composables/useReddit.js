/**
 * Reddit data — fetched DIRECTLY from the browser (not via backend proxy).
 *
 * Why direct: Reddit blocks GCP/Cloud Run IP ranges with 403, so routing
 * through the backend breaks on production. Browser fetches work fine because
 * Reddit's .json API supports CORS for browser origins.
 *
 * Results are cached in the shared `news` Pinia store (15-min TTL) so
 * navigating away and back to NewsView never re-fetches.
 * Microlink OG image fallback is applied for posts with no thumbnail,
 * cached in localStorage (7-day TTL).
 */
import { useNewsStore } from '@/stores/news'

// ---------------------------------------------------------------------------
// Reddit JSON fetch (direct, browser-side)
// ---------------------------------------------------------------------------
const _REDDIT_MEDIA = new Set([
  'external-preview.redd.it', 'preview.redd.it', 'i.redd.it',
  'external-preview.redditmedia.com', 'preview.redditmedia.com',
])

function _decode(url) {
  return (url || '').replace(/&amp;/g, '&').trim()
}

function _pickThumbnail(post) {
  const imgs = post.preview?.images || []
  if (imgs.length) {
    const src = _decode(imgs[0]?.source?.url)
    if (src) return src
    const ress = imgs[0]?.resolutions || []
    if (ress.length) {
      const best = _decode(ress[ress.length - 1]?.url)
      if (best) return best
    }
  }
  const oembed = post.secure_media?.oembed || post.media?.oembed
  const oe = _decode(oembed?.thumbnail_url)
  if (oe) return oe
  const sub = _decode(post.url)
  if (sub) {
    try {
      const host = new URL(sub).hostname.toLowerCase().replace(/^www\./, '')
      if (_REDDIT_MEDIA.has(host)) return sub
    } catch { /* ignore */ }
  }
  const thumb = _decode(post.thumbnail || '')
  if (thumb && !['self', 'default', 'nsfw', 'spoiler', ''].includes(thumb)) return thumb
  return null
}

function _outboundUrl(post) {
  if (post.is_self) return null
  const u = _decode(post.url || '')
  if (!u || !/^https?:\/\//i.test(u)) return null
  try {
    const host = new URL(u).hostname.toLowerCase().replace(/^www\./, '')
    if (host === 'reddit.com' || host.endsWith('.reddit.com') ||
        host === 'redd.it'    || host.endsWith('.redd.it') ||
        _REDDIT_MEDIA.has(host)) return null
    return u
  } catch { return null }
}

async function _fetchSubredditDirect(subreddit, limit) {
  const fetchLimit = limit + 5
  const url = `https://www.reddit.com/r/${subreddit}/hot.json?limit=${fetchLimit}`
  const res = await fetch(url, { headers: { Accept: 'application/json' } })
  if (!res.ok) throw new Error(`Reddit ${res.status}`)
  const payload = await res.json()
  const posts = []
  for (const item of (payload?.data?.children || [])) {
    const p = item?.data || {}
    if (p.stickied) continue
    const thumbnail  = _pickThumbnail(p)
    const outboundUrl = thumbnail ? null : _outboundUrl(p)
    const created   = p.created_utc || 0
    const hoursAgo  = Math.floor((Date.now() / 1000 - created) / 3600)
    posts.push({
      id:           p.id,
      title:        p.title || 'Untitled',
      author:       p.author || 'Unknown',
      score:        p.score || 0,
      num_comments: p.num_comments || 0,
      time:         hoursAgo < 24 ? `${hoursAgo}h ago` : `${Math.floor(hoursAgo / 24)}d ago`,
      url:          `https://www.reddit.com${p.permalink || ''}`,
      thumbnail,
      outbound_url: outboundUrl,
      flair:        p.link_flair_text || '',
      selftext:     p.selftext ? p.selftext.slice(0, 200) + '...' : '',
    })
    if (posts.length >= limit) break
  }
  return posts
}

// ---------------------------------------------------------------------------
// Microlink OG image fallback (localStorage + in-memory, 7-day TTL)
// ---------------------------------------------------------------------------
const _ogMemory = new Map()
const _ogFlight = new Map()
const LS_PREFIX = 'capstone:redditOgThumb:v1:'
const TTL_HIT   = 7 * 24 * 60 * 60 * 1000
const TTL_MISS  = 1 * 60 * 60 * 1000

function _lsRead(url) {
  try {
    const raw = localStorage.getItem(LS_PREFIX + encodeURIComponent(url))
    if (!raw) return undefined
    const row = JSON.parse(raw)
    if (Date.now() - row.t > (row.fail ? TTL_MISS : TTL_HIT)) {
      localStorage.removeItem(LS_PREFIX + encodeURIComponent(url))
      return undefined
    }
    return row.img
  } catch { return undefined }
}

function _lsWrite(url, img) {
  try {
    localStorage.setItem(LS_PREFIX + encodeURIComponent(url),
      JSON.stringify({ img, fail: img === null, t: Date.now() }))
  } catch { /* quota / private mode */ }
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
      _ogMemory.set(articleUrl, img); _lsWrite(articleUrl, img); return img
    } catch {
      _ogMemory.set(articleUrl, null); _lsWrite(articleUrl, null); return null
    } finally { _ogFlight.delete(articleUrl) }
  })()
  _ogFlight.set(articleUrl, pending)
  return pending
}

export async function enrichRedditPostThumbnails(posts) {
  const need = posts.filter(p => !p.thumbnail && p.outboundUrl)
  if (!need.length) return posts
  const unique = [...new Set(need.map(p => p.outboundUrl))]
  for (let i = 0; i < unique.length; i += 4)
    await Promise.all(unique.slice(i, i + 4).map(_fetchOg))
  for (const p of posts)
    if (!p.thumbnail && p.outboundUrl) { const img = _ogMemory.get(p.outboundUrl); if (img) p.thumbnail = img }
  return posts
}

// ---------------------------------------------------------------------------
// Public API — uses Pinia store cache, falls back to direct fetch
// ---------------------------------------------------------------------------
export async function fetchWallstreetbetsPosts(limit = 12) {
  const store = useNewsStore()
  const posts = await store.fetchRedditPosts('wsb', limit, () => _fetchSubredditDirect('wallstreetbets', limit + 5))
  // normalise field name for Microlink (store uses outbound_url, enricher expects outboundUrl)
  const mapped = posts.map(p => ({ ...p, outboundUrl: p.outboundUrl ?? p.outbound_url ?? null }))
  return enrichRedditPostThumbnails(mapped)
}

export async function fetchEconomicsPosts(limit = 12) {
  const store = useNewsStore()
  const posts = await store.fetchRedditPosts('economics', limit, () => _fetchSubredditDirect('economics', limit + 5))
  const mapped = posts.map(p => ({ ...p, outboundUrl: p.outboundUrl ?? p.outbound_url ?? null }))
  return enrichRedditPostThumbnails(mapped)
}
