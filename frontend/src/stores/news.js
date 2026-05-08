import { defineStore } from 'pinia'
import { ref } from 'vue'
import { newsApi } from '@/services/api'

const REDDIT_CACHE_TTL_MS = 15 * 60 * 1000  // 15 min — Reddit posts change slowly

function dedupeArticlesByUrl(articles) {
  const seen = new Set()
  const out = []
  for (const a of articles) {
    const u = (a.url || '').trim().toLowerCase()
    if (u) {
      if (seen.has(u)) continue
      seen.add(u)
    } else {
      const k = `${(a.headline || '').trim().toLowerCase()}|${(a.source || '').trim().toLowerCase()}`
      if (seen.has(k)) continue
      seen.add(k)
    }
    out.push(a)
  }
  return out
}

/**
 * Centralized news caching store to reduce API calls.
 * Caches news results for 5 minutes per unique query.
 */
export const useNewsStore = defineStore('news', () => {
  const CACHE_TTL_MS = 30 * 60 * 1000  // 30 minutes — NewsAPI free tier = 100 req/day
  
  // Cache structure: { query: { articles: [...], fetchedAt: timestamp } }
  const cache = ref({})
  
  /**
   * Fetch news with caching.
   * Cache key is query-only (not limit) so the same query at different limits
   * reuses the same cached result instead of burning extra API calls.
   * @param {string} query - Search query (null for default forex news)
   * @param {number} limit - Number of articles to return (sliced from cached set)
   * @returns {Promise<Array>} - Array of articles
   */
  async function fetchNews(query = null, limit = 10) {
    const cacheKey = query || 'forex-default'
    const now = Date.now()
    
    // Check cache — return a slice so callers with smaller limits get fewer items
    const cached = cache.value[cacheKey]
    if (cached && (now - cached.fetchedAt) < CACHE_TTL_MS) {
      return cached.articles.slice(0, limit)
    }

    // Deduplicate in-flight requests for the same query
    if (cache.value[`${cacheKey}:inflight`]) {
      await cache.value[`${cacheKey}:inflight`]
      const fresh = cache.value[cacheKey]
      return fresh ? fresh.articles.slice(0, limit) : []
    }

    // Fetch fresh data — always request a generous page size so the cache
    // covers all callers regardless of their individual limit argument.
    const FETCH_SIZE = 20
    let resolve
    cache.value[`${cacheKey}:inflight`] = new Promise(r => { resolve = r })

    try {
      const searchQuery = query || 'forex'
      const { data } = await newsApi.getNews(undefined, FETCH_SIZE, searchQuery)
      
      if (data.status === 'ok' && data.articles) {
        const mapped = data.articles.map((article, index) => ({
          id: article.id || `${cacheKey}-${index}`,
          headline: article.headline || article.title || 'Untitled',
          date: article.date || '',
          image: article.image || 'https://placehold.co/400x300/1a1a1a/FFD700?text=No+Image',
          url: article.url,
          source: article.source,
          description: article.description || ''
        }))

        const articles = dedupeArticlesByUrl(mapped)
        cache.value[cacheKey] = { articles, fetchedAt: now }
        return articles.slice(0, limit)
      }
      return []
    } catch (err) {
      console.error('[NewsStore] Failed to fetch news:', err)
      if (cached) return cached.articles.slice(0, limit)
      throw err
    } finally {
      delete cache.value[`${cacheKey}:inflight`]
      resolve?.()
    }
  }
  
  /**
   * Clear cache for a specific query or all cache
   * @param {string} query - Optional query to clear, or null to clear all
   */
  function clearCache(query = null) {
    if (query === null) {
      cache.value = {}
      console.log('[NewsStore] Cleared all cache')
    } else {
      Object.keys(cache.value).forEach(key => {
        if (key.startsWith(query)) {
          delete cache.value[key]
          console.log(`[NewsStore] Cleared cache for "${key}"`)
        }
      })
    }
  }
  
  // ── Reddit cache ─────────────────────────────────────────────────────────
  const redditCache = ref({})  // { 'wsb' | 'economics': { posts, fetchedAt } }

  /**
   * @param {string} subreddit  'wsb' | 'economics'
   * @param {number} limit
   * @param {Function} [fetchFn]  optional custom fetcher; defaults to backend proxy.
   *   Pass a direct-browser fetch function to bypass the backend (needed on Cloud Run
   *   where GCP IPs are blocked by Reddit).
   */
  async function fetchRedditPosts(subreddit, limit = 12, fetchFn = null) {
    const now    = Date.now()
    const cached = redditCache.value[subreddit]
    if (cached && (now - cached.fetchedAt) < REDDIT_CACHE_TTL_MS) {
      return cached.posts.slice(0, limit)
    }

    // Deduplicate in-flight
    const inflightKey = `${subreddit}:inflight`
    if (redditCache.value[inflightKey]) {
      await redditCache.value[inflightKey]
      const fresh = redditCache.value[subreddit]
      return fresh ? fresh.posts.slice(0, limit) : []
    }

    let resolve
    redditCache.value[inflightKey] = new Promise(r => { resolve = r })

    try {
      let posts
      if (fetchFn) {
        // Caller provides a custom fetcher (e.g. browser-direct with fallback)
        posts = await fetchFn()
        
        // If fetchFn returns null, it signals to fall back to backend proxy
        if (posts === null) {
          const apiFetcher = subreddit === 'wsb'
            ? () => newsApi.getWsbPosts(limit)
            : () => newsApi.getEconomicsPosts(limit)
          const { data } = await apiFetcher()
          posts = (data?.posts || []).map(p => ({
            id:           p.id,
            title:        p.title,
            author:       p.author,
            score:        p.score,
            num_comments: p.num_comments,
            time:         p.time,
            url:          p.url,
            thumbnail:    p.thumbnail    || null,
            outbound_url: p.outbound_url || null,
            flair:        p.flair        || '',
            selftext:     p.selftext     || '',
          }))
        }
      } else {
        // Default: backend proxy
        const apiFetcher = subreddit === 'wsb'
          ? () => newsApi.getWsbPosts(limit)
          : () => newsApi.getEconomicsPosts(limit)
        const { data } = await apiFetcher()
        posts = (data?.posts || []).map(p => ({
          id:           p.id,
          title:        p.title,
          author:       p.author,
          score:        p.score,
          num_comments: p.num_comments,
          time:         p.time,
          url:          p.url,
          thumbnail:    p.thumbnail    || null,
          outbound_url: p.outbound_url || null,
          flair:        p.flair        || '',
          selftext:     p.selftext     || '',
        }))
      }
      redditCache.value[subreddit] = { posts, fetchedAt: now }
      return posts.slice(0, limit)
    } catch (err) {
      if (cached) return cached.posts.slice(0, limit)
      throw err
    } finally {
      delete redditCache.value[inflightKey]
      resolve?.()
    }
  }

  return {
    fetchNews,
    fetchRedditPosts,
    clearCache,
    cache,
    redditCache,
  }
})
