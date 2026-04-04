<template>
  <div class="container mx-auto px-0 py-0">
    <!-- Centered Search Bar with Expand Animation -->
    <div class="mb-6 flex justify-center">
      <div 
        ref="searchContainer"
        class="relative transition-all duration-300 ease-out"
        :class="searchFocused ? 'w-full max-w-3xl' : 'w-full max-w-xl'"
      >
        <div class="relative">
          <!-- Search Icon (Yellow) -->
          <div class="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          
          <input
            ref="searchInput"
            v-model="searchQuery"
            @focus="handleSearchFocus"
            @keyup.enter="performSearch"
            type="text"
            placeholder="Search financial news..."
            class="w-full pl-12 pr-12 py-3 bg-bg-secondary border border-gray-700 rounded-full text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all"
          />
          
          <!-- Clear Button (X) -->
          <button
            v-if="searchQuery"
            @click="clearSearch"
            class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Search Suggestions Dropdown with Animation -->
        <transition
          enter-active-class="transition ease-out duration-200"
          enter-from-class="opacity-0 translate-y-1"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition ease-in duration-150"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 translate-y-1"
        >
          <div
            v-if="showSearchSuggestions && !searchQuery"
            class="absolute top-full left-0 right-0 mt-2 bg-bg-secondary border border-gray-700 rounded-2xl shadow-2xl z-50 overflow-hidden"
          >
            <div class="overflow-y-auto" style="max-height: 400px;">
              <div
                v-for="suggestion in searchSuggestions"
                :key="suggestion.query"
                @click="selectSuggestion(suggestion.query)"
                class="px-5 py-3 hover:bg-primary/10 cursor-pointer border-b border-gray-800 last:border-b-0 transition-all hover:pl-6"
              >
                <div class="text-sm text-white font-medium">{{ suggestion.label }}</div>
                <div class="text-xs text-gray-400 mt-0.5">{{ suggestion.description }}</div>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <div class="mb-4">
      <p v-if="loading" class="text-sm text-gray-300">Loading world news...</p>
      <p v-if="error" class="text-sm text-red-400">{{ error }}</p>
    </div>

    <!-- Curated News: 2-card bento + one row of 4 (6 stories; API fetch trimmed & deduped in store) -->
    <h2 class="text-4xl font-bold text-primary mb-6 font-goldman">Curated News</h2>

    <div v-if="!loading && !error && !featuredStories.length && !regularStories.length" class="text-center text-gray-400 py-20">
      No news available right now. Try again in a moment.
    </div>

    <div class="bento-grid mb-6">
      <NewsStoryCard
        v-for="story in featuredStories"
        :key="story.id"
        :story="story"
        :featured="true"
        :class="story.size"
      />
    </div>

    <div class="news-grid news-grid-four mb-6">
      <NewsStoryCard
        v-for="story in regularStories"
        :key="story.id"
        :story="story"
      />
    </div>

    <div v-if="currentSearchQuery && !loading && regularStories.length > 0" class="flex justify-center mb-10">
      <button
        type="button"
        class="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
        @click="loadMoreNews"
      >
        Load More Articles
      </button>
    </div>

    <RedditHotCarousel
      title="r/wallstreetbets"
      :posts="wsbPosts"
      :loading="wsbLoading"
      :error="wsbError"
    />
    <RedditHotCarousel
      title="r/economics"
      :posts="econPosts"
      :loading="econLoading"
      :error="econError"
    />

    <!-- S&P 500 sector heatmap (TradingView stock treemap — equities, not futures) -->
    <section class="mb-10" aria-label="S and P 500 stock heatmap">
      <h2 class="text-4xl font-bold text-primary mb-2 font-goldman">S&amp;P 500 heatmap</h2>
      <div
        class="glass rounded-xl overflow-hidden border border-gray-700 p-2 md:p-4 min-h-[180px] h-[62vh] max-h-[400px] flex flex-col"
      >
        <TradingViewStockHeatmap class="min-h-0 flex-1" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import NewsStoryCard from '@/components/NewsStoryCard.vue'
import RedditHotCarousel from '@/components/RedditHotCarousel.vue'
import TradingViewStockHeatmap from '@/components/TradingViewStockHeatmap.vue'
import { useNewsStore } from '@/stores/news'
import { newsApi } from '@/services/api'
import { fetchWallstreetbetsPosts, fetchEconomicsPosts } from '@/composables/useReddit'

const newsStore = useNewsStore()

const featuredStories = ref([])
const regularStories = ref([])
const error = ref(null)
const loading = ref(false)
const searchQuery = ref('')
const currentSearchQuery = ref(null)
const moreCount = ref(0)
const showSearchSuggestions = ref(false)
const searchFocused = ref(false)
const searchContainer = ref(null)
const searchInput = ref(null)

// Reddit carousels (fetched client-side; see RedditHotCarousel.vue)
const wsbPosts = ref([])
const wsbLoading = ref(false)
const wsbError = ref(null)

const econPosts = ref([])
const econLoading = ref(false)
const econError = ref(null)

// Hardcoded forex-related search suggestions
const searchSuggestions = [
  { query: 'forex trading', label: 'Forex Trading', description: 'Currency market news and analysis' },
  { query: 'central bank', label: 'Central Bank News', description: 'Fed, ECB, BOJ policy updates' },
  { query: 'USD EUR GBP JPY', label: 'Major Currencies', description: 'News about major currency pairs' },
  { query: 'interest rates', label: 'Interest Rates', description: 'Rate decisions and economic policy' },
  { query: 'currency volatility', label: 'Market Volatility', description: 'Currency fluctuations and trends' },
  { query: 'exchange rate', label: 'Exchange Rates', description: 'Global exchange rate movements' },
  { query: 'economic indicators', label: 'Economic Data', description: 'GDP, inflation, employment reports' },
  { query: 'emerging markets currency', label: 'Emerging Markets', description: 'EM currency developments' }
]

// Click outside handler to close dropdown
function handleClickOutside(event) {
  if (searchContainer.value && !searchContainer.value.contains(event.target)) {
    searchFocused.value = false
    showSearchSuggestions.value = false
  }
}

function handleSearchFocus() {
  searchFocused.value = true
  if (!searchQuery.value) {
    showSearchSuggestions.value = true
  }
}

function selectSuggestion(query) {
  searchQuery.value = query
  showSearchSuggestions.value = false
  searchFocused.value = false
  performSearch()
}

const CURATED_TOTAL = 6
const CURATED_FETCH = 8

function storyUrlKey(story) {
  return (story.url || '').trim().toLowerCase()
}

async function loadNews(query = null) {
  loading.value = true
  error.value = null
  moreCount.value = 0

  const normalizedQuery = query && String(query).trim() ? String(query).trim() : null
  currentSearchQuery.value = normalizedQuery

  try {
    const articles = await newsStore.fetchNews(normalizedQuery, CURATED_FETCH)

    if (!articles || articles.length === 0) {
      error.value = 'No news articles found. Please try again later.'
      featuredStories.value = []
      regularStories.value = []
      return
    }

    const top = articles.slice(0, CURATED_TOTAL)
    const processed = top.map((article, index) => ({
      ...article,
      size: index === 0 ? 'large' : index === 1 ? 'medium' : undefined,
    }))

    featuredStories.value = processed.slice(0, 2)
    regularStories.value = processed.slice(2, CURATED_TOTAL)
  } catch (err) {
    console.error('Error loading news:', err)
    const status = err.response?.status
    const serverDetail = err.response?.data?.detail || err.response?.data?.message
    error.value = serverDetail || `Unable to load news${status ? ` (HTTP ${status})` : ''}.`
  } finally {
    loading.value = false
  }
}

function performSearch() {
  if (searchQuery.value.trim()) {
    searchFocused.value = false
    showSearchSuggestions.value = false
    loadNews(searchQuery.value.trim())
  }
}

function clearSearch() {
  searchQuery.value = ''
  searchFocused.value = false
  showSearchSuggestions.value = false
  loadNews()
}

async function loadMoreNews() {
  if (!currentSearchQuery.value) return
  
  loading.value = true
  error.value = null
  moreCount.value += 1

  try {
    const { data } = await newsApi.getNews(undefined, 9, currentSearchQuery.value)
    
    if (data.status !== 'ok' || !data.articles) {
      error.value = 'No more articles available'
      return
    }

    const seen = new Set(
      [...featuredStories.value, ...regularStories.value].map(storyUrlKey).filter(Boolean)
    )

    const articles = data.articles
      .map((article, index) => ({
        id: article.id || `more-${moreCount.value}-${index}`,
        headline: article.headline || article.title || 'Untitled',
        date: article.date || '',
        image: article.image || 'https://placehold.co/400x300/1a1a1a/FFD700?text=No+Image',
        url: article.url,
        source: article.source,
      }))
      .filter((a) => {
        const k = storyUrlKey(a)
        if (!k) return true
        if (seen.has(k)) return false
        seen.add(k)
        return true
      })

    regularStories.value.push(...articles)
  } catch (err) {
    const status = err.response?.status
    const serverDetail = err.response?.data?.detail || err.response?.data?.message
    error.value = serverDetail || `Unable to load more news${status ? ` (HTTP ${status})` : ''}.`
  } finally {
    loading.value = false
  }
}

async function loadWsbPosts() {
  wsbLoading.value = true
  wsbError.value = null

  try {
    wsbPosts.value = await fetchWallstreetbetsPosts(12)
  } catch (err) {
    console.error('[WSB] Failed to load WSB posts:', err)
    wsbError.value = 'Unable to load r/wallstreetbets posts.'
  } finally {
    wsbLoading.value = false
  }
}

async function loadEconomicsPosts() {
  econLoading.value = true
  econError.value = null

  try {
    econPosts.value = await fetchEconomicsPosts(12)
  } catch (err) {
    console.error('[Economics] Failed to load r/economics posts:', err)
    econError.value = 'Unable to load r/economics posts.'
  } finally {
    econLoading.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  loadNews()
  loadWsbPosts()
  loadEconomicsPosts()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

</script>

<style scoped>
/* Bento Box Grid for Featured Stories */
.bento-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

@media (min-width: 768px) {
  .bento-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 250px);
  }

  .large {
    grid-column: 1;
    grid-row: span 2;
  }

  .medium:nth-child(2) {
    grid-column: 2;
    grid-row: 1 / span 2;
  }
}

@media (min-width: 1024px) {
  .bento-grid {
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(2, 280px);
  }

  .large {
    grid-column: 1 / 3;
    grid-row: span 2;
  }

  .medium:nth-child(2) {
    grid-column: 3;
    grid-row: 1 / span 2;
  }
}

/* Regular News Grid */
.news-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 640px) {
  .news-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .news-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1280px) {
  .news-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* Single row of four under the bento (curated strip) */
.news-grid-four {
  grid-template-columns: 1fr;
}

@media (min-width: 640px) {
  .news-grid-four {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .news-grid-four {
    grid-template-columns: repeat(4, 1fr);
  }
}

</style>

