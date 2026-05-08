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
            placeholder="Search r/economics, r/wallstreetbets, r/news..."
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
      <p v-if="curatedLoading" class="text-sm text-gray-300">
        {{ currentSearchQuery ? 'Searching Reddit...' : 'Loading economics news...' }}
      </p>
      <p v-if="curatedError" class="text-sm text-red-400">{{ curatedError }}</p>
    </div>

    <!-- Dynamic Title: Search Results or Top Economics Stories -->
    <h2 class="text-4xl font-bold text-primary mb-6 font-goldman">
      {{ currentSearchQuery ? `Search Results: "${currentSearchQuery}"` : 'Top Economics Stories' }}
    </h2>

    <div v-if="!curatedLoading && !curatedError && !featuredStories.length && !regularStories.length" class="text-center text-gray-400 py-20">
      {{ currentSearchQuery ? 'No results found for your search.' : 'No economics stories available right now. Try again in a moment.' }}
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

    <div class="news-grid news-grid-four mb-10">
      <NewsStoryCard
        v-for="story in regularStories"
        :key="story.id"
        :story="story"
      />
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

<script>
export default { name: 'NewsView' }
</script>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import NewsStoryCard from '@/components/NewsStoryCard.vue'
import RedditHotCarousel from '@/components/RedditHotCarousel.vue'
import TradingViewStockHeatmap from '@/components/TradingViewStockHeatmap.vue'
import { fetchWallstreetbetsPosts, fetchEconomicsPosts, searchRedditPosts } from '@/composables/useReddit'

const featuredStories = ref([])
const regularStories = ref([])
const curatedError = ref(null)
const curatedLoading = ref(false)
const searchQuery = ref('')
const currentSearchQuery = ref(null)
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

// Search suggestions for Reddit (economics, wallstreetbets, news)
const searchSuggestions = [
  { query: 'forex', label: 'Forex Trading', description: 'Currency trading discussions' },
  { query: 'fed', label: 'Federal Reserve', description: 'Fed policy and rate decisions' },
  { query: 'inflation', label: 'Inflation', description: 'Inflation news and analysis' },
  { query: 'stock market', label: 'Stock Market', description: 'Market trends and analysis' },
  { query: 'recession', label: 'Recession', description: 'Economic downturn discussions' },
  { query: 'earnings', label: 'Earnings Reports', description: 'Company earnings and results' },
  { query: 'crypto', label: 'Cryptocurrency', description: 'Crypto market discussions' },
  { query: 'unemployment', label: 'Jobs & Employment', description: 'Employment data and trends' }
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
const CURATED_FETCH = 12

// Load top economics stories from r/economics for the curated section
async function loadCuratedEconomics() {
  curatedLoading.value = true
  curatedError.value = null

  try {
    const posts = await fetchEconomicsPosts(CURATED_FETCH)

    if (!posts || posts.length === 0) {
      curatedError.value = 'No economics stories found. Please try again later.'
      featuredStories.value = []
      regularStories.value = []
      return
    }

    // Transform Reddit posts to match NewsStoryCard format
    const top = posts.slice(0, CURATED_TOTAL)
    const processed = top.map((post, index) => ({
      id: post.id,
      headline: post.title,
      date: post.time,
      image: post.thumbnail || 'https://placehold.co/400x300/1a1a1a/FFD700?text=r/economics',
      url: post.url,
      source: 'r/economics',
      size: index === 0 ? 'large' : index === 1 ? 'medium' : undefined,
    }))

    featuredStories.value = processed.slice(0, 2)
    regularStories.value = processed.slice(2, CURATED_TOTAL)
  } catch (err) {
    console.error('Error loading curated economics:', err)
    curatedError.value = 'Unable to load economics stories.'
  } finally {
    curatedLoading.value = false
  }
}

async function performSearch() {
  if (!searchQuery.value.trim()) return
  
  searchFocused.value = false
  showSearchSuggestions.value = false
  
  const query = searchQuery.value.trim()
  currentSearchQuery.value = query
  
  curatedLoading.value = true
  curatedError.value = null

  try {
    // Search across r/economics, r/wallstreetbets, and r/news
    const posts = await searchRedditPosts(query, 12)

    if (!posts || posts.length === 0) {
      curatedError.value = 'No posts found for your search across Reddit.'
      featuredStories.value = []
      regularStories.value = []
      return
    }

    // Transform Reddit posts to match NewsStoryCard format
    const processed = posts.slice(0, 6).map((post, index) => ({
      id: post.id || `search-${index}`,
      headline: post.title,
      date: post.time,
      image: post.thumbnail || 'https://placehold.co/400x300/1a1a1a/FFD700?text=Reddit',
      url: post.url,
      source: `r/${post.subreddit || 'reddit'}`,
      size: index === 0 ? 'large' : index === 1 ? 'medium' : undefined,
    }))

    // Maintain bento-box layout: 2 featured + 4 regular
    featuredStories.value = processed.slice(0, 2)
    regularStories.value = processed.slice(2, 6)
  } catch (err) {
    console.error('Error searching Reddit:', err)
    curatedError.value = 'Unable to search Reddit. Please try again.'
  } finally {
    curatedLoading.value = false
  }
}

function clearSearch() {
  searchQuery.value = ''
  searchFocused.value = false
  showSearchSuggestions.value = false
  currentSearchQuery.value = null
  loadCuratedEconomics()
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
  loadCuratedEconomics()
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

