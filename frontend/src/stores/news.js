import { defineStore } from 'pinia'
import { ref } from 'vue'
import { newsApi } from '@/services/api'

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
  const CACHE_TTL_MS = 5 * 60 * 1000  // 5 minutes
  
  // Cache structure: { query: { articles: [...], fetchedAt: timestamp } }
  const cache = ref({})
  
  /**
   * Fetch news with caching.
   * @param {string} query - Search query (null for default forex news)
   * @param {number} limit - Number of articles to fetch
   * @returns {Promise<Array>} - Array of articles
   */
  async function fetchNews(query = null, limit = 10) {
    const cacheKey = `${query || 'forex-default'}:${limit}`
    const now = Date.now()
    
    // Check cache
    const cached = cache.value[cacheKey]
    if (cached && (now - cached.fetchedAt) < CACHE_TTL_MS) {
      console.log(`[NewsStore] Using cached news for "${cacheKey}"`)
      return cached.articles
    }
    
    // Fetch fresh data
    console.log(`[NewsStore] Fetching fresh news for "${cacheKey}"`)
    try {
      // Pass query as-is, or 'forex' as default if null
      const searchQuery = query || 'forex'
      const { data } = await newsApi.getNews(undefined, limit, searchQuery)
      
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

        // Update cache
        cache.value[cacheKey] = {
          articles,
          fetchedAt: now
        }

        return articles
      }
      
      // If no articles, return empty array
      return []
    } catch (err) {
      console.error('[NewsStore] Failed to fetch news:', err)
      // Return cached data if available, even if stale
      if (cached) {
        console.log(`[NewsStore] Returning stale cache for "${cacheKey}"`)
        return cached.articles
      }
      throw err
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
  
  return {
    fetchNews,
    clearCache,
    cache
  }
})
