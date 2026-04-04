/**
 * Composable for fetching Reddit data directly from the frontend
 * Bypasses backend to avoid GCP IP blocking issues
 */

const REDDIT_MEDIA_HOSTS = new Set([
  'external-preview.redd.it',
  'preview.redd.it',
  'i.redd.it',
  'external-preview.redditmedia.com',
  'preview.redditmedia.com',
])

function decodeRedditUrl(url) {
  if (!url || typeof url !== 'string') return null
  return url.replace(/&amp;/g, '&').trim()
}

function isRedditHostedMediaUrl(url) {
  const decoded = decodeRedditUrl(url)
  if (!decoded) return false
  try {
    const host = new URL(decoded).hostname.toLowerCase().replace(/^www\./, '')
    return REDDIT_MEDIA_HOSTS.has(host)
  } catch {
    return false
  }
}

/** Thumbnail URL from preview object, post.url (link posts often use external-preview.redd.it), or legacy thumbnail field */
function pickPostThumbnail(post) {
  const previewImages = post.preview?.images || []
  if (previewImages.length > 0) {
    const first = previewImages[0]
    const fromSource = decodeRedditUrl(first?.source?.url)
    if (fromSource) return fromSource
    const resolutions = first?.resolutions || []
    if (resolutions.length > 0) {
      const largest = resolutions[resolutions.length - 1]
      const fromRes = decodeRedditUrl(largest?.url)
      if (fromRes) return fromRes
    }
  }

  const oembed = post.secure_media?.oembed || post.media?.oembed
  const oembedThumb = decodeRedditUrl(oembed?.thumbnail_url)
  if (oembedThumb) return oembedThumb

  const submissionUrl = decodeRedditUrl(post.url)
  if (submissionUrl && isRedditHostedMediaUrl(submissionUrl)) {
    return submissionUrl
  }

  const thumbUrl = post.thumbnail || ''
  if (!['self', 'default', 'nsfw', 'spoiler', ''].includes(thumbUrl)) {
    return decodeRedditUrl(thumbUrl) || thumbUrl
  }

  return null
}

/** External article URL for link posts (Reddit JSON often omits preview images for these). */
function outboundArticleUrl(post) {
  if (post.is_self) return null
  const u = decodeRedditUrl(post.url)
  if (!u || !/^https?:\/\//i.test(u)) return null
  try {
    const h = new URL(u).hostname.toLowerCase()
    if (h === 'redd.it' || h === 'reddit.com' || h.endsWith('.reddit.com') || h.endsWith('.redd.it')) {
      return null
    }
    if (isRedditHostedMediaUrl(u)) return null
    return u
  } catch {
    return null
  }
}

/**
 * Microlink fallback (OG image) — only used when Reddit’s JSON already gave no thumbnail.
 * Not called for posts where pickPostThumbnail() found preview / thumbnail / reddit media URL.
 */
const ogImageMemory = new Map()
const ogImageInflight = new Map()

const LS_OG_PREFIX = 'capstone:redditOgThumb:v1:'
/** Successful image URL: reuse across refreshes; publisher OG images rarely change. */
const OG_PERSIST_TTL_MS = 7 * 24 * 60 * 60 * 1000
/** “No image” from API: short TTL so we retry later without hammering. */
const OG_PERSIST_NEGATIVE_TTL_MS = 60 * 60 * 1000

function lsOgKey(articleUrl) {
  return LS_OG_PREFIX + encodeURIComponent(articleUrl)
}

/** @returns {undefined | null | string} undefined = no entry; null = cached miss */
function readPersistentOg(articleUrl) {
  try {
    const raw = localStorage.getItem(lsOgKey(articleUrl))
    if (!raw) return undefined
    const row = JSON.parse(raw)
    const ttl = row.fail ? OG_PERSIST_NEGATIVE_TTL_MS : OG_PERSIST_TTL_MS
    if (Date.now() - row.t > ttl) {
      localStorage.removeItem(lsOgKey(articleUrl))
      return undefined
    }
    return row.imageUrl
  } catch {
    return undefined
  }
}

function writePersistentOg(articleUrl, imageUrl, fail) {
  try {
    localStorage.setItem(
      lsOgKey(articleUrl),
      JSON.stringify({ imageUrl, fail: !!fail, t: Date.now() })
    )
  } catch {
    /* quota / private mode — in-memory cache still helps within the session */
  }
}

async function fetchOgImageForUrl(articleUrl) {
  if (ogImageMemory.has(articleUrl)) return ogImageMemory.get(articleUrl)
  if (ogImageInflight.has(articleUrl)) return ogImageInflight.get(articleUrl)

  const persisted = readPersistentOg(articleUrl)
  if (persisted !== undefined) {
    ogImageMemory.set(articleUrl, persisted)
    return persisted
  }

  const pending = (async () => {
    try {
      const res = await fetch(
        `https://api.microlink.io/?url=${encodeURIComponent(articleUrl)}`
      )
      const json = await res.json()
      const img =
        json.status === 'success' && json.data?.image?.url
          ? json.data.image.url
          : null
      ogImageMemory.set(articleUrl, img)
      writePersistentOg(articleUrl, img, !img)
      return img
    } catch {
      ogImageMemory.set(articleUrl, null)
      writePersistentOg(articleUrl, null, true)
      return null
    } finally {
      ogImageInflight.delete(articleUrl)
    }
  })()

  ogImageInflight.set(articleUrl, pending)
  return pending
}

/**
 * For posts Reddit did not supply a preview for, resolve thumbnail via OG (Microlink).
 * Skips any post that already has `thumbnail`. Deduplicates by `outboundUrl` per batch.
 * Uses memory + localStorage so refresh / repeat articles do not call Microlink again (until TTL).
 */
export async function enrichRedditPostThumbnails(posts) {
  const need = posts.filter((p) => !p.thumbnail && p.outboundUrl)
  if (need.length === 0) return posts

  const unique = [...new Set(need.map((p) => p.outboundUrl))]
  const batchSize = 4
  for (let i = 0; i < unique.length; i += batchSize) {
    await Promise.all(unique.slice(i, i + batchSize).map((u) => fetchOgImageForUrl(u)))
  }
  for (const p of posts) {
    if (!p.thumbnail && p.outboundUrl) {
      const img = ogImageMemory.get(p.outboundUrl)
      if (img) p.thumbnail = img
    }
  }
  return posts
}

/**
 * @param {string} subreddit e.g. "wallstreetbets" or "economics"
 */
export async function fetchSubredditHotPosts(subreddit, limit = 12) {
  const fetchLimit = limit + 5 // Fetch extra to account for filtered posts
  const url = `https://www.reddit.com/r/${subreddit}/hot.json?limit=${fetchLimit}`
  
  try {
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Reddit API returned ${response.status}`)
    }
    
    const payload = await response.json()
    const children = payload?.data?.children || []
    
    const posts = []
    for (const item of children) {
      const post = item?.data || {}
      
      // Skip stickied/pinned posts
      if (post.stickied) continue
      
      const thumbnail = pickPostThumbnail(post)
      // Only keep article URL when Reddit gave no image (Microlink fallback); avoids noise and clarifies intent.
      const outboundUrl = thumbnail ? null : outboundArticleUrl(post)

      // Calculate relative time
      const created = post.created_utc || 0
      const now = Date.now() / 1000
      const hoursAgo = Math.floor((now - created) / 3600)
      const timeStr = hoursAgo < 24 
        ? `${hoursAgo}h ago` 
        : `${Math.floor(hoursAgo / 24)}d ago`
      
      posts.push({
        id: post.id,
        title: post.title || 'Untitled',
        author: post.author || 'Unknown',
        score: post.score || 0,
        num_comments: post.num_comments || 0,
        time: timeStr,
        url: `https://www.reddit.com${post.permalink || ''}`,
        thumbnail,
        outboundUrl,
        flair: post.link_flair_text || '',
        selftext: post.selftext ? post.selftext.substring(0, 200) + '...' : ''
      })
      
      if (posts.length >= limit) break
    }
    
    return posts
  } catch (error) {
    console.error(`Failed to fetch r/${subreddit} posts:`, error)
    throw error
  }
}

export async function fetchWallstreetbetsPosts(limit = 12) {
  return fetchSubredditHotPosts('wallstreetbets', limit)
}

export async function fetchEconomicsPosts(limit = 12) {
  const posts = await fetchSubredditHotPosts('economics', limit)
  // OG fallback only for posts with no Reddit preview; cached in memory + localStorage (see enrichRedditPostThumbnails).
  await enrichRedditPostThumbnails(posts)
  return posts
}
