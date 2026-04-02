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

    <!-- r/wallstreetbets Carousel -->
    <div class="mb-8">
      <h2 class="text-4xl font-bold text-primary mb-4 font-goldman">r/wallstreetbets</h2>

      <div v-if="wsbLoading" class="glass p-6 rounded-xl">
        <div class="text-sm text-gray-300">Loading WSB posts...</div>
      </div>
      <div v-else-if="wsbError" class="glass p-6 rounded-xl">
        <div class="text-sm text-red-400">{{ wsbError }}</div>
      </div>
      
      <div v-else-if="wsbPosts.length > 0" class="relative">
        <!-- Navigation Arrows -->
        <button
          v-if="wsbCurrentIndex > 0"
          @click="manualPrevSlide"
          class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-10 p-3 bg-bg-secondary/90 hover:bg-primary/20 rounded-full transition-colors border border-gray-700 hover:border-primary shadow-lg"
        >
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        <button
          v-if="wsbCurrentIndex + 3 < wsbPosts.length"
          @click="manualNextSlide"
          class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-10 p-3 bg-bg-secondary/90 hover:bg-primary/20 rounded-full transition-colors border border-gray-700 hover:border-primary shadow-lg"
        >
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </button>
        
        <!-- Carousel Content -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            v-for="post in visibleWsbPosts"
            :key="post.id"
            :href="post.url"
            target="_blank"
            rel="noopener noreferrer"
            class="wsb-card glass rounded-xl overflow-hidden hover:shadow-xl transition-all duration-300 cursor-pointer group"
          >
            <!-- Image Container -->
            <div 
              class="wsb-image-container relative w-full"
              :style="post.thumbnail ? {} : { background: 'radial-gradient(circle at center, rgba(255, 215, 0, 0.15) 0%, rgba(26, 26, 26, 0.95) 70%)' }"
            >
              <img 
                v-if="post.thumbnail"
                :src="post.thumbnail" 
                alt=""
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <div v-else class="flex items-center justify-center h-full">
                <svg class="w-12 h-12 text-primary/30" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                </svg>
              </div>
              <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
            </div>

            <!-- Content Footer -->
            <div class="p-4 bg-bg-primary/80 backdrop-blur-sm relative">
              <div class="flex items-start justify-between gap-2 mb-2">
                <span v-if="post.flair" class="inline-block px-2 py-0.5 bg-primary/20 text-primary text-xs font-semibold rounded flex-shrink-0">
                  {{ post.flair }}
                </span>
                <span class="text-xs text-gray-500 flex-shrink-0">{{ post.time }}</span>
              </div>
              
              <h3 class="text-sm font-bold text-white mb-2 line-clamp-2 leading-tight group-hover:text-primary transition-colors">
                {{ post.title }}
              </h3>
              
              <div class="flex items-center justify-between text-xs text-gray-500">
                <div class="flex items-center gap-3">
                  <span class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                    </svg>
                    {{ post.score }}
                  </span>
                  <span class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    {{ post.num_comments }}
                  </span>
                </div>
                <span class="text-xs">u/{{ post.author }}</span>
              </div>
            </div>
          </a>
        </div>
        
        <!-- Pagination Dots -->
        <div v-if="wsbPosts.length > 3" class="flex justify-center gap-2 mt-4">
          <button
            v-for="pageIndex in Math.ceil(wsbPosts.length / 3)"
            :key="pageIndex"
            @click="wsbCurrentIndex = (pageIndex - 1) * 3"
            :class="[
              'h-2 rounded-full transition-all',
              Math.floor(wsbCurrentIndex / 3) === pageIndex - 1 
                ? 'bg-primary w-8' 
                : 'bg-gray-600 hover:bg-gray-500 w-2'
            ]"
          />
        </div>
      </div>
    </div>

    <!-- Curated News Heading -->
    <h2 class="text-4xl font-bold text-primary mb-6 font-goldman">Curated News</h2>

    <!-- Bento Box Grid - Top Featured Stories -->
    <div class="bento-grid mb-6">
      <NewsStoryCard
        v-for="story in featuredStories"
        :key="story.id"
        :story="story"
        :featured="true"
        :class="story.size"
      />
    </div>

    <!-- Regular News Stories Grid -->
    <div v-if="!loading && !error && !featuredStories.length && !regularStories.length" class="text-center text-gray-400 py-20">
      No news available right now. Try again in a moment.
    </div>

    <div class="news-grid">
      <NewsStoryCard
        v-for="story in regularStories"
        :key="story.id"
        :story="story"
      />
    </div>

    <!-- Load More Button -->
    <div v-if="currentSearchQuery && !loading && regularStories.length > 0" class="flex justify-center mt-8 mb-8">
      <button
        @click="loadMoreNews"
        class="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
      >
        Load More Articles
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import NewsStoryCard from '@/components/NewsStoryCard.vue'
import { useNewsStore } from '@/stores/news'
import { newsApi } from '@/services/api'

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

// WSB posts carousel
const wsbPosts = ref([])
const wsbLoading = ref(false)
const wsbError = ref(null)
const wsbCurrentIndex = ref(0)
let wsbAutoRotateTimer = null

const visibleWsbPosts = computed(() => {
  return wsbPosts.value.slice(wsbCurrentIndex.value, wsbCurrentIndex.value + 3)
})

function nextWsbSlide() {
  if (wsbCurrentIndex.value + 3 < wsbPosts.value.length) {
    wsbCurrentIndex.value += 3
  } else {
    wsbCurrentIndex.value = 0  // Loop back to start
  }
}

function prevWsbSlide() {
  if (wsbCurrentIndex.value > 0) {
    wsbCurrentIndex.value -= 3
  } else {
    // Go to last page
    const totalPages = Math.ceil(wsbPosts.value.length / 3)
    wsbCurrentIndex.value = (totalPages - 1) * 3
  }
}

function startWsbAutoRotate() {
  stopWsbAutoRotate()
  if (wsbPosts.value.length > 3) {
    wsbAutoRotateTimer = setInterval(() => {
      nextWsbSlide()
    }, 8000)  // Rotate every 8 seconds
  }
}

function stopWsbAutoRotate() {
  if (wsbAutoRotateTimer) {
    clearInterval(wsbAutoRotateTimer)
    wsbAutoRotateTimer = null
  }
}

// Pause auto-rotate when user manually navigates
function manualNextSlide() {
  stopWsbAutoRotate()
  nextWsbSlide()
  setTimeout(startWsbAutoRotate, 15000)  // Resume after 15s
}

function manualPrevSlide() {
  stopWsbAutoRotate()
  prevWsbSlide()
  setTimeout(startWsbAutoRotate, 15000)  // Resume after 15s
}

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

async function loadNews(query = null) {
  loading.value = true
  error.value = null
  moreCount.value = 0  // Reset pagination

  try {
    // Use cached news from store
    const articles = await newsStore.fetchNews(query, 15)  // 3 featured + 12 regular
    
    if (!articles || articles.length === 0) {
      error.value = 'No news articles found. Please try again later.'
      featuredStories.value = []
      regularStories.value = []
      return
    }
    
    const processedArticles = articles.map((article, index) => ({
      ...article,
      size: index === 0 ? 'large' : index <= 2 ? 'medium' : undefined,
    }))

    featuredStories.value = processedArticles.slice(0, 3)
    regularStories.value = processedArticles.slice(3, 15)  // Show up to 12 small cards
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

    // Convert and append new articles
    const articles = data.articles.map((article, index) => ({
      id: article.id || `more-${moreCount.value}-${index}`,
      headline: article.headline || article.title || 'Untitled',
      date: article.date || '',
      image: article.image || 'https://placehold.co/400x300/1a1a1a/FFD700?text=No+Image',
      url: article.url,
      source: article.source,
    }))

    // Append to regular stories (don't change featured)
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
    const { data } = await newsApi.getWsbPosts(12)
    
    if (data.status === 'ok' && data.posts) {
      wsbPosts.value = data.posts
      startWsbAutoRotate()  // Start auto-rotation after loading
    }
  } catch (err) {
    console.error('Failed to load WSB posts:', err)
    wsbError.value = 'Unable to load r/wallstreetbets posts.'
  } finally {
    wsbLoading.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  loadNews()
  loadWsbPosts()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  stopWsbAutoRotate()
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
    grid-row: 1;
  }

  .medium:nth-child(3) {
    grid-column: 2;
    grid-row: 2;
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
    grid-row: 1;
  }

  .medium:nth-child(3) {
    grid-column: 3;
    grid-row: 2;
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

/* WSB Cards */
.wsb-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.wsb-card:hover {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 215, 0, 0.3);
  transform: translateY(-2px);
}

.wsb-image-container {
  height: 180px;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  overflow: hidden;
  position: relative;
}

@media (min-width: 768px) {
  .wsb-image-container {
    height: 200px;
  }
}

@media (min-width: 1024px) {
  .wsb-image-container {
    height: 220px;
  }
}
</style>

